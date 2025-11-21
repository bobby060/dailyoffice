# Architecture Documentation

## System Overview

The Daily Office Prayer Generator AWS deployment is a serverless, scalable system for generating liturgical prayer PDFs on-demand with intelligent caching.

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet / Users                          │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                │ HTTPS (TLS 1.2+)
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                      AWS API Gateway (REST)                      │
│  • Regional endpoint                                             │
│  • CORS enabled                                                  │
│  • Binary media type: application/pdf                            │
│  • Endpoint: /prod/prayer                                        │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                │ AWS_PROXY integration
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│              Router Lambda (Python 3.11)                         │
│  Function: DailyOfficePDFRouter                                  │
│  Memory: 512 MB                                                  │
│  Timeout: 60 seconds                                             │
│  Concurrency: 1000 (default)                                     │
│                                                                  │
│  Workflow:                                                       │
│  1. Parse query parameters (type, date, remarkable)              │
│  2. Generate cache key: prayers/{type}/{date}/{size}.pdf         │
│  3. Check S3 cache for existing PDF                              │
│  4. If cache HIT → Return PDF (avg: 200ms)                       │
│  5. If cache MISS → Invoke Generator Lambda                      │
│  6. Store generated PDF in cache                                 │
│  7. Return PDF to client                                         │
└──────────────────┬────────────────────┬─────────────────────────┘
                   │                    │
                   │ Invoke             │ S3 API
                   │ (RequestResponse)  │ (GetObject, PutObject)
                   │                    │
        ┌──────────▼──────────┐  ┌──────▼──────────────────────────┐
        │  Generator Lambda   │  │  S3 Bucket (Cache)              │
        │  (Container Image)  │  │  Name: dailyoffice-pdf-cache-*  │
        │                     │  │  Encryption: AES256             │
        ├─────────────────────┤  │  Versioning: Enabled            │
        │  Runtime: Python    │  │  Lifecycle: 30 days             │
        │  3.11 + LaTeX       │  │                                 │
        │  Memory: 2048 MB    │  │  Structure:                     │
        │  Timeout: 300s      │  │  /prayers/                      │
        │  Storage: 10 GB     │  │    /morning/                    │
        │                     │  │      /2025-12-25/               │
        │  Workflow:          │  │        /letter.pdf              │
        │  1. Fetch from API  │  │        /remarkable.pdf          │
        │  2. Generate LaTeX  │  │    /evening/                    │
        │  3. Compile PDF     │  │      /2025-12-25/               │
        │  4. Return binary   │  │        /letter.pdf              │
        │  (avg: 15-30s)      │  │    /midday/                     │
        │                     │  │      ...                        │
        └──────────┬──────────┘  └─────────────────────────────────┘
                   │
                   │ HTTPS GET
                   │
        ┌──────────▼──────────────────────────────────┐
        │  Daily Office 2019 API (External)           │
        │  https://api.dailyoffice2019.com/api/v1/    │
        │  • Returns liturgical content as JSON        │
        │  • Endpoints:                                │
        │    - /office/morning_prayer/{date}           │
        │    - /office/evening_prayer/{date}           │
        │    - /office/midday_prayer/{date}            │
        └──────────────────────────────────────────────┘
```

## Data Flow

### Scenario 1: Cache HIT (Optimal Path)

```
User → API Gateway → Router Lambda → S3 Bucket
  ↑                                      │
  └──────────────── PDF ─────────────────┘

Time: ~200-500ms
Cost: ~$0.0001 per request
```

1. User makes GET request to `/prayer?type=morning`
2. API Gateway forwards to Router Lambda
3. Router generates cache key: `prayers/morning/2025-11-09/letter.pdf`
4. Router checks S3 bucket
5. PDF found in cache (HIT)
6. Router returns cached PDF with `X-Cache: HIT` header
7. Client receives PDF

**Performance Characteristics:**
- Latency: 200-500ms
- Lambda execution: 100-200ms
- S3 retrieval: 50-100ms
- No LaTeX compilation needed

### Scenario 2: Cache MISS (First Request)

```
User → API Gateway → Router Lambda → Generator Lambda → Daily Office API
  ↑                      │                    │
  │                      ▼                    ▼
  └────── PDF ─────── S3 Bucket          LaTeX PDF
                                             ↓
                                         Compilation
                                             ↓
                                         Return PDF

