#!/usr/bin/env python3
"""
Generate Example PDFs

This script generates example PDF files for morning prayer, evening prayer,
and compline using the current date. The output filenames remain consistent
for easy version control.

Usage:
    python generate_examples.py
"""

import sys
from datetime import date
from pathlib import Path

from dailyoffice import PrayerService


def main():
    """Generate example PDFs for all prayer types."""
    print("Generating example PDFs...")
    print("="*80)

    # Use today's date
    prayer_date = date.today()
    print(f"Using date: {prayer_date.strftime('%Y-%m-%d')}")
    print()

    # Define example files with consistent names
    examples = [
        ('morning', 'morning_prayer_example.pdf', 'Morning Prayer'),
        ('evening', 'evening_prayer_example.pdf', 'Evening Prayer'),
        ('compline', 'compline_example.pdf', 'Compline'),
    ]

    try:
        with PrayerService() as service:
            for prayer_type, filename, display_name in examples:
                print(f"Generating {display_name}...", end=' ')

                # Generate LaTeX content
                if prayer_type == 'morning':
                    latex_content = service.generate_morning_prayer_latex(
                        prayer_date=prayer_date,
                        page_size='letter'
                    )
                elif prayer_type == 'evening':
                    latex_content = service.generate_evening_prayer_latex(
                        prayer_date=prayer_date,
                        page_size='letter'
                    )
                elif prayer_type == 'compline':
                    latex_content = service.generate_compline_latex(
                        prayer_date=prayer_date,
                        page_size='letter'
                    )

                # Compile to PDF
                service.latex_generator.compile_latex_to_pdf(
                    latex_content,
                    filename,
                    save_tex=False
                )

                print(f"✓ Saved to {filename}")

        print()
        print("="*80)
        print("All example PDFs generated successfully!")
        return 0

    except RuntimeError as e:
        print(f"\n\nError: {e}", file=sys.stderr)
        print("\nNote: This script requires pdflatex to be installed.", file=sys.stderr)
        print("See the error message above for installation instructions.", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"\n\nError generating examples: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
