#!/bin/bash
# Build and push the Docker image for the PDF generator Lambda

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

# Step 3: Build the Docker image
echo ""
echo "[3/5] Building Docker image..."
cd "$(dirname "$0")/lambda_generator"

# Copy the dailyoffice package into the build context
echo "Copying dailyoffice package..."
rm -rf dailyoffice
cp -r ../../dailyoffice .

# Build the image
docker build \
    --platform linux/amd64 \
    -t "$ECR_REPOSITORY_NAME:$IMAGE_TAG" \
    -f Dockerfile \
    .

# Clean up copied package
rm -rf dailyoffice

# Step 4: Tag the image for ECR
echo ""
echo "[4/5] Tagging image for ECR..."
ECR_IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPOSITORY_NAME:$IMAGE_TAG"
docker tag "$ECR_REPOSITORY_NAME:$IMAGE_TAG" "$ECR_IMAGE_URI"

# Step 5: Push to ECR
echo ""
echo "[5/5] Pushing image to ECR..."
docker push "$ECR_IMAGE_URI"

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
