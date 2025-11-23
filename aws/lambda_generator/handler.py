"""
Lambda handler for generating Daily Office prayer PDFs.

This handler processes API Gateway requests to generate Daily Office prayers
as LaTeX PDFs. It supports both daily and monthly generation, and accepts
URL parameters similar to the CLI interface.
"""

import json
import base64
import os
import tempfile
from datetime import datetime, date
from pathlib import Path
import sys
import calendar
import boto3

# Add the parent directory to the path to import dailyoffice package
sys.path.insert(0, '/var/task')

from dailyoffice import PrayerService, MonthlyPrayerGenerator

# Initialize S3 client for async job results
s3_client = boto3.client('s3')


def update_job_status(cache_bucket, job_id, status, error=None):
    """
    Update job status in S3.

    Args:
        cache_bucket: S3 bucket name
        job_id: Unique job identifier
        status: Job status (pending, completed, failed)
        error: Error message if failed
    """
    try:
        # Get existing status to preserve params
        try:
            response = s3_client.get_object(
                Bucket=cache_bucket,
                Key=f"jobs/{job_id}/status.json"
            )
            status_data = json.loads(response['Body'].read())
        except Exception:
            status_data = {}

        status_data['status'] = status
        status_data['updated_at'] = datetime.now().isoformat()
        if error:
            status_data['error'] = error

        s3_client.put_object(
            Bucket=cache_bucket,
            Key=f"jobs/{job_id}/status.json",
            Body=json.dumps(status_data),
            ContentType='application/json'
        )
        print(f"Updated job {job_id} status to: {status}")
    except Exception as e:
        print(f"Error updating job status: {str(e)}")


def store_job_result(cache_bucket, job_id, pdf_data, cache_key=None):
    """
    Store job result PDF in S3.

    Args:
        cache_bucket: S3 bucket name
        job_id: Unique job identifier
        pdf_data: PDF binary data
        cache_key: Optional cache key to also store the PDF in cache
    """
    try:
        # Store in job results
        s3_client.put_object(
            Bucket=cache_bucket,
            Key=f"jobs/{job_id}/result.pdf",
            Body=pdf_data,
            ContentType='application/pdf'
        )
        print(f"Stored job result: {job_id}")

        # Also store in cache for future requests
        if cache_key:
            s3_client.put_object(
                Bucket=cache_bucket,
                Key=cache_key,
                Body=pdf_data,
                ContentType='application/pdf',
                Metadata={
                    'generated-at': datetime.now().isoformat()
                }
            )
            print(f"Stored in cache: {cache_key}")
    except Exception as e:
        print(f"Error storing job result: {str(e)}")


def parse_date(date_string):
    """
    Parse date string in YYYY-MM-DD format.

    Args:
        date_string: Date string in YYYY-MM-DD format or None for today

    Returns:
        date object
    """
    if not date_string:
        return date.today()

    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Invalid date format: {date_string}. Expected YYYY-MM-DD")


