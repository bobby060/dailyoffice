"""
Unit tests for Daily Office API Client

Tests the API client functionality using real API sample data.
"""

import unittest
import json
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from dailyoffice.api_client import DailyOfficeAPIClient


class TestDailyOfficeAPIClient(unittest.TestCase):
    """Test suite for DailyOfficeAPIClient."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.samples_dir = Path(__file__).parent.parent / 'api_samples'
        cls.office_dir = cls.samples_dir / 'office'

    def setUp(self):
        """Set up each test."""
        self.client = DailyOfficeAPIClient()

    def tearDown(self):
        """Clean up after each test."""
        self.client.close()

    def test_client_initialization(self):
        """Test that client initializes correctly."""
        self.assertEqual(self.client.base_url, "https://api.dailyoffice2019.com/api/v1/")
        self.assertIsNotNone(self.client.session)
        self.assertIn('User-Agent', self.client.session.headers)

    def test_custom_base_url(self):
        """Test client with custom base URL."""
        custom_url = "https://custom.api.com/v2/"
        client = DailyOfficeAPIClient(base_url=custom_url)
        self.assertEqual(client.base_url, custom_url)
        client.close()

    @patch('dailyoffice.api_client.requests.Session.get')
    def test_get_morning_prayer_success(self, mock_get):
        """Test successful morning prayer fetch."""
        # Load real sample data
        sample_file = self.office_dir / 'morning_prayer_2025-11-08.json'
        with open(sample_file, 'r') as f:
            sample_data = json.load(f)

        # Mock the response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_data
        mock_get.return_value = mock_response

        # Test the method
        test_date = date(2025, 11, 8)
        result = self.client.get_morning_prayer(test_date)

        # Verify
        self.assertIsInstance(result, dict)
        self.assertIn('modules', result)
        self.assertIn('calendar_day', result)
        self.assertEqual(len(result['modules']), 16)

        # Verify correct endpoint was called
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        self.assertIn('morning_prayer/2025-11-08', call_args[0][0])

    @patch('dailyoffice.api_client.requests.Session.get')
    def test_get_morning_prayer_default_date(self, mock_get):
        """Test morning prayer fetch with default (today) date."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'modules': [], 'calendar_day': {}}
        mock_get.return_value = mock_response

        result = self.client.get_morning_prayer()

        # Should call with today's date
        today = date.today()
        expected_date_str = today.strftime("%Y-%m-%d")
        call_args = mock_get.call_args
        self.assertIn(expected_date_str, call_args[0][0])

    @patch('dailyoffice.api_client.requests.Session.get')
    def test_get_evening_prayer_success(self, mock_get):
        """Test successful evening prayer fetch."""
        sample_file = self.office_dir / 'evening_prayer_2025-11-08.json'
        with open(sample_file, 'r') as f:
            sample_data = json.load(f)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_data
        mock_get.return_value = mock_response

        test_date = date(2025, 11, 8)
        result = self.client.get_evening_prayer(test_date)

        self.assertIsInstance(result, dict)
        self.assertIn('modules', result)

    @patch('dailyoffice.api_client.requests.Session.get')
    def test_api_error_handling(self, mock_get):
        """Test handling of API errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Not Found")
        mock_get.return_value = mock_response

        test_date = date(2025, 11, 8)

        with self.assertRaises(Exception):
            self.client.get_morning_prayer(test_date)

    @patch('dailyoffice.api_client.requests.Session.get')
    def test_invalid_json_handling(self, mock_get):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        test_date = date(2025, 11, 8)

        with self.assertRaises(ValueError):
            self.client.get_morning_prayer(test_date)

    def test_context_manager(self):
        """Test client can be used as context manager."""
        with DailyOfficeAPIClient() as client:
            self.assertIsNotNone(client.session)

        # Session should be closed after context
        # Note: requests.Session doesn't have an 'is_closed' attribute,
        # so we just verify it doesn't error

    def test_close_method(self):
        """Test explicit close method."""
        client = DailyOfficeAPIClient()
        client.close()
        # Should not raise an error


class TestAPIDataStructure(unittest.TestCase):
    """Test the structure of real API responses."""

    @classmethod
    def setUpClass(cls):
        """Load sample data for testing."""
        cls.samples_dir = Path(__file__).parent.parent / 'api_samples'
        cls.office_dir = cls.samples_dir / 'office'

    def load_sample(self, filename):
        """Helper to load a sample JSON file."""
        with open(self.office_dir / filename, 'r') as f:
            return json.load(f)

    def test_morning_prayer_structure(self):
        """Test morning prayer has expected structure."""
        data = self.load_sample('morning_prayer_2025-11-08.json')

        # Top-level keys
        self.assertIn('modules', data)
        self.assertIn('calendar_day', data)

        # Calendar day structure
        calendar = data['calendar_day']
        self.assertIn('date', calendar)
        self.assertIn('date_description', calendar)
        self.assertIn('season', calendar)
        self.assertIn('commemorations', calendar)

        # Modules structure
        self.assertIsInstance(data['modules'], list)
        self.assertGreater(len(data['modules']), 0)

        # Check first module
        first_module = data['modules'][0]
        self.assertIn('name', first_module)
        self.assertIn('lines', first_module)

    def test_all_morning_prayer_samples(self):
        """Test all morning prayer samples have consistent structure."""
        morning_prayer_files = [
            'morning_prayer_2025-03-05.json',
            'morning_prayer_2025-04-20.json',
            'morning_prayer_2025-11-08.json',
            'morning_prayer_2025-11-23.json',
            'morning_prayer_2025-12-25.json',
        ]

        for filename in morning_prayer_files:
            with self.subTest(file=filename):
                data = self.load_sample(filename)
                self.assertIn('modules', data)
                self.assertIn('calendar_day', data)
                self.assertIsInstance(data['modules'], list)
                self.assertGreater(len(data['modules']), 0)

    def test_evening_prayer_structure(self):
        """Test evening prayer has expected structure."""
        data = self.load_sample('evening_prayer_2025-11-08.json')

        self.assertIn('modules', data)
        self.assertIn('calendar_day', data)
        self.assertIsInstance(data['modules'], list)

    def test_compline_structure(self):
        """Test compline has expected structure."""
        data = self.load_sample('compline_2025-11-08.json')

        self.assertIn('modules', data)
        self.assertIn('calendar_day', data)
        self.assertIsInstance(data['modules'], list)

    def test_module_line_types(self):
        """Test that modules contain expected line types."""
        data = self.load_sample('morning_prayer_2025-11-08.json')

        expected_line_types = {
            'heading', 'subheading', 'rubric', 'leader', 'congregation',
            'leader_dialogue', 'congregation_dialogue', 'reader', 'citation',
            'html', 'spacer'
        }

        found_line_types = set()
        for module in data['modules']:
            for line in module['lines']:
                if 'line_type' in line:
                    found_line_types.add(line['line_type'])

        # Check we found some expected types
        self.assertTrue(len(found_line_types.intersection(expected_line_types)) > 0)

    def test_calendar_day_date_formats(self):
        """Test calendar day date formats are consistent."""
        data = self.load_sample('morning_prayer_2025-11-08.json')

        calendar = data['calendar_day']
        self.assertIn('date', calendar)
        self.assertRegex(calendar['date'], r'^\d{4}-\d{2}-\d{2}$')

        date_desc = calendar['date_description']
        self.assertIn('weekday', date_desc)
        self.assertIn('month', date_desc)
        self.assertIn('day', date_desc)
        self.assertIn('year', date_desc)


if __name__ == '__main__':
    unittest.main()
