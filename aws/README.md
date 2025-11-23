# Daily Office Prayer Generator - AWS Lambda Deployment

This directory contains all the necessary files to deploy the Daily Office Prayer Generator as an AWS Lambda-based serverless application with S3 caching.

For quick deployment instructions, see [QUICKSTART.md](QUICKSTART.md).

## Architecture Overview

```
┌─────────────┐
│   Client    │
│  (Browser,  │
│  curl, etc) │
└──────┬──────┘
       │
       │ HTTPS GET /prayer?type=morning&date=2025-12-25
       │
       ▼
┌──────────────────┐
│  API Gateway     │
│  (REST API)      │
└────────┬─────────┘
         │
         ▼
┌────────────────────────┐
│  Router Lambda         │
│  (Python 3.11)         │
│                        │
│  1. Generate cache key │
│  2. Check S3 cache     │
└────┬──────────────┬────┘
     │              │
     │ Cache MISS   │ Cache HIT
     │              │
     ▼              ▼
┌─────────────┐   ┌──────────────┐
│ Generator   │   │  S3 Bucket   │
│ Lambda      │   │  (PDF Cache) │
│ (Container) │   └──────────────┘
│             │         ▲
│ - LaTeX     │         │
│ - pdflatex  │         │ Store PDF
│ - Python    │         │
└─────┬───────┘         │
      │                 │
      │ Generate PDF    │
      │                 │
      └─────────────────┘
```

For more architectural details, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Workflow

### Daily Prayers (Synchronous)
1. **Request arrives** at API Gateway with query parameters (type, date, remarkable)
2. **Router Lambda** receives the request and:
   - Generates a cache key based on parameters
   - Checks if a PDF exists in S3 cache
   - If **cache HIT**: Returns the cached PDF directly
   - If **cache MISS**: Invokes the Generator Lambda synchronously
3. **Generator Lambda** generates the PDF and returns it
4. **Router Lambda** stores the PDF in S3 cache and returns it to the client
5. **Client** receives the PDF file

### Monthly Prayers (Asynchronous)
Monthly prayers take 30-120 seconds to generate, which exceeds API Gateway's 29-second timeout. To handle this, monthly requests use an asynchronous pattern:

1. **Request arrives** at API Gateway with `monthly=true`
2. **Router Lambda** checks the S3 cache:
   - If **cache HIT**: Returns the cached PDF directly
   - If **cache MISS**:
     - Creates a job ID and stores job status in S3
     - Invokes Generator Lambda **asynchronously**
     - Returns HTTP 202 with `job_id` immediately
3. **Generator Lambda** (runs in background):
   - Generates the monthly PDF
   - Stores result in S3 at `jobs/{job_id}/result.pdf`
   - Updates job status to `completed` or `failed`
4. **Client polls** `GET /job/{job_id}`:
   - Returns HTTP 202 if still processing
   - Returns the PDF (HTTP 200) when complete
   - Returns HTTP 500 if generation failed

## Components

### 1. Lambda Functions

#### Generator Lambda (`lambda_generator/`)
- **Runtime**: Container image (Python 3.11 + LaTeX)
- **Purpose**: Generates Daily Office prayer PDFs
- **Dependencies**:
  - Python: `requests`
  - System: `texlive`, `pdflatex`
- **Memory**: 2048 MB (configurable)
- **Timeout**: 300 seconds (5 minutes)

#### Router Lambda (`lambda_router/`)
- **Runtime**: Python 3.11
- **Purpose**: Routes requests and manages S3 cache
- **Dependencies**: `boto3`
- **Memory**: 512 MB (configurable)
- **Timeout**: 60 seconds

### 2. Infrastructure (`cloudformation/`)

- **S3 Bucket**: Stores cached PDFs with 30-day lifecycle
- **API Gateway**: REST API with `/prayer` endpoint
- **IAM Roles**: Separate roles for each Lambda with least-privilege permissions
- **CloudWatch Logs**: 14-day retention for monitoring
- **CloudWatch Alarms**: Error rate monitoring for both Lambdas

### 3. Deployment Scripts

- `build-and-push.sh`: Builds Docker image and pushes to ECR
- `deploy-stack.sh`: Deploys CloudFormation stack and updates Lambda code

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
   ```bash
   aws configure
   ```

2. **Docker** installed and running
   ```bash
   docker --version
   ```

