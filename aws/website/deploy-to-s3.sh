#!/bin/bash
# Deploy Daily Office Prayer Generator website to S3

set -e

# Configuration
BUCKET_NAME="${1:-dailyoffice-website}"
AWS_REGION="${AWS_REGION:-us-east-1}"

echo "=========================================="
echo "Deploying Website to S3"
echo "=========================================="
echo "Bucket: $BUCKET_NAME"
echo "Region: $AWS_REGION"
echo "=========================================="

# Step 1: Check if bucket exists, create if not
echo ""
echo "[1/5] Checking S3 bucket..."
if aws s3 ls "s3://$BUCKET_NAME" 2>/dev/null; then
    echo "✓ Bucket exists: $BUCKET_NAME"
else
    echo "Creating bucket: $BUCKET_NAME"
    aws s3 mb "s3://$BUCKET_NAME" --region "$AWS_REGION"
fi

# Step 2: Configure static website hosting
echo ""
echo "[2/5] Configuring static website hosting..."
aws s3 website "s3://$BUCKET_NAME" \
    --index-document index.html \
    --error-document index.html

# Step 3: Set bucket policy for public read
echo ""
echo "[3/5] Setting bucket policy for public access..."
cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
    --bucket "$BUCKET_NAME" \
    --policy file:///tmp/bucket-policy.json

rm /tmp/bucket-policy.json

# Step 4: Disable block public access
echo ""
echo "[4/5] Disabling block public access..."
aws s3api put-public-access-block \
    --bucket "$BUCKET_NAME" \
    --public-access-block-configuration \
        "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Step 5: Upload website files
echo ""
echo "[5/5] Uploading website files..."
cd "$(dirname "$0")"
aws s3 sync . "s3://$BUCKET_NAME" \
    --exclude "*.sh" \
    --exclude "README.md" \
    --exclude ".DS_Store" \
    --cache-control "max-age=300" \
    --content-type "text/html" \
    --exclude "*" \
    --include "*.html"

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Website URL:"
echo "  http://${BUCKET_NAME}.s3-website-${AWS_REGION}.amazonaws.com"
echo ""
echo "To use HTTPS and a custom domain, set up CloudFront:"
echo "  1. Create CloudFront distribution"
echo "  2. Point origin to S3 website endpoint"
echo "  3. Request SSL certificate in ACM"
echo "  4. Add custom domain to CloudFront"
echo ""
echo "To update the website, run:"
echo "  ./deploy-to-s3.sh $BUCKET_NAME"
echo "=========================================="
