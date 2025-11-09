# Quick Start Guide

Deploy the Daily Office Prayer Generator to AWS Lambda in 5 minutes.

## Prerequisites

- AWS CLI configured (`aws configure`)
- Docker installed and running
- Bash shell

## Steps

### 1. Build and Push Docker Image

```bash
cd aws
./build-and-push.sh
```

**Copy the Image URI** from the output (looks like `123456789012.dkr.ecr.us-east-1.amazonaws.com/dailyoffice-pdf-generator:latest`)

### 2. Deploy CloudFormation Stack

```bash
./deploy-stack.sh <paste-image-uri-here>
```

**Copy the API Endpoint** from the output

### 3. Test the API

```bash
curl '<paste-api-endpoint-here>?type=morning' -o test.pdf
open test.pdf  # macOS
# or
xdg-open test.pdf  # Linux
```

## That's It!

Your API is now live. See [README.md](README.md) for more usage examples.

## Sample URLs

Replace `YOUR_API_ENDPOINT` with your actual endpoint:

```bash
# Morning prayer for today
curl 'YOUR_API_ENDPOINT?type=morning' -o morning.pdf

# Evening prayer for Christmas
curl 'YOUR_API_ENDPOINT?type=evening&date=2025-12-25' -o christmas.pdf

# Remarkable tablet format
curl 'YOUR_API_ENDPOINT?type=morning&remarkable=true' -o remarkable.pdf
```

## Clean Up

To remove all AWS resources:

```bash
aws cloudformation delete-stack --stack-name DailyOfficePrayerGenerator
```