3. **AWS Permissions** required:
   - ECR: Create repository, push images
   - Lambda: Create/update functions
   - S3: Create buckets, upload objects
   - CloudFormation: Create/update stacks
   - IAM: Create roles and policies
   - API Gateway: Create REST APIs
   - CloudWatch: Create log groups and alarms

4. **Bash shell** (Linux, macOS, WSL on Windows)

## Deployment Steps

### Step 1: Build and Push Docker Image

```bash
cd aws
chmod +x build-and-push.sh deploy-stack.sh
./build-and-push.sh
```

This script will:
1. Create an ECR repository (if it doesn't exist)
2. Build the Docker image with LaTeX dependencies
3. Push the image to ECR
4. Output the image URI for deployment

**Expected Output:**
```
Image URI: 123456789012.dkr.ecr.us-east-1.amazonaws.com/dailyoffice-pdf-generator:latest
```

### Step 2: Deploy CloudFormation Stack

```bash
./deploy-stack.sh <image-uri>
```

Replace `<image-uri>` with the URI from Step 1.

**Example:**
```bash
./deploy-stack.sh 123456789012.dkr.ecr.us-east-1.amazonaws.com/dailyoffice-pdf-generator:latest
```

Or save stack parameters in `.env` and run:
```bash
source .env
./deploy-stack.sh $IMAGE_URI
```

This script will:
1. Package the router Lambda function
2. Upload it to an S3 deployment bucket
3. Deploy the CloudFormation stack
4. Update the router Lambda code
5. Output the API endpoint

**Expected Output:**
```
API Endpoint: https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/prayer
```
### Step 3: Test the API
You have a few options

1. Use the curl examples below

2. Use the provided python script
```bash
python test_api.py <API_ENDPOINT>
```

## API Usage

### Query Parameters

#### Common Parameters

| Parameter | Required | Type | Description | Example |
|-----------|----------|------|-------------|---------|
| `type` | **Yes** | string | Prayer type: `morning`, `evening`, `midday`, or `compline` | `type=morning` |
| `remarkable` | No | boolean | Format for Remarkable 2 tablet (default: false) | `remarkable=true` |
| `nocache` | No | boolean | Bypass cache and force regeneration (default: false) | `nocache=true` |

#### Daily Prayer Parameters

| Parameter | Required | Type | Description | Example |
|-----------|----------|------|-------------|---------|
| `date` | No | string | Date in YYYY-MM-DD format (default: today) | `date=2025-12-25` |

#### Monthly Prayer Parameters

| Parameter | Required | Type | Description | Example |
|-----------|----------|------|-------------|---------|
| `monthly` | **Yes** | boolean | Enable monthly generation mode | `monthly=true` |
| `year` | No | number | Year (default: current year) | `year=2025` |
| `month` | No | number | Month 1-12 (default: current month) | `month=12` |
| `psalm_cycle` | No | number | Psalm cycle: 30 or 60 (default: 60) | `psalm_cycle=30` |

#### Job Status Endpoint (GET /job/{jobId})

For monthly prayers that aren't cached, the API returns a `job_id` that you poll for completion:

| Response Code | Meaning |
|---------------|---------|
| 200 | Job completed - returns PDF |
| 202 | Job still processing - keep polling |
| 404 | Job not found |
| 500 | Job failed - returns error message |

### Example API Calls

#### Using curl

**Daily Prayers:**
```bash
# Morning prayer for today
curl 'https://your-api.execute-api.us-east-1.amazonaws.com/prod/prayer?type=morning' -o morning_prayer.pdf

# Evening prayer for Christmas Day
curl 'https://your-api.execute-api.us-east-1.amazonaws.com/prod/prayer?type=evening&date=2025-12-25' -o christmas_evening.pdf

# Compline for today
curl 'https://your-api.execute-api.us-east-1.amazonaws.com/prod/prayer?type=compline' -o compline.pdf

# Morning prayer formatted for Remarkable tablet
curl 'https://your-api.execute-api.us-east-1.amazonaws.com/prod/prayer?type=morning&remarkable=true' -o morning_remarkable.pdf
```

**Monthly Prayers (Async Pattern):**
```bash
# Step 1: Start monthly generation (returns job_id if not cached)
JOB_RESPONSE=$(curl -s 'https://your-api.execute-api.us-east-1.amazonaws.com/prod/prayer?type=morning&monthly=true')
echo $JOB_RESPONSE
# {"status": "pending", "job_id": "abc-123-def", "message": "..."}

# Step 2: Poll for completion (repeat until status 200)
JOB_ID="abc-123-def"  # Use job_id from response
curl -s "https://your-api.execute-api.us-east-1.amazonaws.com/prod/job/$JOB_ID" -o monthly.pdf

# If still processing, you'll get:
# {"status": "pending", "job_id": "abc-123-def", "message": "Job is still processing"}

# When complete, you'll get the PDF directly
```

**Simplified Monthly (Python script recommended):**
```bash
# For monthly prayers, use the test script which handles polling automatically
python test_api_endpoint.py https://your-api.execute-api.us-east-1.amazonaws.com/prod/prayer
```

**Monthly with 30-day psalm cycle:**
```bash
curl 'https://your-api.execute-api.us-east-1.amazonaws.com/prod/prayer?type=morning&monthly=true&psalm_cycle=30'
# Returns job_id, then poll /job/{job_id} for result
```

**Advanced:**
```bash
# Bypass cache (force regeneration)
curl 'https://your-api.execute-api.us-east-1.amazonaws.com/prod/prayer?type=morning&nocache=true' -o morning_fresh.pdf
```

#### Using wget

```bash
wget 'https://your-api.execute-api.us-east-1.amazonaws.com/prod/prayer?type=morning' -O morning_prayer.pdf
```

#### Using Python

```python
import requests

response = requests.get(
    'https://your-api.execute-api.us-east-1.amazonaws.com/prod/prayer',
    params={
        'type': 'morning',
        'date': '2025-12-25',
        'remarkable': 'false'
    }
)

with open('prayer.pdf', 'wb') as f:
    f.write(response.content)
```

#### Using JavaScript (Browser)

```javascript
const params = new URLSearchParams({
    type: 'morning',
    date: '2025-12-25',
    remarkable: 'false'
});

fetch(`https://your-api.execute-api.us-east-1.amazonaws.com/prod/prayer?${params}`)
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'morning_prayer.pdf';
        a.click();
    });
