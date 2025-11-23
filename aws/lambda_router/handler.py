"""
Router Lambda handler for caching Daily Office prayer PDFs.

This handler implements a caching layer using S3:
1. Checks if a PDF matching the parameters already exists in S3 cache
2. If found, returns the cached PDF
3. If not found, invokes the generator Lambda to create a new PDF
4. Stores the new PDF in S3 cache and returns it

Supports both daily and monthly prayer generation.
Monthly requests use an async pattern to avoid API Gateway timeout.
"""

import json
import base64
import os
import hashlib
import boto3
import calendar
import uuid
from datetime import datetime

# Initialize AWS clients
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')

# Get environment variables
CACHE_BUCKET = os.environ.get('CACHE_BUCKET')
GENERATOR_FUNCTION_NAME = os.environ.get('GENERATOR_FUNCTION_NAME')
CACHE_TTL_DAYS = int(os.environ.get('CACHE_TTL_DAYS', '30'))


def generate_cache_key(prayer_type, date_string, remarkable, is_monthly=False, year=None, month=None, psalm_cycle=None):
    """
    Generate a unique cache key for the prayer parameters.

    Args:
        prayer_type: Type of prayer (morning, evening, midday, compline)
        date_string: Date in YYYY-MM-DD format (for daily prayers)
        remarkable: Boolean flag for page size
        is_monthly: Boolean flag for monthly generation
        year: Year (for monthly prayers)
        month: Month (for monthly prayers)
        psalm_cycle: Psalm cycle (30 or 60) for monthly prayers

    Returns:
        S3 object key for caching
    """
    page_size = 'remarkable' if remarkable else 'letter'

    if is_monthly:
        # Monthly cache key
        if not year:
            year = datetime.now().year
        if not month:
            month = datetime.now().month

        # Include psalm cycle in cache key if specified
        if psalm_cycle:
            cache_key = f"prayers/monthly/{prayer_type}/{year}/{month:02d}/{page_size}/cycle{psalm_cycle}.pdf"
        else:
            cache_key = f"prayers/monthly/{prayer_type}/{year}/{month:02d}/{page_size}/default.pdf"
    else:
        # Daily cache key
        # Use date string or today's date
        if not date_string:
            date_string = datetime.now().strftime('%Y-%m-%d')

        cache_key = f"prayers/daily/{prayer_type}/{date_string}/{page_size}.pdf"

    return cache_key


def check_cache(cache_key):
    """
    Check if a PDF exists in the S3 cache.

    Args:
        cache_key: S3 object key

    Returns:
        PDF data (bytes) if found, None otherwise
    """
    try:
        response = s3_client.get_object(Bucket=CACHE_BUCKET, Key=cache_key)
        print(f"Cache HIT: {cache_key}")
        return response['Body'].read()
    except s3_client.exceptions.NoSuchKey:
        print(f"Cache MISS: {cache_key}")
        return None
    except Exception as e:
        print(f"Error checking cache: {str(e)}")
        return None


def store_in_cache(cache_key, pdf_data):
    """
    Store a PDF in the S3 cache.

    Args:
        cache_key: S3 object key
        pdf_data: PDF binary data (bytes)
    """
    try:
        s3_client.put_object(
            Bucket=CACHE_BUCKET,
            Key=cache_key,
            Body=pdf_data,
            ContentType='application/pdf',
            CacheControl=f'max-age={CACHE_TTL_DAYS * 86400}',  # Cache TTL in seconds
            Metadata={
                'generated-at': datetime.now().isoformat()
            }
        )
        print(f"Stored in cache: {cache_key}")
    except Exception as e:
        print(f"Error storing in cache: {str(e)}")
        # Don't fail the request if caching fails


def invoke_generator(event):
    """
    Invoke the generator Lambda function to create a new PDF.

    Args:
        event: Original API Gateway event with query parameters

    Returns:
        Generator Lambda response
    """
    try:
        print(f"Invoking generator Lambda: {GENERATOR_FUNCTION_NAME}")

        response = lambda_client.invoke(
            FunctionName=GENERATOR_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps(event)
        )

        payload = json.loads(response['Payload'].read())
        return payload

    except Exception as e:
        print(f"Error invoking generator Lambda: {str(e)}")
        raise


