"""
Markdown Generator for Daily Office Prayer

This module converts API responses from the Daily Office 2019 API
into well-formatted Markdown documents.
"""

import re
from typing import Dict, Any, List
from html import unescape
from datetime import date


class MarkdownGenerator:
    """
    Generates formatted Markdown documents from Daily Office API responses.

    This class handles the conversion of liturgical content including headings,
    prayers, psalms, Scripture readings, and rubrics into readable Markdown format.
    """

    def __init__(self):
        """Initialize the Markdown generator."""
        pass

    def generate_morning_prayer(self, api_response: Dict[str, Any]) -> str:
        """
        Generate a complete morning prayer Markdown document.

        Args:
            api_response: The raw API response dictionary containing modules and calendar data

        Returns:
            A formatted Markdown string containing the complete morning prayer liturgy
        """
        sections = []

        # Add title and date
        calendar_day = api_response.get('calendar_day', {})
        date_desc = calendar_day.get('date_description', {})

        sections.append("# Daily Morning Prayer")
        sections.append(f"## {self._format_date(date_desc)}")
        sections.append("")

        # Add liturgical information
        sections.append(self._format_liturgical_info(calendar_day))
        sections.append("")
        sections.append("---")
        sections.append("")

        # Process each module
        modules = api_response.get('modules', [])
        for module in modules:
            module_md = self._format_module(module)
            if module_md:
                sections.append(module_md)
                sections.append("")

        return "\n".join(sections)

    def _format_date(self, date_desc: Dict[str, Any]) -> str:
        """Format the date description."""
        weekday = date_desc.get('weekday', '')
        month_name = date_desc.get('month_name', '')
        day = date_desc.get('day', '')
        year = date_desc.get('year', '')

        if all([weekday, month_name, day, year]):
            return f"{weekday}, {month_name} {day}, {year}"
        return "Daily Morning Prayer"

    def _format_liturgical_info(self, calendar_day: Dict[str, Any]) -> str:
        """Format liturgical season and feast information."""
        lines = []

        # Primary feast
        primary_feast = calendar_day.get('primary_feast', '')
        if primary_feast:
            lines.append(f"**{primary_feast}**")

        # Season
        season = calendar_day.get('season', {})
        season_name = season.get('name', '')
        colors = season.get('colors', [])
        if season_name:
            color_str = f" ({', '.join(colors)})" if colors else ""
            lines.append(f"*{season_name}{color_str}*")

        return "\n".join(lines) if lines else ""

    def _format_module(self, module: Dict[str, Any]) -> str:
        """
        Format a single module (section) of the prayer.

        Args:
            module: A module dictionary containing 'name' and 'lines'

        Returns:
            Formatted Markdown for the module
        """
        module_name = module.get('name', '')
        lines = module.get('lines', [])

        if not lines:
            return ""

        output = []

        # Module heading
        if module_name:
            output.append(f"## {module_name}")
            output.append("")

        # Process each line
        for line in lines:
            formatted_line = self._format_line(line)
            if formatted_line is not None:
                output.append(formatted_line)

        return "\n".join(output)

    def _format_line(self, line: Dict[str, Any]) -> str:
        """
        Format a single line from the liturgy.

        Args:
            line: A line dictionary containing 'content', 'line_type', and formatting info

        Returns:
            Formatted Markdown string for the line, or None if the line should be skipped
        """
        content = line.get('content', '').strip()
        line_type = line.get('line_type', '')
        indented = line.get('indented', False)
        preface = line.get('preface')

        # Skip empty spacer lines (we'll handle spacing differently)
        if line_type == 'spacer' or not content:
            return ""

        # Handle different line types
        if line_type == 'heading':
            return f"### {content}"

        elif line_type == 'subheading':
            return f"*{content}*"

        elif line_type == 'rubric':
            return f"*{content}*"

        elif line_type == 'citation':
            return f"— {content}"

        elif line_type in ['leader', 'leader_dialogue']:
            prefix = f"**{preface}:** " if preface else "**Officiant:** "
            return self._indent_text(f"{prefix}{content}", indented)

        elif line_type in ['congregation', 'congregation_dialogue']:
            prefix = f"**{preface}:** " if preface else "**People:** "
            return self._indent_text(f"{prefix}{content}", indented)

        elif line_type == 'reader':
            return self._indent_text(f"**Reader:** {content}", indented)

        elif line_type == 'html':
            # Strip HTML and extract clean text
            return self._format_html_content(content)

        else:
            # Default formatting for unknown types
            return self._indent_text(content, indented)

    def _indent_text(self, text: str, indented: Any) -> str:
        """
        Apply indentation to text based on the indented parameter.

        Args:
            text: The text to indent
            indented: Boolean, string, or other indicator of indentation

        Returns:
            Indented text
        """
        if not indented or indented == False:
            return text

        if indented in ['indent', 'hangingIndent', 'hangingIdent', True]:
            return f"  {text}"

        return text

    def _format_html_content(self, html_content: str) -> str:
        """
        Extract and format text from HTML scripture readings.

        Args:
            html_content: HTML content from scripture readings

        Returns:
            Cleaned, formatted text
        """
        # Remove script tags and their content
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)

        # Remove HTML tags but keep the text
        text = re.sub(r'<[^>]+>', ' ', html_content)

        # Clean up verse numbers - make them superscript-style in markdown
        text = re.sub(r'(\d+)\s+', r'<sup>\1</sup> ', text)

        # Unescape HTML entities
        text = unescape(text)

        # Clean up excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Format as blockquote for scripture
        lines = text.strip().split('\n')
        formatted_lines = [f"> {line.strip()}" if line.strip() else ">" for line in lines]

        return '\n'.join(formatted_lines)

    def save_to_file(self, markdown_content: str, filename: str):
        """
        Save the generated Markdown to a file.

        Args:
            markdown_content: The Markdown content to save
            filename: The output filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