```

### Response Headers

The API returns helpful headers:

- `Content-Type: application/pdf`
- `Content-Disposition: inline; filename="morning_prayer_2025-12-25.pdf"`
- `X-Cache: HIT` or `X-Cache: MISS` - Indicates if the PDF was served from cache

## Caching Behavior

### Cache Key Generation

**Daily prayers** are cached based on:
- Prayer type (morning, evening, midday, compline)
- Date (YYYY-MM-DD)
- Page size (letter or remarkable)

**Monthly prayers** are cached based on:
- Prayer type
- Year and month
- Page size
- Psalm cycle (if specified)

**Example S3 cache keys:**
```
# Daily prayers
prayers/daily/morning/2025-12-25/letter.pdf
prayers/daily/evening/2025-12-25/letter.pdf
prayers/daily/compline/2025-12-25/remarkable.pdf

# Monthly prayers
prayers/monthly/morning/2025/12/letter/default.pdf
prayers/monthly/evening/2025/12/remarkable/cycle30.pdf
```

### Cache Lifecycle

- **Default TTL**: 30 days (configurable via CloudFormation parameter)
- **Storage**: S3 Standard with versioning enabled
- **Expiration**: Automatic deletion after TTL via S3 lifecycle policy

### Cache Bypass

To force regeneration of a PDF (e.g., after API data changes):
```bash
curl 'https://your-api.execute-api.us-east-1.amazonaws.com/prod/prayer?type=morning&nocache=true' -o fresh.pdf
```

## Monitoring and Logs

### CloudWatch Logs

- **Generator Lambda**: `/aws/lambda/DailyOfficePDFGenerator`
- **Router Lambda**: `/aws/lambda/DailyOfficePDFRouter`
- **Retention**: 14 days

### CloudWatch Alarms

- **Generator Errors**: Triggers if >5 errors in 5 minutes
- **Router Errors**: Triggers if >10 errors in 5 minutes

### Viewing Logs

```bash
# View recent generator logs
aws logs tail /aws/lambda/DailyOfficePDFGenerator --follow

