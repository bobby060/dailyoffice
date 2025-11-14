"""
Unit tests for LaTeX Generator

Tests the LaTeX generation using real API sample data.
"""

import unittest
import json
from pathlib import Path

from dailyoffice.latex_prayer_generator import LatexGenerator


class TestLatexGenerator(unittest.TestCase):
    """Test suite for LatexGenerator."""

    @classmethod
    def setUpClass(cls):
        """Load sample data for testing."""
        cls.samples_dir = Path(__file__).parent.parent / 'api_samples'
        cls.office_dir = cls.samples_dir / 'office'

    def setUp(self):
        """Set up each test."""
        self.generator = LatexGenerator()

    def load_sample(self, filename):
        """Helper to load a sample JSON file."""
        with open(self.office_dir / filename, 'r') as f:
            return json.load(f)

    def test_generator_initialization(self):
        """Test generator initializes correctly."""
        self.assertIsInstance(self.generator, LatexGenerator)

    def test_generate_morning_prayer_basic(self):
        """Test basic morning prayer generation."""
        data = self.load_sample('morning_prayer_2025-11-08.json')
        latex = self.generator.generate_morning_prayer(data)

        # Should return a string
        self.assertIsInstance(latex, str)
        self.assertGreater(len(latex), 100)

        # Should contain key LaTeX elements
        self.assertIn(r'\documentclass', latex)
        self.assertIn(r'\begin{document}', latex)
        self.assertIn(r'\end{document}', latex)
        self.assertIn('Daily Morning Prayer', latex)

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
                latex = self.generator.generate_morning_prayer(data)

                self.assertIsInstance(latex, str)
                self.assertGreater(len(latex), 100)
                self.assertIn(r'\documentclass', latex)

    def test_escape_latex(self):
        """Test LaTeX special character escaping."""
        # Test basic special characters
        text = "Test & % $ # _ { } ~ ^"
        escaped = self.generator._escape_latex(text)

        self.assertIn(r'\&', escaped)
        self.assertIn(r'\%', escaped)
        self.assertIn(r'\$', escaped)
        self.assertIn(r'\#', escaped)
        self.assertIn(r'\_', escaped)
        self.assertIn(r'\{', escaped)
        self.assertIn(r'\}', escaped)

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

    def test_format_liturgical_info_latex(self):
        """Test liturgical information formatting for LaTeX."""
        calendar_day = {
            'primary_feast': 'Saturday after the Twenty-first Sunday after Pentecost',
            'season': {
                'name': 'Season After Pentecost',
                'colors': ['green']
            }
        }

        result = self.generator._format_liturgical_info_latex(calendar_day)

        self.assertIn(r'\textbf{', result)
        self.assertIn('Saturday after the Twenty-first Sunday after Pentecost', result)
        self.assertIn('Season After Pentecost', result)

    def test_format_line_latex_heading(self):
        """Test heading line formatting for LaTeX."""
        line = {
            'content': 'Opening Sentence',
            'line_type': 'heading',
            'indented': False
        }

        result = self.generator._format_line_latex(line)
        self.assertIn(r'\subsubsection*{', result)
        self.assertIn('Opening Sentence', result)

    def test_format_line_latex_rubric(self):
        """Test rubric line formatting for LaTeX."""
        line = {
            'content': 'The Officiant says to the People',
            'line_type': 'rubric',
            'indented': False
        }

        result = self.generator._format_line_latex(line)
        self.assertIn(r'\textit{', result)

    def test_format_line_latex_leader(self):
        """Test leader line formatting for LaTeX."""
        line = {
            'content': 'O Lord, open our lips;',
            'line_type': 'leader',
            'indented': False
        }

        result = self.generator._format_line_latex(line)
        # Should not have label
        self.assertNotIn('Officiant', result)
        # Should have backslash for line break
        self.assertIn(r'\\', result)

    def test_format_line_latex_congregation(self):
        """Test congregation line formatting for LaTeX."""
        line = {
            'content': 'And our mouth shall proclaim your praise.',
            'line_type': 'congregation',
            'indented': False
        }

        result = self.generator._format_line_latex(line)
        # Should be bold
        self.assertIn(r'\textbf{', result)
        # Should not have label
        self.assertNotIn('People', result)

    def test_format_line_latex_dialogue(self):
        """Test dialogue line formatting for LaTeX."""
        leader_line = {
            'content': 'The Lord be with you.',
            'line_type': 'leader_dialogue',
            'indented': False
        }

        result = self.generator._format_line_latex(leader_line)
        # Should have Officiant label for dialogue
        self.assertIn('Officiant', result)

    def test_indent_text_latex(self):
        """Test LaTeX text indentation."""
        text = "Some text"

        # No indent
        result = self.generator._indent_text_latex(text, False)
        self.assertEqual(result, text)

        # With indent
        result = self.generator._indent_text_latex(text, 'indent')
        self.assertIn(r'\leftskip', result)
        self.assertIn('Some text', result)

    def test_page_size_letter(self):
        """Test LaTeX generation with letter page size."""
        data = self.load_sample('morning_prayer_2025-11-08.json')
        latex = self.generator.generate_morning_prayer(data, page_size='letter')

        self.assertIn('letterpaper', latex)

    def test_page_size_remarkable(self):
        """Test LaTeX generation with remarkable page size."""
        data = self.load_sample('morning_prayer_2025-11-08.json')
        latex = self.generator.generate_morning_prayer(data, page_size='remarkable')

        self.assertIn('6.18in', latex)
        self.assertIn('8.24in', latex)

    def test_generate_with_label(self):
        """Test LaTeX generation with hyperlink label."""
        data = self.load_sample('morning_prayer_2025-11-08.json')
        latex = self.generator.generate_morning_prayer(data, label='day1')

        self.assertIn(r'\label{day1}', latex)

    def test_save_to_latex(self, tmp_path=None):
        """Test saving LaTeX to file."""
        if tmp_path is None:
            import tempfile
            tmp_path = Path(tempfile.mkdtemp())

        latex = r'\documentclass{article}\begin{document}Test\end{document}'
        output_file = tmp_path / "test_output.tex"

        self.generator.save_to_latex(latex, str(output_file))

        # File should exist
        self.assertTrue(output_file.exists())

        # Content should match
        with open(output_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, latex)

    def test_evening_prayer_generation(self):
        """Test evening prayer generation."""
        data = self.load_sample('evening_prayer_2025-11-08.json')
        latex = self.generator.generate_evening_prayer(data)

        self.assertIn('Daily Evening Prayer', latex)
        self.assertIn(r'\documentclass', latex)

    def test_midday_prayer_generation(self):
        """Test midday prayer generation."""
        data = self.load_sample('midday_prayer_2025-11-08.json')
        latex = self.generator.generate_midday_prayer(data)

        self.assertIn('Midday Prayer', latex)
        self.assertIn(r'\documentclass', latex)

    def test_compline_generation(self):
        """Test compline generation."""
        data = self.load_sample('compline_2025-11-08.json')
        latex = self.generator.generate_compline(data)

        self.assertIn('Compline', latex)
        self.assertIn(r'\documentclass', latex)


