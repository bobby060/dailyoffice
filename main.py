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
  # Generate morning prayer for today (as Markdown)
  python main.py --type morning

  # Generate evening prayer for today
  python main.py --type evening

  # Generate midday prayer for a specific date
  python main.py --type midday --date 2025-12-25

  # Generate as PDF using WeasyPrint
  python main.py --type morning --pdf

  # Generate as PDF using LaTeX (requires pdflatex)
  python main.py --type morning --latex

  # Generate PDF with LaTeX and also save the .tex file
  python main.py --type morning --latex --save-tex

  # Generate PDF for Remarkable 2 tablet (6.18x8.24 inches)
  python main.py --type morning --latex --remarkable

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
        choices=['morning', 'evening', 'midday', 'compline'],
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
        help='Generate PDF output using WeasyPrint (requires markdown and weasyprint packages)'
    )

    parser.add_argument(
        '--latex',
        action='store_true',
        help='Generate PDF using LaTeX (requires pdflatex). Default: output PDF only.'
    )

    parser.add_argument(
        '--save-tex',
        action='store_true',
        help='When using --latex, also save the .tex file (in addition to PDF)'
    )

    parser.add_argument(
        '--remarkable',
        action='store_true',
        help='When using --latex, format for Remarkable 2 tablet (6.18x8.24 inches) instead of letter size'
    )

    parser.add_argument(
        '--psalm-cycle',
        type=int,
        choices=[30, 60],
        help='Psalm cycle to use (30 or 60 day). Defaults to 60.',
        metavar='CYCLE'
    )

    parser.add_argument(
        '--print',
        action='store_true',
        help='Print to console instead of saving to file'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.pdf and args.latex:
        print("Error: Cannot specify both --pdf and --latex. Use one or the other.", file=sys.stderr)
        return 1

    if args.save_tex and not args.latex:
        print("Error: --save-tex can only be used with --latex", file=sys.stderr)
        return 1

    if args.remarkable and not args.latex:
        print("Error: --remarkable can only be used with --latex", file=sys.stderr)
        return 1

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
        ext = 'pdf' if (args.pdf or args.latex) else 'md'
        output_file = f"{args.type}_prayer_{date_str}.{ext}"

    # Generate the prayer
    try:
        print(f"Generating {args.type} prayer for {prayer_date}...")

        with PrayerService() as service:
            # Determine which format to generate
            if args.latex:
                # Determine page size
                page_size = "remarkable" if args.remarkable else "letter"

                # Generate LaTeX
                if args.type == 'morning':
                    latex_content = service.generate_morning_prayer_latex(prayer_date=prayer_date, page_size=page_size, psalm_cycle=args.psalm_cycle)
                elif args.type == 'evening':
                    latex_content = service.generate_evening_prayer_latex(prayer_date=prayer_date, page_size=page_size, psalm_cycle=args.psalm_cycle)
                elif args.type == 'midday':
                    latex_content = service.generate_midday_prayer_latex(prayer_date=prayer_date, page_size=page_size, psalm_cycle=args.psalm_cycle)
                elif args.type == 'compline':
                    latex_content = service.generate_compline_latex(prayer_date=prayer_date, page_size=page_size, psalm_cycle=args.psalm_cycle)

                if args.print:
                    # Print LaTeX to console
                    print("\n" + "="*80 + "\n")
                    print(latex_content)
                    print("\n" + "="*80)
                else:
                    # Compile to PDF (and optionally save .tex)
                    tex_filename = None
                    if args.save_tex:
                        # Determine .tex filename
                        if args.output:
                            tex_filename = str(Path(output_file).with_suffix('.tex'))
                        else:
                            date_str = prayer_date.strftime("%Y-%m-%d")
                            tex_filename = f"{args.type}_prayer_{date_str}.tex"

                    service.markdown_generator.compile_latex_to_pdf(
                        latex_content,
                        output_file,
                        save_tex=args.save_tex,
                        tex_filename=tex_filename
                    )
                    print(f"✓ {args.type.capitalize()} prayer compiled to PDF: {output_file}")
                    if args.save_tex:
                        print(f"✓ LaTeX source saved to: {tex_filename}")
            else:
                # Generate markdown based on prayer type
                if args.type == 'morning':
                    markdown_content = service.generate_morning_prayer_markdown(prayer_date=prayer_date, psalm_cycle=args.psalm_cycle)
                elif args.type == 'evening':
                    markdown_content = service.generate_evening_prayer_markdown(prayer_date=prayer_date, psalm_cycle=args.psalm_cycle)
                elif args.type == 'midday':
                    markdown_content = service.generate_midday_prayer_markdown(prayer_date=prayer_date, psalm_cycle=args.psalm_cycle)
                elif args.type == 'compline':
                    markdown_content = service.generate_compline_markdown(prayer_date=prayer_date, psalm_cycle=args.psalm_cycle)

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

    except RuntimeError as e:
        # Handle LaTeX compilation errors
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Error generating {args.type} prayer: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
