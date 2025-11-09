#!/usr/bin/env python3
"""
API Sample Data Collection Script

This script fetches sample data from various Daily Office 2019 API endpoints
and saves them to JSON files for development and testing purposes.

Run this script locally where you have API access, then share the
'api_samples' directory for further development.
"""

import requests
import json
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Any, List, Tuple


class APISampleCollector:
    """Collects sample data from Daily Office API endpoints."""

    BASE_URL = "https://api.dailyoffice2019.com/api/v1/"

    def __init__(self, output_dir: str = "api_samples"):
        """
        Initialize the sample collector.

        Args:
            output_dir: Directory to save sample JSON files
        """
        self.base_url = self.BASE_URL
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Create subdirectories for organization
        self.dirs = {
            'office': self.output_dir / 'office',
            'family': self.output_dir / 'family',
            'calendar': self.output_dir / 'calendar',
            'general': self.output_dir / 'general',
        }
        for dir_path in self.dirs.values():
            dir_path.mkdir(exist_ok=True)

        # Set up session with browser-like headers
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })

        # Track results
        self.results = {
            'successful': [],
            'failed': [],
        }

    def fetch_endpoint(self, endpoint: str, description: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Fetch data from an endpoint.

        Args:
            endpoint: API endpoint path (without base URL)
            description: Human-readable description

        Returns:
            Tuple of (success: bool, data: dict or error message)
        """
        url = f"{self.base_url}{endpoint}"
        print(f"  Fetching: {description}")
        print(f"    URL: {url}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            print(f"    ✓ Success ({len(json.dumps(data))} bytes)")
            return True, data

        except requests.RequestException as e:
            error_msg = f"Failed: {str(e)}"
            print(f"    ✗ {error_msg}")
            return False, {'error': error_msg, 'url': url}

    def save_json(self, data: Dict[str, Any], filepath: Path):
        """Save data to a JSON file with pretty formatting."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"    Saved to: {filepath}")

    def collect_office_prayers(self, test_dates: List[date]):
        """
        Collect samples from office prayer endpoints.

        Args:
            test_dates: List of dates to test
        """
        print("\n" + "="*80)
        print("COLLECTING OFFICE PRAYERS")
        print("="*80)

        office_types = [
            'morning_prayer',
            'midday_prayer',
            'evening_prayer',
            'compline',
        ]

        for office_type in office_types:
            print(f"\n{office_type.upper().replace('_', ' ')}:")
            print("-" * 60)

            for test_date in test_dates:
                date_str = test_date.strftime("%Y-%m-%d")
                endpoint = f"office/{office_type}/{date_str}"
                description = f"{office_type.replace('_', ' ').title()} - {date_str}"

                success, data = self.fetch_endpoint(endpoint, description)

                if success:
                    filename = f"{office_type}_{date_str}.json"
                    filepath = self.dirs['office'] / filename
                    self.save_json(data, filepath)
                    self.results['successful'].append(f"office/{office_type}/{date_str}")
                else:
                    self.results['failed'].append(f"office/{office_type}/{date_str}")

    def collect_family_prayers(self, test_dates: List[date]):
        """
        Collect samples from family prayer endpoints.

        Args:
            test_dates: List of dates to test
        """
        print("\n" + "="*80)
        print("COLLECTING FAMILY PRAYERS")
        print("="*80)

        family_types = [
            'morning_prayer',
            'midday_prayer',
            'early_evening_prayer',
            'close_of_day_prayer',
        ]

        for family_type in family_types:
            print(f"\n{family_type.upper().replace('_', ' ')}:")
            print("-" * 60)

            # Just collect one sample date for family prayers
            test_date = test_dates[0]
            date_str = test_date.strftime("%Y-%m-%d")
            endpoint = f"family/{family_type}/{date_str}"
            description = f"Family {family_type.replace('_', ' ').title()} - {date_str}"

            success, data = self.fetch_endpoint(endpoint, description)

            if success:
                filename = f"family_{family_type}_{date_str}.json"
                filepath = self.dirs['family'] / filename
                self.save_json(data, filepath)
                self.results['successful'].append(f"family/{family_type}/{date_str}")
            else:
                self.results['failed'].append(f"family/{family_type}/{date_str}")

    def collect_calendar_info(self, test_dates: List[date]):
        """
        Collect calendar information.

        Args:
            test_dates: List of dates to test
        """
        print("\n" + "="*80)
        print("COLLECTING CALENDAR DATA")
        print("="*80)

        # Test different calendar endpoint formats
        for test_date in test_dates[:2]:  # Just a couple samples
            # Full date
            date_str = test_date.strftime("%Y-%m-%d")
            endpoint = f"calendar/{date_str}"
            description = f"Calendar - {date_str}"

            success, data = self.fetch_endpoint(endpoint, description)

            if success:
                filename = f"calendar_{date_str}.json"
                filepath = self.dirs['calendar'] / filename
                self.save_json(data, filepath)
                self.results['successful'].append(endpoint)
            else:
                self.results['failed'].append(endpoint)

        # Test month view (one sample)
        test_date = test_dates[0]
        year_month = test_date.strftime("%Y-%m")
        endpoint = f"calendar/{year_month}"
        description = f"Calendar Month - {year_month}"

        success, data = self.fetch_endpoint(endpoint, description)

        if success:
            filename = f"calendar_month_{year_month}.json"
            filepath = self.dirs['calendar'] / filename
            self.save_json(data, filepath)
            self.results['successful'].append(endpoint)
        else:
            self.results['failed'].append(endpoint)

    def collect_readings(self, test_dates: List[date]):
        """
        Collect daily readings.

        Args:
            test_dates: List of dates to test
        """
        print("\n" + "="*80)
        print("COLLECTING DAILY READINGS")
        print("="*80)

        for test_date in test_dates[:2]:  # Just a couple samples
            date_str = test_date.strftime("%Y-%m-%d")
            endpoint = f"readings/{date_str}"
            description = f"Readings - {date_str}"

            success, data = self.fetch_endpoint(endpoint, description)

            if success:
                filename = f"readings_{date_str}.json"
                filepath = self.dirs['general'] / filename
                self.save_json(data, filepath)
                self.results['successful'].append(endpoint)
            else:
                self.results['failed'].append(endpoint)

    def collect_general_endpoints(self):
        """Collect data from general endpoints (non-date-specific)."""
        print("\n" + "="*80)
        print("COLLECTING GENERAL ENDPOINTS")
        print("="*80)

        endpoints = [
            ('about', 'About Information'),
            ('collects', 'All Collects'),
            ('grouped_collects', 'Grouped Collects'),
            ('collect_categories/', 'Collect Categories'),
            ('psalms/', 'Psalm List'),
            ('psalms/topics/', 'Psalm Topics'),
            ('litany', 'Litany'),
            ('available_settings/', 'Available Settings'),
        ]

        for endpoint, description in endpoints:
            success, data = self.fetch_endpoint(endpoint, description)

            if success:
                filename = f"{endpoint.replace('/', '_').strip('_')}.json"
                filepath = self.dirs['general'] / filename
                self.save_json(data, filepath)
                self.results['successful'].append(endpoint)
            else:
                self.results['failed'].append(endpoint)

    def collect_sample_psalms(self):
        """Collect a few individual psalm examples."""
        print("\n" + "="*80)
        print("COLLECTING SAMPLE INDIVIDUAL PSALMS")
        print("="*80)

        # Collect a few sample psalms
        psalm_ids = [1, 23, 51, 119]  # Common psalms

        for psalm_id in psalm_ids:
            endpoint = f"psalms/{psalm_id}/"
            description = f"Psalm {psalm_id}"

            success, data = self.fetch_endpoint(endpoint, description)

            if success:
                filename = f"psalm_{psalm_id}.json"
                filepath = self.dirs['general'] / filename
                self.save_json(data, filepath)
                self.results['successful'].append(endpoint)
            else:
                self.results['failed'].append(endpoint)

    def print_summary(self):
        """Print a summary of collection results."""
        print("\n" + "="*80)
        print("COLLECTION SUMMARY")
        print("="*80)

        total = len(self.results['successful']) + len(self.results['failed'])
        success_count = len(self.results['successful'])
        fail_count = len(self.results['failed'])

        print(f"\nTotal endpoints tested: {total}")
        print(f"  ✓ Successful: {success_count}")
        print(f"  ✗ Failed: {fail_count}")

        if self.results['failed']:
            print("\nFailed endpoints:")
            for endpoint in self.results['failed']:
                print(f"  - {endpoint}")

        print(f"\nAll data saved to: {self.output_dir.absolute()}")
        print("\nNext steps:")
        print("  1. Review the saved JSON files")
        print("  2. Compress the 'api_samples' directory:")
        print(f"     zip -r api_samples.zip {self.output_dir}")
        print("  3. Share the api_samples.zip file for further development")

    def create_readme(self):
        """Create a README file documenting the collected data."""
        readme_path = self.output_dir / "README.md"

        readme_content = f"""# Daily Office API Sample Data

This directory contains sample API responses collected from the Daily Office 2019 API.

## Collection Date
{date.today().strftime("%Y-%m-%d")}

## Directory Structure

- `office/` - Office prayers (morning, midday, evening, compline)
- `family/` - Family prayers
- `calendar/` - Calendar information
- `general/` - General endpoints (collects, psalms, etc.)

## Summary

- Total successful: {len(self.results['successful'])}
- Total failed: {len(self.results['failed'])}

## Successful Endpoints

{chr(10).join(f"- {ep}" for ep in self.results['successful'])}

## Failed Endpoints

{chr(10).join(f"- {ep}" for ep in self.results['failed']) if self.results['failed'] else "None"}

## Usage

These files can be used for:
- Development and testing without API access
- Understanding API response structures
- Building offline functionality
- Creating comprehensive tests

## File Naming Convention

- Office prayers: `{{type}}_{{YYYY-MM-DD}}.json`
- Family prayers: `family_{{type}}_{{YYYY-MM-DD}}.json`
- Calendar: `calendar_{{YYYY-MM-DD}}.json` or `calendar_month_{{YYYY-MM}}.json`
- General: `{{endpoint_name}}.json`
"""

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

        print(f"\nCreated README: {readme_path}")


def main():
    """Main execution function."""
    print("="*80)
    print("DAILY OFFICE 2019 API - SAMPLE DATA COLLECTOR")
    print("="*80)
    print("\nThis script will fetch sample data from various API endpoints.")
    print("Make sure you have internet access and the API is reachable.\n")

    # Define test dates - use a variety of dates to capture different liturgical situations
    today = date.today()
    test_dates = [
        today,                              # Today
        date(2025, 12, 25),                # Christmas
        date(2025, 4, 20),                 # Easter Sunday 2025
        date(2025, 3, 5),                  # Ash Wednesday 2025
        date(2025, 11, 23),                # Regular Sunday
    ]

    print(f"Test dates: {', '.join(d.strftime('%Y-%m-%d') for d in test_dates)}\n")

    # Create collector and gather data
    collector = APISampleCollector()

    try:
        # Collect office prayers (main focus)
        collector.collect_office_prayers(test_dates)

        # Collect family prayers (one sample per type)
        collector.collect_family_prayers(test_dates)

        # Collect calendar information
        collector.collect_calendar_info(test_dates)

        # Collect daily readings
        collector.collect_readings(test_dates)

        # Collect general endpoints
        collector.collect_general_endpoints()

        # Collect sample individual psalms
        collector.collect_sample_psalms()

        # Create documentation
        collector.create_readme()

        # Print summary
        collector.print_summary()

        return 0

    except KeyboardInterrupt:
        print("\n\nCollection interrupted by user.")
        collector.print_summary()
        return 1
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
