#!/bin/bash
# Build and push the Docker image for the PDF generator Lambda

BUILD_ONLY=false
if [[ "$1" == "--build-only" ]]; then
    BUILD_ONLY=true
fi

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_NAME="dailyoffice-pdf-generator"
IMAGE_TAG="${IMAGE_TAG:-latest}"

echo "=========================================="
echo "Building Daily Office PDF Generator Image"
echo "=========================================="
echo "AWS Account: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
echo "ECR Repository: $ECR_REPOSITORY_NAME"
echo "Image Tag: $IMAGE_TAG"
echo "=========================================="


if [ "$BUILD_ONLY" = true ]; then

    echo ""
    echo "Build only mode enabled. Skipping ECR repository creation and login."
    echo "You can find the image locally as: $ECR_REPOSITORY_NAME:$IMAGE_TAG"
    echo "To push to ECR later, run this script without the --build-only flag"


else


    # Step 1: Create ECR repository if it doesn't exist
    echo ""
    echo "[1/5] Creating ECR repository..."
    aws ecr describe-repositories \
        --repository-names "$ECR_REPOSITORY_NAME" \
        --region "$AWS_REGION" 2>/dev/null || \
    aws ecr create-repository \
        --repository-name "$ECR_REPOSITORY_NAME" \
        --region "$AWS_REGION" \
        --image-scanning-configuration scanOnPush=true

    # Step 2: Get ECR login credentials
    echo ""
    echo "[2/5] Logging into ECR..."
    aws ecr get-login-password --region "$AWS_REGION" | \
        docker login --username AWS --password-stdin \
        "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

fi

# Step 3: Build the Docker image
echo ""
echo "[3/5] Building Docker image..."
cd "$(dirname "$0")/lambda_generator"

# Copy the dailyoffice package into the build context
echo "Copying dailyoffice package..."
rm -rf dailyoffice
cp -r ../../dailyoffice .

# Build the image
# Note: Use DOCKER_BUILDKIT=0 to ensure Docker manifest v2 schema 2 format
# which is required by AWS Lambda. Lambda does not support OCI manifests.
# Also disable provenance and SBOM attestations which create image indexes
# that Lambda doesn't support (added in Docker BuildKit 0.10+).
DOCKER_BUILDKIT=0 docker build \
    --platform linux/amd64 \
    --provenance=false \
    --sbom=false \
    -t "$ECR_REPOSITORY_NAME:$IMAGE_TAG" \
    -f Dockerfile \
    .

# Clean up copied package
rm -rf dailyoffice

if [ "$BUILD_ONLY" = true ]; then
    echo ""
    echo "Build complete. Skipping push to ECR."
    echo "You can find the image locally as: $ECR_REPOSITORY_NAME:$IMAGE_TAG"
    exit 0
fi

# Step 4: Tag the image for ECR
echo ""
echo "[4/5] Tagging image for ECR..."
ECR_IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG"
docker tag "$ECR_REPOSITORY_NAME:$IMAGE_TAG" "$ECR_IMAGE_URI"

# Step 5: Push to ECR
echo ""
echo "[5/5] Pushing image to ECR..."
# Push with --disable-content-trust to ensure compatibility
docker push "$ECR_IMAGE_URI"

# Verify the manifest type
echo ""
echo "Verifying image manifest type..."
MANIFEST=$(aws ecr batch-get-image \
    --repository-name "$ECR_REPOSITORY_NAME" \
    --image-ids imageTag="$IMAGE_TAG" \
    --region "$AWS_REGION" \
    --query 'images[0].imageManifest' \
    --output text 2>/dev/null || echo "")

if [ -n "$MANIFEST" ]; then
    SCHEMA_VERSION=$(echo "$MANIFEST" | grep -o '"schemaVersion":[0-9]*' | cut -d':' -f2)
    MEDIA_TYPE=$(echo "$MANIFEST" | grep -o '"mediaType":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "Schema Version: $SCHEMA_VERSION"
    echo "Media Type: $MEDIA_TYPE"

    # Check if it's the correct format for Lambda
    if [ "$SCHEMA_VERSION" = "2" ]; then
        echo "✓ Manifest schema version is correct for Lambda"
    else
        echo "⚠ WARNING: Unexpected manifest schema version: $SCHEMA_VERSION"
        echo "  Lambda requires Docker manifest v2 schema 2"
    fi

    # Check media type
    if [[ "$MEDIA_TYPE" == *"docker"* ]] || [[ "$MEDIA_TYPE" == *"vnd.docker"* ]]; then
        echo "✓ Manifest media type appears compatible with Lambda"
    elif [[ "$MEDIA_TYPE" == *"oci"* ]]; then
        echo "⚠ WARNING: OCI manifest detected - Lambda may not support this"
        echo "  Try rebuilding with DOCKER_BUILDKIT=0"
    fi
fi

echo ""
echo "=========================================="
echo "Build and Push Complete!"
echo "=========================================="
echo "Image URI: $ECR_IMAGE_URI"
echo ""
echo "Use this URI when deploying the CloudFormation stack:"
echo "  ImageUri=$ECR_IMAGE_URI"
echo ""
echo "To deploy or update the stack, run:"
echo "  ./deploy-stack.sh $ECR_IMAGE_URI"
echo "=========================================="