def lambda_handler(event, context):
    """
    Lambda handler for generating Daily Office prayer PDFs.

    Expected query parameters (from API Gateway):
    - type: Prayer type (morning, evening, midday, or compline) [REQUIRED]
    - date: Date in YYYY-MM-DD format (default: today) [for daily prayers]
    - year: Year (YYYY format) [for monthly prayers]
    - month: Month (1-12) [for monthly prayers]
    - monthly: Boolean flag for monthly generation (default: false)
    - remarkable: Boolean flag for Remarkable 2 tablet format (default: false)
    - psalm_cycle: Psalm cycle (30 or 60) for monthly prayers (default: 60)

    Returns:
        API Gateway compatible response with PDF as base64-encoded binary
    """
    # Check if this is an async job invocation
    job_id = event.get('job_id')
    cache_bucket = event.get('cache_bucket')
    is_async_job = job_id is not None

    try:
        # Extract query parameters from API Gateway event
        params = event.get('queryStringParameters', {}) or {}

        # Get prayer type (required)
        prayer_type = params.get('type', '').lower()
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

        # Check if monthly generation is requested
        is_monthly = params.get('monthly', 'false').lower() in ['true', '1', 'yes']

        # Get page size (remarkable flag)
        remarkable = params.get('remarkable', 'false').lower() in ['true', '1', 'yes']
        page_size = 'remarkable' if remarkable else 'letter'

        if is_monthly:
            # Monthly generation
            year = params.get('year')
            month = params.get('month')

            # Default to current year/month if not provided
            if not year:
                year = date.today().year
            else:
                try:
                    year = int(year)
                except ValueError:
                    return {
                        'statusCode': 400,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        },
                        'body': json.dumps({'error': 'Invalid year format. Expected YYYY'})
                    }

            if not month:
                month = date.today().month
            else:
                try:
                    month = int(month)
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

            # Get optional psalm cycle
            psalm_cycle = params.get('psalm_cycle')
            if psalm_cycle:
                try:
                    psalm_cycle = int(psalm_cycle)
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

            month_name = calendar.month_name[month]
            print(f"Generating monthly {prayer_type} prayers for {month_name} {year} (page_size={page_size})")

            # Generate monthly PDF
            with tempfile.TemporaryDirectory() as temp_dir:
                output_pdf = Path(temp_dir) / "prayer.pdf"

                # Disable local file caching in Lambda environment
                with MonthlyPrayerGenerator(enable_cache=False) as generator:
                    generator.compile_to_pdf(
                        year=year,
                        month=month,
                        output_pdf=str(output_pdf),
                        prayer_type=prayer_type,
                        page_size=page_size,
                        psalm_cycle=psalm_cycle,
                        save_tex=False
                    )

                # Read the PDF file as binary
                with open(output_pdf, 'rb') as pdf_file:
                    pdf_data = pdf_file.read()

            # Generate filename for Content-Disposition header
            month_abbr = calendar.month_abbr[month]
            filename = f"{prayer_type}_prayer_monthly_{month_abbr}_{year}.pdf"

            # If this is an async job, store results in S3
            if is_async_job:
                # Get cache key from job params
                cache_key = None
                try:
                    response = s3_client.get_object(
                        Bucket=cache_bucket,
                        Key=f"jobs/{job_id}/status.json"
                    )
                    job_status = json.loads(response['Body'].read())
                    cache_key = job_status.get('params', {}).get('cache_key')
                except Exception:
                    pass

                # Store result and update status
                store_job_result(cache_bucket, job_id, pdf_data, cache_key)
                update_job_status(cache_bucket, job_id, 'completed')

                # Return success (no response body needed for async)
                return {
                    'statusCode': 200,
                    'body': json.dumps({'status': 'completed', 'job_id': job_id})
                }

        else:
            # Daily generation (existing code)
            # Get date (optional, defaults to today)
            date_string = params.get('date')
            prayer_date = parse_date(date_string)

            print(f"Generating {prayer_type} prayer for {prayer_date} (page_size={page_size})")

            # Generate LaTeX content using existing service
            # Disable local file caching in Lambda environment
            with PrayerService(enable_cache=False) as service:
                if prayer_type == 'morning':
                    latex_content = service.generate_morning_prayer_latex(prayer_date, page_size)
                elif prayer_type == 'evening':
                    latex_content = service.generate_evening_prayer_latex(prayer_date, page_size)
                elif prayer_type == 'midday':
                    latex_content = service.generate_midday_prayer_latex(prayer_date, page_size)
                else:  # compline
                    latex_content = service.generate_compline_latex(prayer_date, page_size)

                # Compile LaTeX to PDF in temporary directory
                with tempfile.TemporaryDirectory() as temp_dir:
                    output_pdf = Path(temp_dir) / "prayer.pdf"

                    # Use the existing compile_latex_to_pdf method
                    service.latex_generator.compile_latex_to_pdf(
                        latex_content,
                        str(output_pdf),
                        save_tex=False
                    )

                    # Read the PDF file as binary
                    with open(output_pdf, 'rb') as pdf_file:
                        pdf_data = pdf_file.read()

            # Generate filename for Content-Disposition header
            filename = f"{prayer_type}_prayer_{prayer_date.strftime('%Y-%m-%d')}.pdf"

        # Encode PDF as base64 for API Gateway
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

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

    except ValueError as e:
        print(f"Validation error: {str(e)}")
        # Update job status if async
        if is_async_job:
            update_job_status(cache_bucket, job_id, 'failed', str(e))
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

    except Exception as e:
        print(f"Error generating prayer: {str(e)}")
        import traceback
        traceback.print_exc()

        # Update job status if async
        if is_async_job:
            update_job_status(cache_bucket, job_id, 'failed', str(e))

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