def invoke_generator_async(event, job_id):
    """
    Invoke the generator Lambda function asynchronously for monthly PDFs.

    Args:
        event: Original API Gateway event with query parameters
        job_id: Unique job identifier for tracking

    Returns:
        None (async invocation)
    """
    try:
        print(f"Invoking generator Lambda async: {GENERATOR_FUNCTION_NAME}, job_id: {job_id}")

        # Add job_id to the event for the generator to use
        event_with_job = event.copy()
        event_with_job['job_id'] = job_id
        event_with_job['cache_bucket'] = CACHE_BUCKET

        lambda_client.invoke(
            FunctionName=GENERATOR_FUNCTION_NAME,
            InvocationType='Event',  # Async invocation
            Payload=json.dumps(event_with_job)
        )

    except Exception as e:
        print(f"Error invoking generator Lambda async: {str(e)}")
        raise


def create_job(job_id, params):
    """
    Create a new job status entry in S3.

    Args:
        job_id: Unique job identifier
        params: Request parameters for the job
    """
    try:
        status_data = {
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'params': params
        }

        s3_client.put_object(
            Bucket=CACHE_BUCKET,
            Key=f"jobs/{job_id}/status.json",
            Body=json.dumps(status_data),
            ContentType='application/json'
        )
        print(f"Created job: {job_id}")
    except Exception as e:
        print(f"Error creating job: {str(e)}")
        raise


def get_job_status(job_id):
    """
    Get the status of a job from S3.

    Args:
        job_id: Unique job identifier

    Returns:
        dict with status information, or None if job not found
    """
    try:
        # First check if the job exists
        response = s3_client.get_object(
            Bucket=CACHE_BUCKET,
            Key=f"jobs/{job_id}/status.json"
        )
        status_data = json.loads(response['Body'].read())
        return status_data
    except s3_client.exceptions.NoSuchKey:
        return None
    except Exception as e:
        print(f"Error getting job status: {str(e)}")
        return None


def get_job_result(job_id):
    """
    Get the PDF result of a completed job from S3.

    Args:
        job_id: Unique job identifier

    Returns:
        PDF data (bytes) if found, None otherwise
    """
    try:
        response = s3_client.get_object(
            Bucket=CACHE_BUCKET,
            Key=f"jobs/{job_id}/result.pdf"
        )
        return response['Body'].read()
    except s3_client.exceptions.NoSuchKey:
        return None
    except Exception as e:
        print(f"Error getting job result: {str(e)}")
        return None


