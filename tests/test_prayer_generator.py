"""
Unit tests for Markdown Generator

Tests the markdown generation using real API sample data.
"""

import unittest
import json
from pathlib import Path

from dailyoffice.markdown_prayer_generator import MarkdownGenerator


class TestMarkdownGenerator(unittest.TestCase):
    """Test suite for MarkdownGenerator."""

    @classmethod
    def setUpClass(cls):
        """Load sample data for testing."""
        cls.samples_dir = Path(__file__).parent.parent / 'api_samples'
        cls.office_dir = cls.samples_dir / 'office'

    def setUp(self):
        """Set up each test."""
        self.generator = MarkdownGenerator()

    def load_sample(self, filename):
        """Helper to load a sample JSON file."""
        with open(self.office_dir / filename, 'r') as f:
            return json.load(f)

    def test_generator_initialization(self):
        """Test generator initializes correctly."""
        self.assertIsInstance(self.generator, MarkdownGenerator)

    def test_generate_morning_prayer_basic(self):
        """Test basic morning prayer generation."""
        data = self.load_sample('morning_prayer_2025-11-08.json')
        markdown = self.generator.generate_morning_prayer(data)

        # Should return a string
        self.assertIsInstance(markdown, str)
        self.assertGreater(len(markdown), 100)

        # Should contain key elements
        self.assertIn('# Daily Morning Prayer', markdown)
        self.assertIn('Saturday, November 8, 2025', markdown)

    def test_generate_with_all_dates(self):
        """Test generation works for all sample dates."""
        files = [
            'morning_prayer_2025-03-05.json',  # Ash Wednesday
            'morning_prayer_2025-04-20.json',  # Easter
            'morning_prayer_2025-11-08.json',  # Regular
            'morning_prayer_2025-11-23.json',  # Sunday
            'morning_prayer_2025-12-25.json',  # Christmas
        ]

        for filename in files:
            with self.subTest(file=filename):
                data = self.load_sample(filename)
                markdown = self.generator.generate_morning_prayer(data)

                self.assertIsInstance(markdown, str)
                self.assertGreater(len(markdown), 100)
                self.assertIn('# Daily Morning Prayer', markdown)

    def test_format_date(self):
        """Test date formatting."""
        date_desc = {
            'weekday': 'Saturday',
            'month_name': 'November',
            'day': '8',
            'year': '2025'
        }

        result = self.generator._format_date(date_desc)
        self.assertEqual(result, 'Saturday, November 8, 2025')

    def test_format_liturgical_info(self):
        """Test liturgical information formatting."""
        calendar_day = {
            'primary_feast': 'Saturday after the Twenty-first Sunday after Pentecost',
            'season': {
                'name': 'Season After Pentecost',
                'colors': ['green']
            }
        }

        result = self.generator._format_liturgical_info(calendar_day)

        self.assertIn('Saturday after the Twenty-first Sunday after Pentecost', result)
        self.assertIn('Season After Pentecost', result)
        self.assertIn('green', result)

    def test_format_line_heading(self):
        """Test heading line formatting."""
        line = {
            'content': 'Opening Sentence',
            'line_type': 'heading',
            'indented': False
        }

        result = self.generator._format_line(line)
        self.assertEqual(result, '### Opening Sentence')

    def test_format_line_subheading(self):
        """Test subheading line formatting."""
        line = {
            'content': 'Te Deum Laudamus',
            'line_type': 'subheading',
            'indented': False
        }

        result = self.generator._format_line(line)
        self.assertEqual(result, '*Te Deum Laudamus*')

    def test_format_line_rubric(self):
        """Test rubric line formatting."""
        line = {
            'content': 'The Officiant says to the People',
            'line_type': 'rubric',
            'indented': False
        }

        result = self.generator._format_line(line)
        self.assertEqual(result, '*The Officiant says to the People*')

    def test_format_line_leader(self):
        """Test leader line formatting."""
        line = {
            'content': 'O Lord, open our lips;',
            'line_type': 'leader',
            'indented': False
        }

        result = self.generator._format_line(line)
        # Leader lines should be plain text without labels
        self.assertEqual(result, 'O Lord, open our lips;')
        self.assertNotIn('Officiant:', result)

    def test_format_line_congregation(self):
        """Test congregation line formatting."""
        line = {
            'content': 'And our mouth shall proclaim your praise.',
            'line_type': 'congregation',
            'indented': False
        }

        result = self.generator._format_line(line)
        # Congregation lines should be bold without labels
        self.assertEqual(result, '**And our mouth shall proclaim your praise.**')
        self.assertNotIn('People:', result)

    def test_format_line_with_preface(self):
        """Test line formatting with custom preface."""
        line = {
            'content': 'The Lord be with you.',
            'line_type': 'leader_dialogue',
            'indented': False,
            'preface': 'Officiant'
        }

        result = self.generator._format_line(line)
        # Leader lines should be plain text without labels (preface is ignored)
        self.assertEqual(result, 'The Lord be with you.')
        self.assertNotIn('Officiant:', result)

    def test_format_line_citation(self):
        """Test citation line formatting."""
        line = {
            'content': 'JOHN 4:23',
            'line_type': 'citation',
            'indented': False
        }

        result = self.generator._format_line(line)
        self.assertEqual(result, '— JOHN 4:23')

    def test_format_line_spacer(self):
        """Test spacer line formatting."""
        line = {
            'content': '',
            'line_type': 'spacer',
            'indented': False
        }

        result = self.generator._format_line(line)
        self.assertEqual(result, '')

    def test_indent_text(self):
        """Test text indentation."""
        text = "Some text"

        # No indent
        result = self.generator._indent_text(text, False)
        self.assertEqual(result, text)

        # With indent
        result = self.generator._indent_text(text, 'indent')
        self.assertEqual(result, '  Some text')

    def test_format_html_content(self):
        """Test HTML content formatting (Scripture readings)."""
        html = '<p class="chapter-2"><span>Test verse 1</span></p>'

        result = self.generator._format_html_content(html)

        # HTML tags should be removed
        self.assertNotIn('<p', result)
        self.assertNotIn('<span', result)
        # Should contain the text content
        self.assertIn('Test verse', result)

    def test_save_to_file(self, tmp_path=None):
        """Test saving markdown to file."""
        if tmp_path is None:
            import tempfile
            tmp_path = Path(tempfile.mkdtemp())

        markdown = "# Test\n\nContent"
        output_file = tmp_path / "test_output.md"

        self.generator.save_to_file(markdown, str(output_file))

        # File should exist
        self.assertTrue(output_file.exists())

        # Content should match
        with open(output_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, markdown)

    def test_full_morning_prayer_contains_sections(self):
        """Test that generated morning prayer contains expected sections."""
        data = self.load_sample('morning_prayer_2025-11-08.json')
        markdown = self.generator.generate_morning_prayer(data)

        expected_sections = [
            '## Opening Sentence',
            '## Confession of Sin',
            '## The Preces',
            '## Psalms',
            '## The Apostles\' Creed',
            '## The Prayers',
        ]

        for section in expected_sections:
            with self.subTest(section=section):
                self.assertIn(section, markdown)

    def test_special_liturgical_days(self):
        """Test generation for special liturgical days."""
        # Christmas
        christmas_data = self.load_sample('morning_prayer_2025-12-25.json')
        christmas_md = self.generator.generate_morning_prayer(christmas_data)
        self.assertIn('Christmas', christmas_md)

        # Easter
        easter_data = self.load_sample('morning_prayer_2025-04-20.json')
        easter_md = self.generator.generate_morning_prayer(easter_data)
        self.assertIn('Easter', easter_md)

    def test_psalm_formatting(self):
        """Test that psalms are formatted correctly."""
        data = self.load_sample('morning_prayer_2025-11-08.json')
        markdown = self.generator.generate_morning_prayer(data)

        # Should contain psalm content
        self.assertIn('Psalm', markdown)


