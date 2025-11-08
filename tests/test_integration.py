"""
Integration tests for Daily Office Prayer Service

Tests the full workflow from API to markdown generation.
"""

import unittest
import json
from pathlib import Path
from datetime import date
from unittest.mock import Mock, patch
import tempfile

from dailyoffice import PrayerService, DailyOfficeAPIClient, MarkdownGenerator


class TestPrayerServiceIntegration(unittest.TestCase):
    """Integration tests for PrayerService."""

    @classmethod
    def setUpClass(cls):
        """Load sample data."""
        cls.samples_dir = Path(__file__).parent.parent / 'api_samples'
        cls.office_dir = cls.samples_dir / 'office'

    def load_sample(self, filename):
        """Helper to load a sample JSON file."""
        with open(self.office_dir / filename, 'r') as f:
            return json.load(f)

    def test_service_initialization(self):
        """Test that service initializes correctly."""
        service = PrayerService()
        self.assertIsInstance(service.api_client, DailyOfficeAPIClient)
        self.assertIsInstance(service.markdown_generator, MarkdownGenerator)
        service.close()

    @patch.object(DailyOfficeAPIClient, 'get_morning_prayer')
    def test_generate_morning_prayer_markdown(self, mock_api):
        """Test end-to-end markdown generation."""
        # Load real sample data
        sample_data = self.load_sample('morning_prayer_2025-11-08.json')
        mock_api.return_value = sample_data

        service = PrayerService()
        test_date = date(2025, 11, 8)

        markdown = service.generate_morning_prayer_markdown(test_date)

        # Verify API was called correctly
        mock_api.assert_called_once_with(prayer_date=test_date)

        # Verify markdown output
        self.assertIsInstance(markdown, str)
        self.assertGreater(len(markdown), 100)
        self.assertIn('# Daily Morning Prayer', markdown)
        self.assertIn('November 8, 2025', markdown)

        service.close()

    @patch.object(DailyOfficeAPIClient, 'get_morning_prayer')
    def test_save_morning_prayer(self, mock_api):
        """Test saving prayer to file."""
        sample_data = self.load_sample('morning_prayer_2025-11-08.json')
        mock_api.return_value = sample_data

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / 'test_prayer.md'

            service = PrayerService()
            service.save_morning_prayer(
                str(output_file),
                date(2025, 11, 8)
            )

            # File should exist
            self.assertTrue(output_file.exists())

            # Content should be valid
            with open(output_file, 'r') as f:
                content = f.read()

            self.assertIn('# Daily Morning Prayer', content)
            self.assertGreater(len(content), 100)

            service.close()

    def test_context_manager(self):
        """Test service can be used as context manager."""
        with PrayerService() as service:
            self.assertIsInstance(service, PrayerService)

    @patch.object(DailyOfficeAPIClient, 'get_morning_prayer')
    def test_multiple_dates(self, mock_api):
        """Test generating prayers for multiple dates."""
        dates_and_files = [
            (date(2025, 11, 8), 'morning_prayer_2025-11-08.json'),
            (date(2025, 12, 25), 'morning_prayer_2025-12-25.json'),
            (date(2025, 4, 20), 'morning_prayer_2025-04-20.json'),
        ]

        service = PrayerService()

        for test_date, filename in dates_and_files:
            with self.subTest(date=test_date):
                sample_data = self.load_sample(filename)
                mock_api.return_value = sample_data

                markdown = service.generate_morning_prayer_markdown(test_date)

                self.assertIsInstance(markdown, str)
                self.assertGreater(len(markdown), 100)

        service.close()