def handle_job_status_request(event):
    """
    Handle GET /job/{jobId} requests to check job status.

    Args:
        event: API Gateway event

    Returns:
        API Gateway compatible response
    """
    try:
        # Extract job ID from path parameters
        path_params = event.get('pathParameters', {}) or {}
        job_id = path_params.get('jobId')

        if not job_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Missing job ID'})
            }

        # Get job status
        status_data = get_job_status(job_id)

        if not status_data:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Job not found'})
            }

        # If job is completed, return the PDF
        if status_data.get('status') == 'completed':
            pdf_data = get_job_result(job_id)

            if pdf_data:
                pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

                # Generate filename from params
                params = status_data.get('params', {})
                prayer_type = params.get('type', 'prayer')
                year = params.get('year', datetime.now().year)
                month = params.get('month', datetime.now().month)
                month_abbr = calendar.month_abbr[int(month)]
                filename = f"{prayer_type}_prayer_monthly_{month_abbr}_{year}.pdf"

                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/pdf',
                        'Content-Disposition': f'inline; filename="{filename}"',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': pdf_base64,
                    'isBase64Encoded': True
                }
            else:
                # Status says completed but no PDF found
                return {
                    'statusCode': 500,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({'error': 'Job completed but result not found'})
                }

        # If job failed, return error
        if status_data.get('status') == 'failed':
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'status': 'failed',
                    'error': status_data.get('error', 'Unknown error')
                })
            }

        # Job is still pending
        return {
            'statusCode': 202,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'pending',
                'job_id': job_id,
                'message': 'Job is still processing'
            })
        }

    except Exception as e:
        print(f"Error handling job status request: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


def lambda_handler(event, context):
    """
    Router Lambda handler for caching Daily Office prayer PDFs.

    Expected query parameters (from API Gateway):
    - type: Prayer type (morning, evening, midday, or compline) [REQUIRED]
    - date: Date in YYYY-MM-DD format (default: today) [for daily prayers]
    - year: Year (YYYY format) [for monthly prayers]
    - month: Month (1-12) [for monthly prayers]
    - monthly: Boolean flag for monthly generation (default: false)
    - remarkable: Boolean flag for Remarkable 2 tablet format (default: false)
    - psalm_cycle: Psalm cycle (30 or 60) for monthly prayers (default: 60)
    - nocache: Boolean flag to bypass S3 cache (default: false) [optional, for debugging]

    Returns:
        API Gateway compatible response with PDF as base64-encoded binary
    """
    try:
        # Check if this is a job status request (GET /job/{jobId})
        resource = event.get('resource', '')
        if resource == '/job/{jobId}':
            return handle_job_status_request(event)

        # Extract query parameters
        params = event.get('queryStringParameters', {}) or {}

        prayer_type = params.get('type', '').lower()
        date_string = params.get('date')
        remarkable = params.get('remarkable', 'false').lower() in ['true', '1', 'yes']
        bypass_cache = params.get('nocache', 'false').lower() in ['true', '1', 'yes']
        is_monthly = params.get('monthly', 'false').lower() in ['true', '1', 'yes']

        # Validate prayer type
        if prayer_type not in ['morning', 'evening', 'midday', 'compline']:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid or missing prayer type. Must be one of: morning, evening, midday, compline'
                })
            }

        # Extract monthly parameters if applicable
        year = None
        month = None
        psalm_cycle = None

        if is_monthly:
            year_str = params.get('year')
            month_str = params.get('month')
            psalm_cycle_str = params.get('psalm_cycle')

            # Default to current year/month if not provided
            if not year_str:
                year = datetime.now().year
            else:
                try:
                    year = int(year_str)
                except ValueError:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Invalid year format. Expected YYYY'})
                    }

            if not month_str:
                month = datetime.now().month
            else:
                try:
                    month = int(month_str)
                    if not 1 <= month <= 12:
                        raise ValueError()
                except ValueError:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Invalid month. Must be 1-12'})
                    }

            if psalm_cycle_str:
                try:
                    psalm_cycle = int(psalm_cycle_str)
                    if psalm_cycle not in [30, 60]:
                        raise ValueError()
                except ValueError:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Invalid psalm_cycle. Must be 30 or 60'})
                    }

        # Generate cache key
        cache_key = generate_cache_key(
            prayer_type,
            date_string,
            remarkable,
            is_monthly=is_monthly,
            year=year,
            month=month,
            psalm_cycle=psalm_cycle
        )

        # Check cache unless bypass requested
        pdf_data = None
        cache_hit = False

        if not bypass_cache:
            pdf_data = check_cache(cache_key)
            if pdf_data:
                cache_hit = True

        # If not in cache, generate new PDF
        if pdf_data is None:
            # For monthly requests, use async pattern to avoid API Gateway timeout
            if is_monthly:
                # Generate a unique job ID
                job_id = str(uuid.uuid4())

                # Store job parameters for status tracking
                job_params = {
                    'type': prayer_type,
                    'year': year,
                    'month': month,
                    'remarkable': remarkable,
                    'psalm_cycle': psalm_cycle,
                    'cache_key': cache_key
                }
                create_job(job_id, job_params)

                # Invoke generator asynchronously
                invoke_generator_async(event, job_id)

                # Return job ID immediately
                return {
                    'statusCode': 202,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'status': 'pending',
                        'job_id': job_id,
                        'message': 'Monthly PDF generation started. Poll /job/{job_id} for status.'
                    })
                }

            # For daily requests, use synchronous invocation
            generator_response = invoke_generator(event)

            # Check if generator returned an error
            if generator_response.get('statusCode') != 200:
                return generator_response

            # Decode the base64 PDF from generator response
            pdf_base64 = generator_response.get('body', '')
            pdf_data = base64.b64decode(pdf_base64)

            # Store in cache for future requests
            store_in_cache(cache_key, pdf_data)

        # Encode PDF as base64 for API Gateway
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        # Generate filename for Content-Disposition header
        if is_monthly:
            month_abbr = calendar.month_abbr[month]
            filename = f"{prayer_type}_prayer_monthly_{month_abbr}_{year}.pdf"
        else:
            date_str = date_string if date_string else datetime.now().strftime('%Y-%m-%d')
            filename = f"{prayer_type}_prayer_{date_str}.pdf"

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/pdf',
                'Content-Disposition': f'inline; filename="{filename}"',
                'Access-Control-Allow-Origin': '*',
                'X-Cache': 'HIT' if cache_hit else 'MISS'
            },
            'body': pdf_base64,
            'isBase64Encoded': True
        }

    except Exception as e:
        print(f"Error in router: {str(e)}")
        import traceback
        traceback.print_exc()

        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }
