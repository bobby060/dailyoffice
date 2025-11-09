# Daily Office Prayer Generator

Generate beautifully formatted prayer documents from *The Book of Common Prayer* (2019) using the Daily Office 2019 API.

## Overview

This Python application fetches daily office liturgy from the [Daily Office 2019 API](https://api.dailyoffice2019.com) and generates well-formatted Markdown and PDF documents. The application supports:

- **Morning Prayer** - Complete morning office with readings and canticles
- **Evening Prayer** - Evening office with appropriate canticles
- **Midday Prayer** - Midday office for noontime prayer

Each service includes all components.

Examples of generated documents are included in the repository for reference.

## Features

- ✅ **Three prayer types**: Morning, Evening, and Midday Prayer
- ✅ **Multiple output formats**: Markdown and PDF
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



2. Install dependencies:


Recommend doing this inside a virtual environment

```bash
pip install -r requirements.txt
```

This will install:
- `requests` - for API communication
- `markdown` - for PDF generation
- `weasyprint` - for PDF generation

If you only want Markdown output (not PDF), you can install just the required dependency:

```bash
pip install requests
```

## Usage

### Basic Usage

Generate morning prayer for today:

```bash
python main.py --type morning
```

This creates a file named `morning_prayer_YYYY-MM-DD.md` with today's morning prayer.

To see all available options:

```bash
python main.py
# or
python main.py --help
```

### Command-Line Options

```bash
python main.py [OPTIONS]
```

**Options:**

- `-h, --help` - Show help message and exit
  ```bash
  python main.py --help
  ```

- `-t, --type {morning|evening|midday}` - Type of prayer to generate (default: morning)
  ```bash
  python main.py --type evening
  ```

- `-d, --date YYYY-MM-DD` - Specify a date for the prayer (default: today)
  ```bash
  python main.py --date 2025-12-25
  ```

- `-o, --output FILE` - Specify output filename (default: <type>_prayer_YYYY-MM-DD.md)
  ```bash
  python main.py --output my_prayer.md
  ```

- `--pdf` - Generate PDF output instead of Markdown
  ```bash
  python main.py --pdf
  ```

- `--print` - Print to console instead of saving to file
  ```bash
  python main.py --print
  ```

### Examples

1. **Generate morning prayer for Christmas Day:**
   ```bash
   python main.py --date 2025-12-25 --output christmas_morning.md
   ```

2. **Generate evening prayer as PDF:**
   ```bash
   python main.py --type evening --pdf --output evening_prayer.pdf
   ```

3. **Generate midday prayer for a specific date:**
   ```bash
   python main.py --type midday --date 2025-11-08
   ```

4. **Preview without saving:**
   ```bash
   python main.py --print
   ```

5. **Generate all three prayers for Sunday:**
   ```bash
   python main.py --type morning --date 2025-11-23 --output sunday_morning.md
   python main.py --type midday --date 2025-11-23 --output sunday_midday.md
   python main.py --type evening --date 2025-11-23 --output sunday_evening.md
   ```

## Project Structure

```
dailyoffice/
├── dailyoffice/                   # Main package
│   ├── __init__.py               # Package initialization
│   ├── api_client.py             # API communication class
│   ├── prayer_generator.py       # Markdown generation class
│   └── prayer_service.py         # Service layer coordinating components
├── main.py                        # CLI entry point
├── collect_api_samples.py         # API sample data collection script
├── test_with_sample_data.py       # Test with sample data
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── TESTING_INSTRUCTIONS.md        # Instructions for collecting API samples
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

- [ ] LaTeX output generation for even more precise formatting
- [ ] Compline support
- [ ] Custom canticle selection
- [ ] Configuration file support
- [ ] Multiple output formats (HTML, DOCX)
- [ ] Week-at-a-time generation
- [ ] Custom CSS styling for PDF output
- [ ] Combine morning, midday, and evening prayers into a single document

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
