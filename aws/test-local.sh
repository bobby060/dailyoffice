#!/bin/bash
# Test the Lambda handlers locally (without deploying to AWS)

set -e

echo "=========================================="
echo "Testing Lambda Handlers Locally"
echo "=========================================="

# Test the generator Lambda handler
echo ""
echo "[1/2] Testing Generator Lambda..."
echo "Creating test event..."

cat > /tmp/test_event.json <<EOF
{
  "queryStringParameters": {
    "type": "morning",
    "date": "2025-12-25",
    "remarkable": "false"
  }
}
EOF

echo "Running handler locally..."
cd lambda_generator

# Add parent directory to Python path
export PYTHONPATH="../..:$PYTHONPATH"

# Run the handler
python3 -c "
import sys
import json
sys.path.insert(0, '../..')
from handler import lambda_handler

with open('/tmp/test_event.json', 'r') as f:
    event = json.load(f)

response = lambda_handler(event, None)
print('Status Code:', response['statusCode'])
print('Content-Type:', response['headers']['Content-Type'])
print('Is Base64 Encoded:', response.get('isBase64Encoded', False))

if response['statusCode'] == 200:
    import base64
    pdf_data = base64.b64decode(response['body'])
    with open('/tmp/test_output.pdf', 'wb') as f:
        f.write(pdf_data)
    print('PDF saved to /tmp/test_output.pdf')
    print('PDF size:', len(pdf_data), 'bytes')
    print('✅ Generator Lambda test PASSED')
else:
    print('❌ Generator Lambda test FAILED')
    print('Error:', response.get('body'))
    sys.exit(1)
"

cd ..

# Test the router Lambda (mock S3 and Lambda invocation)
echo ""
echo "[2/2] Testing Router Lambda (syntax check)..."
cd lambda_router

python3 -c "
import handler as router_handler
print('✅ Router Lambda imports successfully')
print('Available functions:', dir(router_handler))
print('Lambda handler:', router_handler.lambda_handler)
"

cd ..

echo ""
echo "=========================================="
echo "Local Tests Complete!"
echo "=========================================="
echo "Generated PDF: /tmp/test_output.pdf"
echo ""
echo "To view the PDF:"
echo "  open /tmp/test_output.pdf  # macOS"
echo "  xdg-open /tmp/test_output.pdf  # Linux"
echo ""
echo "Next step: Deploy to AWS"
echo "  ./build-and-push.sh"
echo "=========================================="
