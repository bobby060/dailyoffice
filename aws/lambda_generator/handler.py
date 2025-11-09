"""
Lambda handler for generating Daily Office prayer PDFs.

This handler processes API Gateway requests to generate Daily Office prayers
as LaTeX PDFs. It accepts URL parameters similar to the CLI interface.
"""

import json
import base64
import os
import tempfile
from datetime import datetime, date
from pathlib import Path
import sys

# Add the parent directory to the path to import dailyoffice package
sys.path.insert(0, '/var/task')

from dailyoffice import PrayerService


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
    - type: Prayer type (morning, evening, or midday) [REQUIRED]
    - date: Date in YYYY-MM-DD format (default: today)
    - remarkable: Boolean flag for Remarkable 2 tablet format (default: false)

    Returns:
        API Gateway compatible response with PDF as base64-encoded binary
    """
    try:
        # Extract query parameters from API Gateway event
        params = event.get('queryStringParameters', {}) or {}

        # Get prayer type (required)
        prayer_type = params.get('type', '').lower()
        if prayer_type not in ['morning', 'evening', 'midday']:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid or missing prayer type. Must be one of: morning, evening, midday'
                })
            }

        # Get date (optional, defaults to today)
        date_string = params.get('date')
        prayer_date = parse_date(date_string)

        # Get page size (remarkable flag)
        remarkable = params.get('remarkable', 'false').lower() in ['true', '1', 'yes']
        page_size = 'remarkable' if remarkable else 'letter'

        print(f"Generating {prayer_type} prayer for {prayer_date} (page_size={page_size})")

        # Generate LaTeX content using existing service
        with PrayerService() as service:
            if prayer_type == 'morning':
                latex_content = service.generate_morning_prayer_latex(prayer_date, page_size)
            elif prayer_type == 'evening':
                latex_content = service.generate_evening_prayer_latex(prayer_date, page_size)
            else:  # midday
                latex_content = service.generate_midday_prayer_latex(prayer_date, page_size)

            # Compile LaTeX to PDF in temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                output_pdf = Path(temp_dir) / "prayer.pdf"

                # Use the existing compile_latex_to_pdf method
                service.markdown_generator.compile_latex_to_pdf(
                    latex_content,
                    str(output_pdf),
                    save_tex=False
                )

                # Read the PDF file as binary
                with open(output_pdf, 'rb') as pdf_file:
                    pdf_data = pdf_file.read()

        # Encode PDF as base64 for API Gateway
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        # Generate filename for Content-Disposition header
        filename = f"{prayer_type}_prayer_{prayer_date.strftime('%Y-%m-%d')}.pdf"

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