class TestEndToEndWorkflow(unittest.TestCase):
    """Test complete end-to-end workflows."""

    @classmethod
    def setUpClass(cls):
        """Load sample data."""
        cls.samples_dir = Path(__file__).parent.parent / 'api_samples'
        cls.office_dir = cls.samples_dir / 'office'

    def load_sample(self, filename):
        """Helper to load a sample JSON file."""
        with open(self.office_dir / filename, 'r') as f:
            return json.load(f)

    @patch.object(DailyOfficeAPIClient, 'get_morning_prayer')
    def test_complete_workflow_regular_day(self, mock_api):
        """Test complete workflow for a regular day."""
        sample_data = self.load_sample('morning_prayer_2025-11-08.json')
        mock_api.return_value = sample_data

        # Create service
        service = PrayerService()

        # Generate markdown
        markdown = service.generate_morning_prayer_markdown(date(2025, 11, 8))

        # Verify all major sections are present
        expected_sections = [
            'Opening Sentence',
            'Confession of Sin',
            'Preces',
            'Invitatory',
            'Psalms',
            'First Lesson',
            'TE DEUM LAUDAMUS',
            'Second Lesson',
            'BENEDICTUS',
            'Apostles\' Creed',
            'The Prayers',
            'Collect',
            'General Thanksgiving',
        ]

        for section in expected_sections:
            with self.subTest(section=section):
                self.assertIn(section, markdown)

        service.close()

    @patch.object(DailyOfficeAPIClient, 'get_morning_prayer')
    def test_complete_workflow_christmas(self, mock_api):
        """Test complete workflow for Christmas."""
        sample_data = self.load_sample('morning_prayer_2025-12-25.json')
        mock_api.return_value = sample_data

        service = PrayerService()
        markdown = service.generate_morning_prayer_markdown(date(2025, 12, 25))

        # Should include Christmas-specific content
        self.assertIn('Christmas', markdown)
        self.assertIn('December 25, 2025', markdown)

        service.close()

    @patch.object(DailyOfficeAPIClient, 'get_morning_prayer')
    def test_complete_workflow_easter(self, mock_api):
        """Test complete workflow for Easter."""
        sample_data = self.load_sample('morning_prayer_2025-04-20.json')
        mock_api.return_value = sample_data

        service = PrayerService()
        markdown = service.generate_morning_prayer_markdown(date(2025, 4, 20))

        # Should include Easter-specific content
        self.assertIn('Easter', markdown)
        self.assertIn('April 20, 2025', markdown)

        service.close()

    @patch.object(DailyOfficeAPIClient, 'get_morning_prayer')
    def test_complete_workflow_ash_wednesday(self, mock_api):
        """Test complete workflow for Ash Wednesday."""
        sample_data = self.load_sample('morning_prayer_2025-03-05.json')
        mock_api.return_value = sample_data

        service = PrayerService()
        markdown = service.generate_morning_prayer_markdown(date(2025, 3, 5))

        # Should include Ash Wednesday content
        self.assertIn('March 5, 2025', markdown)

        service.close()


class TestRealDataIntegration(unittest.TestCase):
    """Test integration with all real sample data files."""

    @classmethod
    def setUpClass(cls):
        """Load all sample files."""
        cls.samples_dir = Path(__file__).parent.parent / 'api_samples'
        cls.office_dir = cls.samples_dir / 'office'

    def test_all_morning_prayer_samples(self):
        """Test that all morning prayer samples can be processed."""
        morning_prayer_files = [
            f for f in self.office_dir.glob('morning_prayer_*.json')
        ]

        self.assertGreater(len(morning_prayer_files), 0)

        generator = MarkdownGenerator()

        for sample_file in morning_prayer_files:
            with self.subTest(file=sample_file.name):
                with open(sample_file, 'r') as f:
                    data = json.load(f)

                # Should not raise an error
                markdown = generator.generate_morning_prayer(data)

                # Should produce valid output
                self.assertIsInstance(markdown, str)
                self.assertGreater(len(markdown), 100)
                self.assertIn('# Daily Morning Prayer', markdown)

    def test_all_evening_prayer_samples(self):
        """Test that all evening prayer samples have correct structure."""
        evening_prayer_files = [
            f for f in self.office_dir.glob('evening_prayer_*.json')
        ]

        self.assertGreater(len(evening_prayer_files), 0)

        for sample_file in evening_prayer_files:
            with self.subTest(file=sample_file.name):
                with open(sample_file, 'r') as f:
                    data = json.load(f)

                # Check structure
                self.assertIn('modules', data)
                self.assertIn('calendar_day', data)

    def test_all_compline_samples(self):
        """Test that all compline samples have correct structure."""
        compline_files = [
            f for f in self.office_dir.glob('compline_*.json')
        ]

        self.assertGreater(len(compline_files), 0)

        for sample_file in compline_files:
            with self.subTest(file=sample_file.name):
                with open(sample_file, 'r') as f:
                    data = json.load(f)

                # Check structure
                self.assertIn('modules', data)
                self.assertIn('calendar_day', data)


if __name__ == '__main__':
    unittest.main()