Time: ~15-30s
Cost: ~$0.005 per request
```

1. User makes GET request to `/prayer?type=morning&date=2025-12-25`
2. API Gateway forwards to Router Lambda
3. Router generates cache key: `prayers/morning/2025-12-25/letter.pdf`
4. Router checks S3 bucket
5. PDF not found (MISS)
6. Router invokes Generator Lambda with parameters
7. Generator fetches prayer data from Daily Office API
8. Generator creates LaTeX document
9. Generator compiles LaTeX to PDF using `pdflatex`
10. Generator returns PDF to Router
11. Router stores PDF in S3 with metadata
12. Router returns PDF to client with `X-Cache: MISS` header

**Performance Characteristics:**
- Latency: 15-30 seconds
- API fetch: 1-2 seconds
- LaTeX generation: 1-2 seconds
- PDF compilation: 10-20 seconds (2 passes)
- S3 upload: 500ms-1s

## Security Architecture

### Network Security

```
Internet (Public)
     │
     │ TLS 1.2+
     ▼
┌─────────────────────────────────────┐
│  API Gateway (Regional Endpoint)    │
│  • TLS termination                  │
│  • Rate limiting: 10,000 req/s      │
│  • Throttling: 5,000 req/s          │
└────────────┬────────────────────────┘
             │
             │ Private integration
             ▼
┌─────────────────────────────────────┐
│  VPC (Optional - not implemented)   │
│  Lambda functions run in AWS VPC    │
└─────────────────────────────────────┘
```

### IAM Security Model

#### Router Lambda Role
- **Principle**: Least privilege
- **Permissions**:
  - ✅ S3: GetObject, PutObject on cache bucket only
  - ✅ Lambda: InvokeFunction on Generator Lambda only
  - ✅ CloudWatch: Write logs to own log group
  - ❌ No EC2, RDS, or other service access
  - ❌ No IAM modification permissions

#### Generator Lambda Role
- **Principle**: Least privilege
- **Permissions**:
  - ✅ CloudWatch: Write logs to own log group
  - ✅ Network: Outbound HTTPS to Daily Office API
  - ❌ No S3 access (returns PDF to Router)
  - ❌ No other AWS service access

### Data Security

```
┌─────────────────────────────────────┐
│  S3 Bucket Security                 │
├─────────────────────────────────────┤
│  ✅ Encryption at rest: AES256      │
│  ✅ Versioning: Enabled             │
│  ✅ Public access: BLOCKED          │
│  ✅ Access: IAM only                │
│  ✅ Logging: CloudTrail             │
│  ❌ No bucket policies              │
│  ❌ No ACLs                          │
└─────────────────────────────────────┘
```

## Scalability

### Horizontal Scaling

| Component | Concurrency | Scaling |
|-----------|-------------|---------|
| API Gateway | Unlimited | Automatic |
| Router Lambda | 1000 (default) | Automatic to 10,000 |
| Generator Lambda | 100 (recommended) | Automatic, configurable |
| S3 Bucket | Unlimited | Automatic |

### Performance Optimization

1. **Cache Hit Rate**: Target >80% for cost efficiency
2. **Lambda Memory**: Higher memory = more CPU
   - Router: 512 MB sufficient
   - Generator: 2048 MB recommended (faster compilation)
3. **Concurrent Executions**:
   - Reserve capacity for peak times
   - Monitor throttling metrics

### Cost Optimization

#### Caching Strategy
```
Cost per request (cache HIT):  $0.0001
Cost per request (cache MISS): $0.0050

With 80% cache hit rate:
Average cost = (0.8 × $0.0001) + (0.2 × $0.0050)
             = $0.00108 per request
             = $32.40 per 30,000 requests/month
