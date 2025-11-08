#!/usr/bin/env python3
"""
Daily Office Morning Prayer Generator - Main CLI

Generate formatted morning prayer documents from The Book of Common Prayer (2019)
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
    parser = argparse.ArgumentParser(
        description="Generate Daily Morning Prayer from The Book of Common Prayer (2019)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate morning prayer for today
  python main.py

  # Generate for a specific date
  python main.py --date 2025-12-25

  # Save to a specific file
  python main.py --output christmas_morning_prayer.md --date 2025-12-25

  # Display to console instead of saving
  python main.py --print
        """
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
        help='Output filename (default: morning_prayer_YYYY-MM-DD.md)',
        metavar='FILE'
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
        output_file = f"morning_prayer_{date_str}.md"

    # Generate the prayer
    try:
        print(f"Generating morning prayer for {prayer_date}...")

        with PrayerService() as service:
            markdown_content = service.generate_morning_prayer_markdown(
                prayer_date=prayer_date
            )

            if args.print:
                # Print to console
                print("\n" + "="*80 + "\n")
                print(markdown_content)
                print("\n" + "="*80)
            else:
                # Save to file
                service.markdown_generator.save_to_file(markdown_content, output_file)
                print(f"✓ Morning prayer saved to: {output_file}")

        return 0

    except Exception as e:
        print(f"Error generating morning prayer: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
