#!/bin/bash

# Daily Office Prayer Generator - AWS Stack Destruction
# This script removes all AWS resources created by the deployment
#
# Usage: ./destroy-stack.sh [STACK_NAME]
# If STACK_NAME is not provided, uses default: dailyofficeprayergenerator

set -e

# Use provided stack name or default
STACK_NAME=${1:-dailyofficeprayergenerator}

echo "🧹 Starting cleanup of Daily Office Prayer Generator AWS resources..."
echo "📋 Stack name: $STACK_NAME"

# Delete CloudFormation stack
echo "📋 Deleting CloudFormation stack..."
aws cloudformation delete-stack --stack-name "$STACK_NAME" --region us-east-1

# Wait for stack deletion
echo "⏳ Waiting for stack deletion to complete..."
aws cloudformation wait stack-delete-complete --stack-name "$STACK_NAME" --region us-east-1
echo "✅ CloudFormation stack deleted"

# Delete ECR images
echo "🖼️  Deleting ECR images..."
aws ecr batch-delete-image \
    --repository-name dailyoffice-pdf-generator \
    --image-ids imageTag=latest \
    --region us-east-1 \
    2>/dev/null || echo "⚠️  No images to delete (or repository doesn't exist)"


# Delete local image
echo "🖼️  Deleting local Docker image..."
docker rmi dailyoffice-pdf-generator:latest 2>/dev/null || echo "⚠️  Local image not found or already deleted"

# Delete ECR repository
echo "📦 Deleting ECR repository..."
aws ecr delete-repository \
    --repository-name dailyoffice-pdf-generator \
    --force \
    --region us-east-1 \
    2>/dev/null || echo "⚠️  Repository already deleted or doesn't exist"

# Delete S3 cache bucket (if needed)
echo "🗄️  Deleting S3 cache bucket..."
CACHE_BUCKET="dailyoffice-pdf-cache-$(aws sts get-caller-identity --query Account --output text --region us-east-1)"
aws s3 rb "s3://$CACHE_BUCKET" --force \
    --region us-east-1 \
    2>/dev/null || echo "⚠️  Cache bucket already deleted or doesn't exist"

echo "🎉 Cleanup complete! All Daily Office Prayer Generator AWS resources have been removed."