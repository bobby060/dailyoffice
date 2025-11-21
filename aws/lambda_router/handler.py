"""
Router Lambda handler for caching Daily Office prayer PDFs.

This handler implements a caching layer using S3:
1. Checks if a PDF matching the parameters already exists in S3 cache
2. If found, returns the cached PDF
3. If not found, invokes the generator Lambda to create a new PDF
4. Stores the new PDF in S3 cache and returns it

Supports both daily and monthly prayer generation.
"""

import json
import base64
import os
import hashlib
import boto3
import calendar
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