```

#### Recommendations
1. Increase cache TTL for stable content (30-90 days)
2. Monitor cache hit rate via `X-Cache` header
3. Pre-warm cache for common dates (next 7 days)
4. Use Remarkable format only when needed (separate cache)

## Monitoring and Observability

### CloudWatch Metrics

**Router Lambda:**
- `Invocations`: Total requests
- `Duration`: Response time (p50, p99)
- `Errors`: Failed requests
- `Throttles`: Rate limiting events
- **Custom**: Cache hit rate (via logs)

**Generator Lambda:**
- `Invocations`: PDF generations
- `Duration`: Generation time (p50, p99)
- `Errors`: Compilation failures
- `ConcurrentExecutions`: Parallel requests

**S3 Bucket:**
- `NumberOfObjects`: Cached PDFs
- `BucketSizeBytes`: Storage used
- `AllRequests`: Total S3 operations

### CloudWatch Logs

**Log Groups:**
- `/aws/lambda/DailyOfficePDFRouter`
- `/aws/lambda/DailyOfficePDFGenerator`

**Retention:** 14 days (configurable)

**Log Insights Queries:**

```sql
-- Cache hit rate (last 24 hours)
fields @timestamp, @message
| filter @message like /Cache HIT|Cache MISS/
| stats count(*) by @message
```

```sql
-- Average generation time
fields @timestamp, @message, @duration
| filter @type = "REPORT"
| stats avg(@duration), max(@duration), pct(@duration, 95)
```

### CloudWatch Alarms

1. **Generator Errors** (Critical)
   - Metric: `Errors > 5` in 5 minutes
   - Action: Email alert

2. **Router Errors** (Warning)
   - Metric: `Errors > 10` in 5 minutes
   - Action: Email alert

3. **High Latency** (Warning)
   - Metric: `Duration > 30s (p99)` for Generator
   - Action: Email alert

## Disaster Recovery

### Backup Strategy

**S3 Bucket:**
- Versioning enabled: 30-day history
- Cross-region replication: Optional
- Lifecycle rules: Auto-delete after 30 days

**Lambda Functions:**
- Code stored in ECR (Generator)
- Code in CloudFormation (Router)
- Infrastructure as Code: `template.yaml`

### Recovery Procedures

**Complete Stack Failure:**
```bash
# Redeploy entire stack
./build-and-push.sh
./deploy-stack.sh <image-uri>
```

**S3 Bucket Corruption:**
```bash
# Cache will auto-regenerate on demand
# No manual intervention needed
```

**Lambda Function Failure:**
```bash
# Update specific function
aws lambda update-function-code \
  --function-name DailyOfficePDFGenerator \
  --image-uri <new-image-uri>
```

### RTO/RPO

- **RTO** (Recovery Time Objective): 30 minutes
- **RPO** (Recovery Point Objective): 0 (stateless system)

## Future Enhancements

### Potential Improvements

1. **CDN Integration**
   - Add CloudFront for global distribution
   - Reduce latency for international users
   - Additional caching layer

2. **Authentication**
   - API Gateway API keys
   - AWS Cognito user pools
   - Usage quotas per user

3. **Pre-warming**
   - EventBridge scheduled jobs
   - Generate PDFs for next 7 days daily
   - Improve cache hit rate to 95%+

4. **WebSocket Support**
   - Real-time generation status
   - Progress updates during compilation
   - Better UX for slow generations

5. **Multi-Region Deployment**
   - Active-Active in multiple regions
   - Route53 geo-routing
   - Regional S3 buckets

6. **Database Integration**
   - DynamoDB for metadata
   - Track popular prayers
   - Analytics and usage patterns

## Compliance and Standards

- **Data Privacy**: No PII collected
- **Content**: Public domain liturgical texts
- **Encryption**: At rest (S3 AES256) and in transit (TLS)
- **Logging**: CloudWatch Logs (14-day retention)
- **Access Control**: IAM role-based
- **Cost Management**: Budgets and alerts available

## References

- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [API Gateway Best Practices](https://docs.aws.amazon.com/apigateway/latest/developerguide/best-practices.html)
- [S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/best-practices.html)
