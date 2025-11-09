# Monthly Prayer Generator

Generate a complete month of Daily Office prayers in a single PDF with navigation.

## Features

- **Complete Monthly Coverage**: Generates prayers for every day of a specified month
- **Professional Layout**: Includes title page and hyperlinked index
- **Smart Navigation**:
  - Clickable index linking to each day
  - Header links to jump back to index
  - Navigation bar at top of each day
  - Current date shown in header
- **Multiple Page Sizes**: Support for standard letter and Remarkable 2 tablet
- **All Prayer Types**: Morning, Evening, Midday, and Compline prayers

## Quick Start

### Command Line Usage

```bash
# Generate morning prayers for current month
python generate_monthly.py --type morning

# Generate evening prayers for a specific month
python generate_monthly.py --type evening --year 2025 --month December

# Generate for Remarkable 2 tablet
python generate_monthly.py --type morning --remarkable

# Save LaTeX source file
python generate_monthly.py --type morning --save-tex
```

### Python API Usage

```python
from dailyoffice import MonthlyPrayerGenerator

# Generate monthly prayers
with MonthlyPrayerGenerator() as generator:
    generator.compile_to_pdf(
        year=2025,
        month=12,
        output_pdf='december_morning_prayers.pdf',
        prayer_type='morning',
        page_size='letter'  # or 'remarkable'
    )
```

## Command Line Options

- `--type, -t`: Prayer type (morning, evening, midday, compline) - **Required**
- `--year, -y`: Year (default: current year)
- `--month, -m`: Month as number (1-12) or name (default: current month)
- `--output, -o`: Output PDF filename
- `--save-tex`: Save the LaTeX source file
- `--remarkable`: Format for Remarkable 2 tablet (6.18x8.24 inches)

## Examples

### Generate Different Prayer Types

```bash
# Morning prayers for January 2025
python generate_monthly.py --type morning --year 2025 --month January

# Evening prayers for December
python generate_monthly.py --type evening --month 12

# Compline for current month
python generate_monthly.py --type compline
```

### Custom Output

```bash
# Custom filename
python generate_monthly.py --type morning --output my_prayers.pdf

# Save both PDF and LaTeX source
python generate_monthly.py --type morning --save-tex
```

### Different Page Sizes

```bash
# Standard letter size (8.5x11 inches)
python generate_monthly.py --type morning

# Remarkable 2 tablet size (6.18x8.24 inches)
python generate_monthly.py --type morning --remarkable
```

## PDF Features

### Navigation

Each generated PDF includes:

1. **Title Page**: Shows the prayer type and month/year
2. **Index Page**: Lists all days with clickable links
3. **Daily Prayers**: Each day's complete prayer with:
   - Navigation bar at the top (back to index, jump to top of day)
   - Current date shown in page header
   - Link to index in every page header

### Navigation Links

- **Index Links**: Click any date in the index to jump to that day's prayer
- **Header Links**: "Index" link in top-left of every page
- **Navigation Bar**: At the top of each day:
  - "← Back to Index": Return to the index page
  - "↑ Top of [Date]": Jump to the first page of that day's prayer
- **Current Day**: Center of header shows current day

## API Reference

### MonthlyPrayerGenerator Class

```python
from dailyoffice import MonthlyPrayerGenerator

generator = MonthlyPrayerGenerator()
```

#### Methods

##### `generate_monthly_latex(year, month, prayer_type='morning', page_size='letter')`

Generate LaTeX source for a monthly prayer document.

**Parameters:**
- `year` (int): The year (e.g., 2025)
- `month` (int): The month (1-12)
- `prayer_type` (str): Prayer type - 'morning', 'evening', 'midday', or 'compline'
- `page_size` (str): Page size - 'letter' or 'remarkable'

**Returns:** LaTeX document as a string

**Example:**
```python
latex_content = generator.generate_monthly_latex(
    year=2025,
    month=12,
    prayer_type='morning',
    page_size='letter'
)
```

##### `compile_to_pdf(year, month, output_pdf, prayer_type='morning', page_size='letter', save_tex=False, tex_filename=None)`

Generate and compile a monthly prayer document to PDF.

**Parameters:**
- `year` (int): The year
- `month` (int): The month (1-12)
- `output_pdf` (str): Output PDF filename
- `prayer_type` (str): Prayer type
- `page_size` (str): Page size - 'letter' or 'remarkable'
- `save_tex` (bool): Whether to save the .tex source file
- `tex_filename` (str): Custom .tex filename (if save_tex is True)

**Example:**
```python
generator.compile_to_pdf(
    year=2025,
    month=12,
    output_pdf='december_2025_morning.pdf',
    prayer_type='morning',
    page_size='letter',
    save_tex=True,
    tex_filename='december_2025_morning.tex'
)
```

##### Context Manager Support

```python
with MonthlyPrayerGenerator() as generator:
    generator.compile_to_pdf(...)
# Resources automatically closed
```

## Requirements

- Python 3.7+
- pdflatex (for PDF compilation)
- Internet connection (to fetch prayers from Daily Office 2019 API)

### Installing LaTeX

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-latex-base texlive-latex-extra
```

**macOS:**
```bash
brew install --cask mactex-no-gui
```

**Windows:**
Install MiKTeX or TeX Live from their respective websites.

## How It Works

1. **Fetches Data**: Makes API calls to Daily Office 2019 for each day of the month
2. **Generates LaTeX**: Creates individual LaTeX documents for each day
3. **Combines Content**: Merges all days into a single document with:
   - Shared preamble (document settings, packages)
   - Title page
   - Index with hyperlinks
   - Daily content with navigation
4. **Compiles PDF**: Uses pdflatex to create the final PDF

## Tips

- **Large Files**: Monthly PDFs can be large (50-100+ pages). Consider using `--remarkable` for smaller file sizes.
- **API Rate Limiting**: Generating a full month makes 28-31 API calls. If you encounter issues, wait a moment and retry.
- **Custom Months**: Use month names for convenience: `--month December` instead of `--month 12`
- **Save LaTeX**: Use `--save-tex` to save the source file if you want to customize the layout

## Troubleshooting

### LaTeX Errors

If you get LaTeX compilation errors:
1. Ensure pdflatex is installed and in your PATH
2. Try running with `--save-tex` to inspect the generated LaTeX
3. Check for special characters in prayer content that might need escaping

### API Errors

If API calls fail:
1. Check your internet connection
2. Verify the Daily Office 2019 API is accessible
3. Try a different month/year

### PDF Not Generated

1. Check that pdflatex completed successfully (look for error messages)
2. Ensure you have write permissions in the output directory
3. Try a different output filename

## Support

For issues or questions:
- Check the main README.md for general setup
- Report bugs via GitHub issues
- Visit https://www.dailyoffice2019.com/ for information about the Daily Office
