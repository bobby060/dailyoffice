# Daily Office Morning Prayer Generator

Generate beautifully formatted morning prayer documents from *The Book of Common Prayer* (2019) using the Daily Office 2019 API.

## Overview

This Python application fetches daily morning prayer liturgy from the [Daily Office 2019 API](https://api.dailyoffice2019.com) and generates well-formatted Markdown documents. The output includes all components of the morning prayer service:

- Opening Sentence
- Confession of Sin
- The Preces
- Invitatory (Venite)
- Psalms (with 30-day or 60-day reading cycle)
- Old Testament Reading
- Te Deum Laudamus (or other canticle)
- New Testament Reading
- Benedictus (Song of Zechariah)
- The Apostles' Creed
- The Prayers and Collects
- Final Prayers and Dismissal

## Features

- ✅ Fetch morning prayer for any date
- ✅ Support for both 30-day and 60-day psalm reading cycles
- ✅ Generate clean, readable Markdown output
- ✅ Includes all daily readings and prayers
- ✅ Properly formatted liturgical text with leader/congregation parts
- ✅ Command-line interface for easy use
- 🔄 Future: LaTeX output for precise PDF formatting

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone or download this repository

2. Install dependencies:

```bash
pip install -r requirements.txt
```

The required packages are:
- `requests` - for API communication
- `python-dateutil` - for date handling

## Usage

### Basic Usage

Generate morning prayer for today:

```bash
python main.py
```

This creates a file named `morning_prayer_YYYY-MM-DD.md` with today's morning prayer.

### Command-Line Options

```bash
python main.py [OPTIONS]
```

**Options:**

- `-d, --date YYYY-MM-DD` - Specify a date for the prayer (default: today)
  ```bash
  python main.py --date 2025-12-25
  ```

- `-p, --psalm-cycle {30|60}` - Choose psalm reading cycle (default: 60)
  ```bash
  python main.py --psalm-cycle 30
  ```

- `-o, --output FILE` - Specify output filename (default: morning_prayer_YYYY-MM-DD.md)
  ```bash
  python main.py --output my_prayer.md
  ```

- `--print` - Print to console instead of saving to file
  ```bash
  python main.py --print
  ```

### Examples

1. **Generate prayer for Christmas Day:**
   ```bash
   python main.py --date 2025-12-25 --output christmas_morning.md
   ```

2. **Use 30-day psalm cycle:**
   ```bash
   python main.py --psalm-cycle 30
   ```

3. **Preview without saving:**
   ```bash
   python main.py --print
   ```

4. **Generate for a specific date with custom filename:**
   ```bash
   python main.py -d 2025-11-08 -o november_8_prayer.md -p 60
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

## Architecture

The application is organized into three main components:

### 1. DailyOfficeAPIClient (`api_client.py`)

Handles all communication with the Daily Office 2019 API:
- Constructs proper API requests
- Manages HTTP sessions
- Handles errors and timeouts
- Supports both morning and evening prayer endpoints

### 2. MarkdownGenerator (`prayer_generator.py`)

Converts API responses into formatted Markdown:
- Processes different line types (headings, prayers, rubrics, etc.)
- Formats Scripture readings
- Handles indentation and liturgical formatting
- Cleans HTML content from readings

### 3. PrayerService (`prayer_service.py`)

High-level service layer that coordinates the workflow:
- Combines API client and markdown generator
- Provides simple interface for generating prayers
- Manages resource lifecycle

## API Information

This application uses the [Daily Office 2019 API](https://api.dailyoffice2019.com), which provides:

- Daily morning, midday, evening, and compline prayers
- Readings from the Revised Common Lectionary
- Proper collects and prayers for each day
- Church calendar information (seasons, feasts, commemorations)

**API Endpoint Format:**
```
https://api.dailyoffice2019.com/api/v1/office/morning_prayer/YYYY-MM-DD
```

## Output Format

The generated Markdown includes:

- **Liturgical metadata** - date, season, feast day
- **Structured sections** - each part of the service as a heading
- **Role indicators** - "Officiant:" and "People:" for responsive parts
- **Scripture** - formatted as blockquotes
- **Citations** - properly marked
- **Rubrics** - in italics

Example output structure:

```markdown
# Daily Morning Prayer
## Friday, November 8, 2025

**Friday after the Twenty-first Sunday after Pentecost**
*Season After Pentecost (green)*

---

## Opening Sentence

**Officiant:** The hour is coming, and is now here...

## Confession of Sin

*The Officiant says to the People*
...
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

- [ ] LaTeX output generation for precise PDF formatting
- [ ] Evening prayer support
- [ ] Compline support
- [ ] Custom canticle selection
- [ ] PDF generation directly
- [ ] Configuration file support
- [ ] Multiple output formats (HTML, DOCX)

## License

This project is provided as-is for personal use in daily prayer and worship.

The liturgical content is from *The Book of Common Prayer* (2019) of the Anglican Church in North America.

## Credits

- API provided by [Daily Office 2019](https://www.dailyoffice2019.com)
- Liturgical content from *The Book of Common Prayer* (2019), Anglican Church in North America

## Support

For issues with the API or liturgical content, visit [https://www.dailyoffice2019.com](https://www.dailyoffice2019.com).

For issues with this generator, please check the error messages and ensure:
1. You have an internet connection
2. The date format is correct (YYYY-MM-DD)
3. Dependencies are installed (`pip install -r requirements.txt`)

---

*May the grace of our Lord Jesus Christ, and the love of God, and the fellowship of the Holy Spirit, be with us all evermore. Amen.*
