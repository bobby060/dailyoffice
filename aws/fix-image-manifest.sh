#!/bin/bash
# Fix Docker image manifest format for AWS Lambda compatibility
#
# This script checks if an image in ECR has manifest issues and provides
# guidance on how to fix them. The solution is to rebuild the image with
# DOCKER_BUILDKIT=0 to ensure Docker manifest v2 schema 2 format.

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY_NAME="dailyoffice-pdf-generator"
IMAGE_TAG="${1:-latest}"

echo "=========================================="
echo "Image Manifest Checker for Lambda"
echo "=========================================="
echo "AWS Account: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"
echo "ECR Repository: $ECR_REPOSITORY_NAME"
echo "Image Tag: $IMAGE_TAG"
echo "=========================================="

# Check the manifest
echo ""
echo "Checking manifest format..."
MANIFEST=$(aws ecr batch-get-image \
    --repository-name "$ECR_REPOSITORY_NAME" \
    --image-ids imageTag="$IMAGE_TAG" \
    --region "$AWS_REGION" \
    --query 'images[0].imageManifest' \
    --output text 2>/dev/null || echo "")

if [ -z "$MANIFEST" ]; then
    echo "✗ Error: Could not retrieve image manifest"
    echo "  Make sure the image exists in ECR"
    exit 1
fi

SCHEMA_VERSION=$(echo "$MANIFEST" | grep -o '"schemaVersion":[0-9]*' | cut -d':' -f2)
MEDIA_TYPE=$(echo "$MANIFEST" | grep -o '"mediaType":"[^"]*"' | head -1 | cut -d'"' -f4)

echo ""
echo "Current Manifest Details:"
echo "  Schema Version: $SCHEMA_VERSION"
echo "  Media Type: $MEDIA_TYPE"
echo ""

# Check for issues
HAS_ISSUES=false

if [ "$SCHEMA_VERSION" != "2" ]; then
    echo "✗ Issue: Schema version $SCHEMA_VERSION is not compatible with Lambda"
    echo "  Lambda requires Docker manifest v2 schema 2"
    HAS_ISSUES=true
fi

if [[ "$MEDIA_TYPE" == *"oci"* ]]; then
    echo "✗ Issue: OCI manifest format detected"
    echo "  Lambda requires Docker v2 manifest format"
    HAS_ISSUES=true
elif [[ "$MEDIA_TYPE" == *"list"* ]] || [[ "$MEDIA_TYPE" == *"index"* ]]; then
    echo "✗ Issue: Multi-architecture manifest detected"
    echo "  Lambda requires a single-architecture manifest"
    HAS_ISSUES=true
fi

if [ "$HAS_ISSUES" = false ]; then
    echo "✓ Manifest format appears compatible with Lambda"
    echo ""
    exit 0
fi

# Provide fix instructions
echo ""
echo "=========================================="
echo "HOW TO FIX"
echo "=========================================="
echo ""
echo "The image needs to be rebuilt with the correct manifest format."
echo "Run the following command:"
echo ""
echo "  ./build-and-push.sh"
echo ""
echo "This will rebuild the image using DOCKER_BUILDKIT=0 to ensure"
echo "the correct Docker manifest v2 schema 2 format."
echo ""
echo "If you've already built the image, delete it and rebuild:"
echo ""
echo "  # Delete the existing image"
echo "  aws ecr batch-delete-image \\"
echo "    --repository-name $ECR_REPOSITORY_NAME \\"
echo "    --image-ids imageTag=$IMAGE_TAG \\"
echo "    --region $AWS_REGION"
echo ""
echo "  # Rebuild and push"
echo "  ./build-and-push.sh"
echo ""
echo "=========================================="