class TestMarkdownOutput(unittest.TestCase):
    """Test the quality and structure of markdown output."""

    @classmethod
    def setUpClass(cls):
        """Load sample data."""
        cls.samples_dir = Path(__file__).parent.parent / 'api_samples'
        cls.office_dir = cls.samples_dir / 'office'

    def setUp(self):
        """Set up each test."""
        self.generator = MarkdownGenerator()

    def load_sample(self, filename):
        """Helper to load a sample JSON file."""
        with open(self.office_dir / filename, 'r') as f:
            return json.load(f)

    def test_no_double_blank_lines(self):
        """Test that there are no excessive blank lines."""
        data = self.load_sample('morning_prayer_2025-11-08.json')
        markdown = self.generator.generate_morning_prayer(data)

        # Should not have triple newlines
        self.assertNotIn('\n\n\n\n', markdown)

    def test_proper_heading_hierarchy(self):
        """Test that headings use proper markdown hierarchy."""
        data = self.load_sample('morning_prayer_2025-11-08.json')
        markdown = self.generator.generate_morning_prayer(data)

        # Should have h1 (title)
        self.assertIn('# Daily Morning Prayer', markdown)

        # Should have h2 (date)
        self.assertIn('## ', markdown)

        # Should have h3 (sections)
        self.assertIn('### ', markdown)

    def test_markdown_valid_structure(self):
        """Test that output is valid markdown."""
        data = self.load_sample('morning_prayer_2025-11-08.json')
        markdown = self.generator.generate_morning_prayer(data)

        # Headings should be at start of line
        lines = markdown.split('\n')
        for line in lines:
            if line.startswith('#'):
                # Should be proper heading (# followed by space)
                self.assertTrue(
                    line.startswith('# ') or
                    line.startswith('## ') or
                    line.startswith('### ')
                )


if __name__ == '__main__':
    unittest.main()
