#!/usr/bin/env python3
"""
Daily Office Prayer Generator - Main CLI

Generate formatted prayer documents from The Book of Common Prayer (2019)
using the Daily Office 2019 API.
"""

import argparse
import sys
from datetime import datetime, date
from pathlib import Path

from dailyoffice import PrayerService


def parse_date(date_str: str) -> date:
    """
    Parse a date string in YYYY-MM-DD format.

    Args:
        date_str: Date string to parse

    Returns:
        Parsed date object

    Raises:
        ValueError: If the date string is invalid
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"Invalid date format '{date_str}'. Use YYYY-MM-DD format.") from e


def main():
    """Main CLI entry point."""
    # If no arguments provided, show help and exit
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    parser = argparse.ArgumentParser(
        description="Generate Daily Office prayers from The Book of Common Prayer (2019)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate morning prayer for today
  python main.py --type morning

  # Generate evening prayer for today
  python main.py --type evening

  # Generate midday prayer for a specific date
  python main.py --type midday --date 2025-12-25

  # Generate as PDF
  python main.py --type morning --pdf --output morning_prayer.pdf

  # Save to a specific file
  python main.py --type morning --output christmas_morning_prayer.md --date 2025-12-25

  # Display to console instead of saving
  python main.py --type morning --print

  # Get help
  python main.py --help

For more information, visit: https://www.dailyoffice2019.com/
        """
    )

    parser.add_argument(
        '--type', '-t',
        type=str,
        choices=['morning', 'evening', 'midday'],
        required=True,
        help='Type of prayer to generate'
    )

    parser.add_argument(
        '--date', '-d',
        type=str,
        help='Date for the prayer in YYYY-MM-DD format (default: today)',
        metavar='YYYY-MM-DD'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output filename (default: <type>_prayer_YYYY-MM-DD.md or .pdf)',
        metavar='FILE'
    )

    parser.add_argument(
        '--pdf',
        action='store_true',
        help='Generate PDF output instead of Markdown (requires markdown and weasyprint packages)'
    )

    parser.add_argument(
        '--print',
        action='store_true',
        help='Print to console instead of saving to file'
    )

    args = parser.parse_args()

    # Parse the date
    try:
        if args.date:
            prayer_date = parse_date(args.date)
        else:
            prayer_date = date.today()
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        date_str = prayer_date.strftime("%Y-%m-%d")
        ext = 'pdf' if args.pdf else 'md'
        output_file = f"{args.type}_prayer_{date_str}.{ext}"

    # Generate the prayer
    try:
        print(f"Generating {args.type} prayer for {prayer_date}...")

        with PrayerService() as service:
            # Generate markdown based on prayer type
            if args.type == 'morning':
                markdown_content = service.generate_morning_prayer_markdown(prayer_date=prayer_date)
            elif args.type == 'evening':
                markdown_content = service.generate_evening_prayer_markdown(prayer_date=prayer_date)
            elif args.type == 'midday':
                markdown_content = service.generate_midday_prayer_markdown(prayer_date=prayer_date)

            if args.print:
                # Print to console
                print("\n" + "="*80 + "\n")
                print(markdown_content)
                print("\n" + "="*80)
            else:
                # Save to file (PDF or Markdown)
                if args.pdf:
                    service.markdown_generator.save_to_pdf(markdown_content, output_file)
                    print(f"✓ {args.type.capitalize()} prayer saved as PDF to: {output_file}")
                else:
                    service.markdown_generator.save_to_file(markdown_content, output_file)
                    print(f"✓ {args.type.capitalize()} prayer saved to: {output_file}")

        return 0

    except ImportError as e:
        if 'markdown' in str(e) or 'weasyprint' in str(e):
            print(f"Error: PDF generation requires additional packages.", file=sys.stderr)
            print(f"Install them with: pip install markdown weasyprint", file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Error generating {args.type} prayer: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
