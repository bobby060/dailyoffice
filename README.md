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

- ✅ **Four prayer types**: Morning, Evening, Midday Prayer, and Compline
- ✅ **Monthly generation**: Create a complete month of prayers in one PDF with hyperlinked navigation
- ✅ **Multiple output formats**: Markdown, PDF (via WeasyPrint), and PDF (via LaTeX)
- ✅ **LaTeX generation**: Generate beautiful PDFs with LaTeX for professional typesetting
- ✅ **Multiple page sizes**: Letter and Remarkable 2 tablet sizes
- ✅ **Clean formatting**: People's responses in bold, no labels needed
- ✅ **Psalm formatting**: Responsive reading format (officiant normal, people bold)
- ✅ **Fetch prayers for any date**
- ✅ **Includes all daily readings and prayers**
- ✅ **Command-line interface** for easy use
- ✅ **Comprehensive test suite** (49 tests)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

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
```

**macOS:**
```bash
brew install --cask basictex
# or for full installation:
brew install --cask mactex-no-gui
```

**Windows:**
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
  ```bash
  python generate_daily.py --help
  ```

- `-t, --type {morning|evening|midday}` - Type of prayer to generate, required
  ```bash
  python generate_daily.py --type evening
  ```

- `-d, --date YYYY-MM-DD` - Specify a date for the prayer (default: today)
  ```bash
  python generate_daily.py --date 2025-12-25
  ```

- `-o, --output FILE` - Specify output filename (default: <Type>-Prayer-Mon-DD-YYYY.md)
  ```bash
  python generate_daily.py --output my_prayer.md
  ```

- `--pdf` - Generate PDF output using WeasyPrint (requires markdown and weasyprint packages)
  ```bash
  python generate_daily.py --pdf
  ```

- `--latex` - Generate PDF using LaTeX (requires pdflatex). Default: output PDF only.
  ```bash
  python generate_daily.py --latex
  ```

- `--save-tex` - When using --latex, also save the .tex file (in addition to PDF)
  ```bash
  python generate_daily.py --latex --save-tex
  ```

- `--print` - Print to console instead of saving to file
  ```bash
  python generate_daily.py --print
  ```

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
- Supports all page sizes (letter and remarkable)

See [MONTHLY_GENERATOR.md](MONTHLY_GENERATOR.md) for complete documentation on monthly generation.

## Project Structure

```
dailyoffice/
├── dailyoffice/                      # Main package
│   ├── __init__.py                  # Package initialization
│   ├── api_client.py                # API communication class
│   ├── prayer_generator.py          # Markdown/LaTeX generation class
│   ├── prayer_service.py            # Service layer coordinating components
│   └── monthly_prayer_generator.py  # Monthly prayer generation class
├── generate_daily.py                 # CLI entry point for single prayers
├── generate_monthly.py               # CLI entry point for monthly prayers
├── collect_api_samples.py            # API sample data collection script
├── test_with_sample_data.py          # Test with sample data
├── requirements.txt                  # Python dependencies
├── README.md                         # This file
├── MONTHLY_GENERATOR.md              # Monthly generator documentation
└── TESTING_INSTRUCTIONS.md           # Instructions for collecting API samples
```

## API Information

This application uses the [Daily Office 2019 API](https://api.dailyoffice2019.com), which provides:

- Daily morning, midday, evening, and compline prayers
- Readings from the Revised Common Lectionary
- Proper collects and prayers for each day
- Church calendar information (seasons, feasts, commemorations)

**API Endpoint Formats:**
```
https://api.dailyoffice2019.com/api/v1/office/morning_prayer/YYYY-MM-DD
https://api.dailyoffice2019.com/api/v1/office/evening_prayer/YYYY-MM-DD
https://api.dailyoffice2019.com/api/v1/office/midday_prayer/YYYY-MM-DD
```

## Development

### Collecting API Sample Data

For development and testing purposes, you can collect sample API responses:

```bash
python collect_api_samples.py
```

This script will:
- Fetch data from various API endpoints
- Save responses to the `api_samples/` directory
- Create organized JSON files for testing
- Generate a summary report

See [TESTING_INSTRUCTIONS.md](TESTING_INSTRUCTIONS.md) for detailed instructions.

### Running Tests

The project includes comprehensive unit and integration tests (49 tests total):

```bash
# Run all tests
./run_tests.sh

# Or use unittest directly
python3 -m unittest discover -s tests -p "test_*.py"

# Run specific test file
python3 -m unittest tests.test_api_client -v
```

Test the markdown generator with sample data:

```bash
python test_with_sample_data.py
```

See [tests/README.md](tests/README.md) for detailed testing documentation.

### Code Style

The codebase follows Python PEP 8 style guidelines with comprehensive docstrings for all classes and methods.

## Future Enhancements

- [x] Compline support
- [x] Monthly prayer generation with navigation
- [x] Multiple page sizes (letter, remarkable)
- [ ] Custom canticle selection
- [ ] Configuration file support
- [ ] Multiple output formats (HTML, DOCX)
- [ ] Week-at-a-time generation
- [ ] Custom CSS styling for PDF output

## License

This project is provided as-is for personal use in daily prayer and worship.

The liturgical content is from *The Book of Common Prayer* (2019) of the Anglican Church in North America and should be used in accordance with their guidelines. Notably, this repository is not associated with the Anglican Church in North America, the Book of Common Prayer or the Daily Office 2019 website.

## Credits

- API provided by [Daily Office 2019](https://www.dailyoffice2019.com)
- Liturgical content from *The Book of Common Prayer* (2019), Anglican Church in North America via that API

## Support

For issues with the API or liturgical content, visit [https://www.dailyoffice2019.com](https://www.dailyoffice2019.com).

For issues with this generator, please check the error messages and ensure:
1. You have an internet connection
2. The date format is correct (YYYY-MM-DD)
3. Dependencies are installed (`pip install -r requirements.txt`)

---

*May the grace of our Lord Jesus Christ, and the love of God, and the fellowship of the Holy Spirit, be with us all evermore. Amen.*
