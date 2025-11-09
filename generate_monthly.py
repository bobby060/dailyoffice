#!/usr/bin/env python3
"""
Monthly Prayer Generator - CLI Tool

Generate formatted monthly prayer documents from The Book of Common Prayer (2019)
using the Daily Office 2019 API. Creates a combined PDF with all prayers for a month,
including a title page, index with hyperlinks, and navigation.
"""

import argparse
import sys
from datetime import date
from pathlib import Path
import calendar

from dailyoffice import MonthlyPrayerGenerator


def parse_month(month_str: str) -> int:
    """
    Parse a month string (1-12 or month name).

    Args:
        month_str: Month to parse (1-12 or name like "January")

    Returns:
        Month number (1-12)

    Raises:
        ValueError: If the month string is invalid
    """
    # Try parsing as a number first
    try:
        month_num = int(month_str)
        if 1 <= month_num <= 12:
            return month_num
        raise ValueError(f"Month number must be 1-12, got {month_num}")
    except ValueError:
        pass

    # Try parsing as month name
    month_str_lower = month_str.lower()
    for i, month_name in enumerate(calendar.month_name):
        if month_name.lower().startswith(month_str_lower):
            return i

    for i, month_abbr in enumerate(calendar.month_abbr):
        if month_abbr.lower() == month_str_lower:
            return i

    raise ValueError(f"Invalid month: '{month_str}'. Use 1-12 or month name.")


def main():
    """Main CLI entry point."""
    # If no arguments provided, show help and exit
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    parser = argparse.ArgumentParser(
        description="Generate monthly Daily Office prayer documents from The Book of Common Prayer (2019)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate morning prayers for current month
  python generate_monthly.py --type morning

  # Generate evening prayers for December 2025
  python generate_monthly.py --type evening --year 2025 --month 12

  # Generate with month name
  python generate_monthly.py --type morning --year 2025 --month December

  # Generate for Remarkable 2 tablet
  python generate_monthly.py --type morning --month January --remarkable

  # Save the LaTeX source file too
  python generate_monthly.py --type morning --save-tex

  # Custom output filename
  python generate_monthly.py --type morning --output my_prayers.pdf

For more information, visit: https://www.dailyoffice2019.com/
        """
    )

    parser.add_argument(
        '--type', '-t',
        type=str,
        choices=['morning', 'evening', 'midday', 'compline'],
        required=True,
        help='Type of prayer to generate'
    )

    parser.add_argument(
        '--year', '-y',
        type=int,
        help='Year for the prayers (default: current year)',
        metavar='YYYY'
    )

    parser.add_argument(
        '--month', '-m',
        type=str,
        help='Month for the prayers - use 1-12 or month name (default: current month)',
        metavar='MONTH'
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output PDF filename (default: <type>_prayers_YYYY-MM.pdf)',
        metavar='FILE'
    )

    parser.add_argument(
        '--save-tex',
        action='store_true',
        help='Also save the LaTeX source file (in addition to PDF)'
    )

    parser.add_argument(
        '--remarkable',
        action='store_true',
        help='Format for Remarkable 2 tablet (6.18x8.24 inches) instead of letter size'
    )

    parser.add_argument(
        '--psalm-cycle',
        type=int,
        choices=[30, 60],
        help='Psalm cycle to use (30 or 60 day). Defaults to 60.',
        metavar='CYCLE'
    )

    args = parser.parse_args()

    # Determine year and month
    today = date.today()
    year = args.year if args.year else today.year

    try:
        if args.month:
            month = parse_month(args.month)
        else:
            month = today.month
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Validate year
    if year < 1900 or year > 2100:
        print(f"Error: Year must be between 1900 and 2100, got {year}", file=sys.stderr)
        return 1

    # Determine output filename
    if args.output:
        output_file = args.output
    else:
        month_str = f"{year}-{month:02d}"
        output_file = f"{args.type}_prayers_{month_str}.pdf"

    # Determine page size
    page_size = "remarkable" if args.remarkable else "letter"

    # Generate the monthly prayers
    try:
        month_name = calendar.month_name[month]
        print(f"Generating monthly {args.type} prayers for {month_name} {year}...")
        print(f"Page size: {page_size}")
        print()

        with MonthlyPrayerGenerator() as generator:
            # Determine .tex filename if saving
            tex_filename = None
            if args.save_tex:
                if args.output:
                    tex_filename = str(Path(output_file).with_suffix('.tex'))
                else:
                    month_str = f"{year}-{month:02d}"
                    tex_filename = f"{args.type}_prayers_{month_str}.tex"

            # Generate and compile
            generator.compile_to_pdf(
                year=year,
                month=month,
                output_pdf=output_file,
                prayer_type=args.type,
                page_size=page_size,
                psalm_cycle=args.psalm_cycle,
                save_tex=args.save_tex,
                tex_filename=tex_filename
            )

            print()
            print(f"✓ Monthly {args.type} prayers compiled to PDF: {output_file}")
            if args.save_tex:
                print(f"✓ LaTeX source saved to: {tex_filename}")

        return 0

    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except RuntimeError as e:
        # Handle LaTeX compilation errors
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Error generating monthly prayers: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