class TestLatexOutput(unittest.TestCase):
    """Test the quality and structure of LaTeX output."""

    @classmethod
    def setUpClass(cls):
        """Load sample data."""
        cls.samples_dir = Path(__file__).parent.parent / 'api_samples'
        cls.office_dir = cls.samples_dir / 'office'

    def setUp(self):
        """Set up each test."""
        self.generator = LatexGenerator()

    def load_sample(self, filename):
        """Helper to load a sample JSON file."""
        with open(self.office_dir / filename, 'r') as f:
            return json.load(f)

    def test_valid_latex_structure(self):
        """Test that output has valid LaTeX structure."""
        data = self.load_sample('morning_prayer_2025-11-08.json')
        latex = self.generator.generate_morning_prayer(data)

        # Should have preamble
        self.assertIn(r'\documentclass', latex)
        self.assertIn(r'\usepackage', latex)

        # Should have document environment
        self.assertIn(r'\begin{document}', latex)
        self.assertIn(r'\end{document}', latex)

        # Document should come after preamble
        begin_pos = latex.find(r'\begin{document}')
        class_pos = latex.find(r'\documentclass')
        self.assertGreater(begin_pos, class_pos)

    def test_no_unescaped_special_chars(self):
        """Test that special characters are properly escaped."""
        data = self.load_sample('morning_prayer_2025-11-08.json')
        latex = self.generator.generate_morning_prayer(data)

        # Extract content between \begin{document} and \end{document}
        begin_doc = latex.find(r'\begin{document}')
        end_doc = latex.find(r'\end{document}')
        content = latex[begin_doc:end_doc]

        # Count unescaped special chars (outside of LaTeX commands)
        # This is a basic check - more sophisticated parsing would be needed for completeness
        # For now, just check that we have escaped versions
        if '&' in content:
            self.assertIn(r'\&', content)
        if '%' in content:
            self.assertIn(r'\%', content)


if __name__ == '__main__':
    unittest.main()
