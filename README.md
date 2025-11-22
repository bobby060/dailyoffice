# Daily Office Prayer Generator

Generate beautifully formatted prayer documents from *The Book of Common Prayer* (2019) using the Daily Office 2019 API.

One of my daily struggles is the tension between the desire to disconnect from my phone and the convenience of not having to flip back and forward between the BCP and the readings. This project is an attempt to solve that problem by generating a single, well-formatted document for each prayer that I can send to my e-reader or print out.

## Overview

This Python application fetches daily office liturgy from the [Daily Office 2019 API](https://api.dailyoffice2019.com) and generates well-formatted Markdown and PDF documents. The application supports:

- **Morning Prayer** - Complete morning office with readings and canticles
- **Evening Prayer** - Evening office with appropriate canticles
- **Midday Prayer** - Midday office for noontime prayer

Each service includes all components.

Examples of generated documents are included in the repository for reference.

## Features

-  **All four daily prayers**: Morning, Evening, Midday Prayer, and Compline
-  **Monthly generation**: Create a complete month of prayers in one PDF with hyperlinked navigation
-  **Multiple output formats**: Markdown, PDF (via WeasyPrint), and PDF (via LaTeX)
-  **LaTeX generation**: Generate beautiful PDFs with LaTeX for professional typesetting
-  **Multiple page sizes**: Letter and Remarkable 2 tablet sizes
-  **Clean formatting**: Generally matches the style of the printed BCP/ 2019 website
-  **Fetch prayers for any date**
-  **Includes all daily readings and prayers**
-  **Command-line interface** for easy use

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- texlive (for LaTeX PDF generation, optional)

### Setup

1. Clone or download this repository

```bash
git clone https://github.com/bobby060/dailyoffice.git
cd dailyoffice
```

2. Install dependencies:


Recommend doing this inside a virtual environment

```bash
pip install -r requirements.txt
```

If you only want Markdown output (not PDF), you can install just the required dependency:

```bash
pip install requests
```

### Optional: LaTeX for PDF Generation

For high-quality PDF generation using LaTeX (optional, alternative to WeasyPrint):

**Ubuntu/Debian:**
```bash
sudo apt-get install texlive-latex-base
sudo apt-get install texlive-latex-extra
```

**macOS:**
*not tested*
```bash
brew install --cask basictex
# or for full installation:
brew install --cask mactex-no-gui
```

**Windows:**
*not tested*
- Install [MiKTeX](https://miktex.org/) or [TeX Live](https://www.tug.org/texlive/)

LaTeX provides professional typesetting and is recommended for the best-looking PDFs. If you don't install LaTeX, you can still use the `--pdf` option which uses WeasyPrint.

## Usage

### Quick Start

**Single Day Prayer:**
Generate morning prayer for today:

```bash
python generate_daily.py --type morning
```

This creates a file named `Morning-Prayer-Mon-DD-YYYY.md` with today's morning prayer.

**Monthly Prayer:**
Generate all prayers for a month:

```bash
python generate_monthly.py --type morning
```

This creates a PDF with all morning prayers for the current month, including a title page, index, and hyperlinked navigation.

To see all available options:

```bash
python generate_daily.py --help
python generate_monthly.py --help
```

### Command-Line Options

```bash
python generate_daily.py [OPTIONS]
```

**Options:**

- `-h, --help` - Show help message and exit
- `-t, --type {morning|evening|midday}` - Type of prayer to generate, required
- `-d, --date YYYY-MM-DD` - Specify a date for the prayer (default: today)
- `-o, --output FILE` - Specify output filename (default: <Type>-Prayer-Mon-DD-YYYY.md)
- `--remarkable` - Format output for Remarkable 2 tablet (PDF only)
- `--pdf` - Generate PDF output using WeasyPrint (requires markdown and weasyprint packages)
- `--latex` - Generate PDF using LaTeX (requires pdflatex). Default: output PDF only.
- `--save-tex` - When using --latex, also save the .tex file (in addition to PDF)
- `--print` - Print to console instead of saving to file
### Examples

1. **Generate morning prayer for Christmas Day:**
   ```bash
   python generate_daily.py --type morning --date 2025-12-25 --output christmas_morning.md
   ```

2. **Generate evening prayer as PDF (using WeasyPrint):**
   ```bash
   python generate_daily.py --type evening --pdf --output evening_prayer.pdf
   ```

3. **Generate morning prayer as PDF using LaTeX:**
   ```bash
   python generate_daily.py --type morning --latex
   ```

4. **Generate PDF with LaTeX and save the .tex source file:**
   ```bash
   python generate_daily.py --type morning --latex --save-tex
   ```

5. **Generate midday prayer for a specific date:**
   ```bash
   python generate_daily.py --type midday --date 2025-11-08
   ```

6. **Preview without saving:**
   ```bash
   python generate_daily.py --type morning --print
   ```

7. **Generate all three prayers for Sunday:**
   ```bash
   python generate_daily.py --type morning --date 2025-11-23 --output sunday_morning.md
   python generate_daily.py --type midday --date 2025-11-23 --output sunday_midday.md
   python generate_daily.py --type evening --date 2025-11-23 --output sunday_evening.md
   ```

### Monthly Prayer Generation

For a complete month of prayers in one PDF document, use `generate_monthly.py`:

Options are similar to above except you can specify the month and year instead of date.

```bash
# Generate morning prayers for current month
python generate_monthly.py --type morning

# Generate for a specific month
python generate_monthly.py --type evening --year 2025 --month December

# Format for Remarkable 2 tablet
python generate_monthly.py --type morning --remarkable
```

**Monthly PDF Features:**
- Title page with month and prayer type
- Hyperlinked index of all days
- Navigation bar on each day (back to index, jump to top of day)
- Current day shown in page header

See [MONTHLY_GENERATOR.md](MONTHLY_GENERATOR.md) for complete documentation on monthly generation.


## AWS Cloud Deployment

This application can be deployed as a serverless API on AWS Lambda with automatic PDF caching via S3. This allows you to generate prayer PDFs on-demand via HTTP requests without running the application locally.

For detailed deployment instructions, troubleshooting, and customization options, see [aws/README.md](aws/README.md).

## License

This project is provided as-is for personal use in daily prayer and worship.

The liturgical content is from *The Book of Common Prayer* (2019) of the Anglican Church in North America and should be used in accordance with their guidelines. Notably, this repository is not associated with the Anglican Church in North America, the Book of Common Prayer or the Daily Office 2019 website.

## Credits

- API provided by [Daily Office 2019](https://www.dailyoffice2019.com)
- Liturgical content from *The Book of Common Prayer* (2019), Anglican Church in North America via that API

## Support

For issues with this generator, please check the error messages and ensure:
1. You have an internet connection
2. The date format is correct (YYYY-MM-DD)
3. Dependencies are installed (`pip install -r requirements.txt`)
4. Submit an issue on GitHub if you encounter bugs or have questions