# View recent router logs
aws logs tail /aws/lambda/DailyOfficePDFRouter --follow
```

## Cost Estimation

Based on moderate usage (1000 requests/day, 50% cache hit rate):

| Service | Usage | Estimated Monthly Cost |
|---------|-------|----------------------|
| Lambda (Router) | 1000 req/day × 512MB × 1s | ~$0.20 |
| Lambda (Generator) | 500 req/day × 2048MB × 30s | ~$15.00 |
| S3 Storage | ~1GB stored | ~$0.02 |
| S3 Requests | 1000 GET/day | ~$0.01 |
| API Gateway | 1000 req/day | ~$1.00 |
| Data Transfer | ~30GB/month | ~$2.70 |
| **Total** | | **~$19/month** |

**Notes:**
- AWS Free Tier includes 1M Lambda requests and 400,000 GB-seconds of compute per month
- Costs scale linearly with usage
- Cache hit rate significantly affects costs (higher cache hit rate = lower costs)

## Customization

### Enable API Gateway Logging

By default, API Gateway logging is **disabled** to avoid requiring account-level IAM role configuration. To enable detailed logging:

```bash
aws cloudformation deploy \
    --stack-name DailyOfficePrayerGenerator \
    --parameter-overrides \
        EnableAPILogging=true
```

This will:
1. Create an IAM role for API Gateway to write to CloudWatch Logs
2. Configure the account-level CloudWatch Logs role
3. Enable INFO-level logging for all API requests
4. Enable data trace logging (full request/response bodies)

**Logs Location**: CloudWatch Logs > Log Groups > `API-Gateway-Execution-Logs_*`

**Note**: Once enabled, API Gateway logs can be verbose and incur CloudWatch Logs storage costs.

### Adjust Lambda Memory/Timeout

Edit CloudFormation parameters in `deploy-stack.sh`:

```bash
aws cloudformation deploy \
    --parameter-overrides \
        GeneratorMemorySize=3008 \
        GeneratorTimeout=600 \
        RouterMemorySize=1024 \
        RouterTimeout=120
```

### Change Cache TTL

```bash
aws cloudformation deploy \
    --parameter-overrides \
        CacheTTLDays=90
```

### Change AWS Region

```bash
export AWS_REGION=us-west-2
./build-and-push.sh
./deploy-stack.sh <image-uri>
```

## Troubleshooting

### Build Issues

**Problem**: Docker build fails with LaTeX errors

**Solution**:
```bash
# Test LaTeX installation in container
docker run --rm public.ecr.aws/lambda/python:3.11 bash -c "yum install -y texlive && pdflatex --version"
```

**Prevention**: The updated `build-and-push.sh` script now automatically disables attestations to ensure Lambda compatibility.

### Deployment Issues

**Problem**: CloudFormation stack creation fails

**Solution**:
```bash
# Check stack events
aws cloudformation describe-stack-events --stack-name DailyOfficePrayerGenerator

# Delete failed stack and retry
aws cloudformation delete-stack --stack-name DailyOfficePrayerGenerator
```

### Generator Lambda Timeout

**Problem**: PDF generation takes too long

**Solutions**:
1. Increase memory (more CPU allocated proportionally)
2. Increase timeout (max 15 minutes for Lambda)
3. Optimize LaTeX compilation (single pass if possible)

### API Gateway 413 Error (Payload Too Large)

**Problem**: Generated PDF exceeds API Gateway limit (10 MB)

**Solution**: Consider using S3 pre-signed URLs instead of direct binary response

## Cleanup

To remove all AWS resources:

```bash
# Clean up entire stack
./destroy-stack.sh
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name DailyOfficePrayerGenerator

# Wait for stack deletion
aws cloudformation wait stack-delete-complete --stack-name DailyOfficePrayerGenerator

# Delete ECR images
aws ecr batch-delete-image \
    --repository-name dailyoffice-pdf-generator \
    --image-ids imageTag=latest

# Delete ECR repository
aws ecr delete-repository \
    --repository-name dailyoffice-pdf-generator \
    --force

# Delete S3 cache bucket (if needed)
CACHE_BUCKET="dailyoffice-pdf-cache-$(aws sts get-caller-identity --query Account --output text)"
aws s3 rb "s3://$CACHE_BUCKET" --force
```

## Security Considerations

1. **API Access**: Currently public (no authentication)
   - Consider adding API keys via API Gateway
   - Or use AWS Cognito for user authentication

2. **CORS**: Enabled for all origins (`*`)
   - Restrict to specific domains in production

3. **S3 Bucket**: Private with encryption at rest
   - Public access blocked by default
   - PDFs only accessible via Lambda

4. **IAM Roles**: Least-privilege permissions
   - Router can only read/write to cache bucket
   - Router can only invoke generator Lambda

5. **DDoS Protection**: Consider adding:
   - API Gateway throttling/quotas
   - AWS WAF for additional protection

## Support

For issues or questions:
- Check CloudWatch Logs for detailed error messages
- Review the main project README: `../README.md`
- Check API response error messages (JSON format)

## License

Same as the main Daily Office Prayer Generator project.
