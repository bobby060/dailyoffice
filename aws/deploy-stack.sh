#!/bin/bash
# Deploy the Daily Office CloudFormation stack

set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
STACK_NAME="${STACK_NAME:-DailyOfficePrayerGenerator}"
IMAGE_URI="$1"

if [ -z "$IMAGE_URI" ]; then
    echo "Error: Image URI is required"
    echo "Usage: $0 <image-uri>"
    echo ""
    echo "Example:"
    echo "  $0 123456789012.dkr.ecr.us-east-1.amazonaws.com/dailyoffice-pdf-generator:latest"
    echo ""
    echo "To build and push the image first, run:"
    echo "  ./build-and-push.sh"
    exit 1
fi

echo "=========================================="
echo "Deploying Daily Office CloudFormation Stack"
echo "=========================================="
echo "Stack Name: $STACK_NAME"
echo "AWS Region: $AWS_REGION"
echo "Image URI: $IMAGE_URI"
echo "=========================================="

# Package the router Lambda function
echo ""
echo "[1/3] Packaging router Lambda function..."
cd "$(dirname "$0")/lambda_router"
rm -f lambda_router.zip
zip -q lambda_router.zip handler.py
cd ..

# Upload router Lambda to S3 (CloudFormation needs it)
# First check if deployment bucket exists
DEPLOYMENT_BUCKET="${STACK_NAME}-deployment-$(aws sts get-caller-identity --query Account --output text)"
echo ""
echo "[2/3] Uploading router Lambda to S3..."
aws s3 ls "s3://$DEPLOYMENT_BUCKET" 2>/dev/null || \
    aws s3 mb "s3://$DEPLOYMENT_BUCKET" --region "$AWS_REGION"

aws s3 cp lambda_router/lambda_router.zip "s3://$DEPLOYMENT_BUCKET/lambda_router.zip"

# Update the CloudFormation template to use the S3 code
TEMPLATE_FILE="cloudformation/template.yaml"
TEMP_TEMPLATE_FILE="/tmp/dailyoffice-template-updated.yaml"

# Read the template and update the router Lambda code
cat "$TEMPLATE_FILE" | \
    sed '/Code:/,/}/c\      Code:\n        S3Bucket: '"$DEPLOYMENT_BUCKET"'\n        S3Key: lambda_router.zip' \
    > "$TEMP_TEMPLATE_FILE"

# Deploy the stack
echo ""
echo "[3/3] Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file "$TEMPLATE_FILE" \
    --stack-name "$STACK_NAME" \
    --parameter-overrides \
        ImageUri="$IMAGE_URI" \
        CacheTTLDays=30 \
        GeneratorMemorySize=2048 \
        GeneratorTimeout=300 \
        RouterMemorySize=512 \
        RouterTimeout=60 \
    --capabilities CAPABILITY_NAMED_IAM \
    --region "$AWS_REGION" \
    --no-fail-on-empty-changeset

# Update the router Lambda function code
echo ""
echo "Updating router Lambda function code..."
ROUTER_FUNCTION_NAME=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`RouterFunctionArn`].OutputValue' \
    --output text | awk -F: '{print $NF}')

cd lambda_router
zip -q -r lambda_router.zip handler.py
aws lambda update-function-code \
    --function-name "$ROUTER_FUNCTION_NAME" \
    --zip-file fileb://lambda_router.zip \
    --region "$AWS_REGION" > /dev/null
rm lambda_router.zip
cd ..

# Get the API endpoint
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="

API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`APIEndpoint`].OutputValue' \
    --output text)

CACHE_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$AWS_REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`CacheBucketName`].OutputValue' \
    --output text)

echo "API Endpoint: $API_ENDPOINT"
echo "Cache Bucket: $CACHE_BUCKET"
echo ""
echo "Example API calls:"
echo "  # Morning prayer for today"
echo "  curl '$API_ENDPOINT?type=morning' -o morning_prayer.pdf"
echo ""
echo "  # Evening prayer for Christmas"
echo "  curl '$API_ENDPOINT?type=evening&date=2025-12-25' -o christmas_evening.pdf"
echo ""
echo "  # Morning prayer for Remarkable tablet"
echo "  curl '$API_ENDPOINT?type=morning&remarkable=true' -o morning_remarkable.pdf"
echo ""
echo "  # Morning prayer with 30-day psalter cycle"
echo "  curl '$API_ENDPOINT?type=morning&psalter=30' -o morning_30day.pdf"
echo "=========================================="
