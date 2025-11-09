"""
Markdown Generator for Daily Office Prayer

This module converts API responses from the Daily Office 2019 API
into well-formatted Markdown documents and PDFs.
"""

import re
from typing import Dict, Any, List, Optional
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

    def generate_prayer(self, api_response: Dict[str, Any], title: str = "Daily Office") -> str:
        """
        Generate a complete prayer Markdown document.

        Args:
            api_response: The raw API response dictionary containing modules and calendar data
            title: The title for the prayer document

        Returns:
            A formatted Markdown string containing the complete prayer liturgy
        """
        sections = []

        # Add title and date
        calendar_day = api_response.get('calendar_day', {})
        date_desc = calendar_day.get('date_description', {})

        sections.append(f"# {title}")
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

    def generate_morning_prayer(self, api_response: Dict[str, Any]) -> str:
        """
        Generate a complete morning prayer Markdown document.

        Args:
            api_response: The raw API response dictionary containing modules and calendar data

        Returns:
            A formatted Markdown string containing the complete morning prayer liturgy
        """
        return self.generate_prayer(api_response, "Daily Morning Prayer")

    def generate_evening_prayer(self, api_response: Dict[str, Any]) -> str:
        """
        Generate a complete evening prayer Markdown document.

        Args:
            api_response: The raw API response dictionary containing modules and calendar data

        Returns:
            A formatted Markdown string containing the complete evening prayer liturgy
        """
        return self.generate_prayer(api_response, "Daily Evening Prayer")

    def generate_midday_prayer(self, api_response: Dict[str, Any]) -> str:
        """
        Generate a complete midday prayer Markdown document.

        Args:
            api_response: The raw API response dictionary containing modules and calendar data

        Returns:
            A formatted Markdown string containing the complete midday prayer liturgy
        """
        return self.generate_prayer(api_response, "Midday Prayer")

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

        # Module heading - only add if not duplicated in first line
        if module_name:
            # Check if first line is a heading with same content
            first_line = lines[0] if lines else {}
            if not (first_line.get('line_type') == 'heading' and
                    first_line.get('content', '').strip() == module_name):
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
            # Leader/officiant lines in normal text (no label)
            # Escape trailing asterisks (psalm pause markers) so they don't break markdown
            content = re.sub(r'(\*+)\s*$', r'\\\1', content).rstrip()
            # Add verse number if preface is a number (for psalms)
            if preface and isinstance(preface, (int, str)) and str(preface).isdigit():
                content = f"<sup>{preface}</sup> {content}"
            return self._indent_text(content, indented)

        elif line_type in ['congregation', 'congregation_dialogue']:
            # Congregation/people lines in bold (no label)
            # Escape trailing asterisks (psalm pause markers) so they don't break markdown
            content = re.sub(r'(\*+)\s*$', r'\\\1', content).rstrip()
            # Add verse number if preface is a number (for psalms)
            if preface and isinstance(preface, (int, str)) and str(preface).isdigit():
                content = f"<sup>{preface}</sup> {content}"
            return self._indent_text(f"**{content}**", indented)

        elif line_type == 'reader':
            # Reader lines in normal text (no label)
            return self._indent_text(content, indented)

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
        Extract and format text from HTML scripture readings and psalms.

        For psalms, preserves the responsive reading format:
        - Hanging indent (officiant) lines: normal text
        - Indented (people) lines: bold text

        Args:
            html_content: HTML content from scripture readings or psalms

        Returns:
            Cleaned, formatted text
        """
        # Remove script tags and their content
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)

        # Check if this is psalm content (has psalm-specific classes)
        is_psalm = 'class=\'psalm\'' in html_content or 'class="psalm"' in html_content

        if is_psalm:
            # Handle psalm formatting specially
            lines = []

            # Extract paragraphs
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)

            for para in paragraphs:
                # Extract verse numbers and preserve them as <sup> tags
                verse_num = ''
                verse_match = re.search(r'<sup[^>]*>(\d+)</sup>', para)
                if verse_match:
                    verse_num = f'<sup>{verse_match.group(1)}</sup> '
                    # Remove the sup tag from para so number doesn't appear twice
                    para = re.sub(r'<sup[^>]*>\d+</sup>\s*', '', para)

                # Remove asterisk spans
                para = re.sub(r'<span class=["\']asterisk["\']>\*</span>', '', para)

                # Check if this is a strong/bold line (people's response)
                has_strong = '<strong>' in para

                # Remove all HTML tags but preserve content
                text = re.sub(r'<[^>]+>', '', para)
                text = unescape(text)

                # Escape trailing asterisks (psalm pause markers) so they don't break markdown
                text = re.sub(r'(\*+)\s*$', r'\\\1', text).rstrip()

                if text:
                    # If has strong tags, make the whole line bold
                    if has_strong:
                        lines.append(f"  {verse_num}**{text}**")
                    else:
                        lines.append(f"{verse_num}{text}")

            return '\n'.join(lines)

        else:
            # Regular scripture reading - format as blockquote
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

    def save_to_pdf(self, markdown_content: str, filename: str):
        """
        Save the generated Markdown to a PDF file.

        Args:
            markdown_content: The Markdown content to convert to PDF
            filename: The output filename (should end in .pdf)

        Raises:
            ImportError: If required PDF generation libraries are not installed
        """
        try:
            import markdown
            from weasyprint import HTML, CSS
        except ImportError as e:
            raise ImportError(
                "PDF generation requires 'markdown' and 'weasyprint' packages. "
                "Install them with: pip install markdown weasyprint"
            ) from e

        # Convert markdown to HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['extra', 'nl2br', 'sane_lists']
        )

        # Add CSS styling for better PDF appearance
        css = CSS(string='''
            @page {
                size: Letter;
                margin: 1in;
            }
            body {
                font-family: "Times New Roman", Times, serif;
                font-size: 12pt;
                line-height: 1.6;
                color: #000;
            }
            h1 {
                font-size: 24pt;
                text-align: center;
                margin-bottom: 0.5em;
            }
            h2 {
                font-size: 18pt;
                text-align: center;
                margin-top: 0;
                margin-bottom: 1em;
            }
            h3 {
                font-size: 14pt;
                margin-top: 1.5em;
                margin-bottom: 0.5em;
            }
            em {
                font-style: italic;
                color: #666;
            }
            strong {
                font-weight: bold;
            }
            blockquote {
                margin-left: 2em;
                font-style: italic;
            }
            hr {
                border: none;
                border-top: 1px solid #000;
                margin: 1.5em 0;
            }
        ''')

        # Create full HTML document
        full_html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Daily Office Prayer</title>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        '''

        # Generate PDF
        HTML(string=full_html).write_pdf(filename, stylesheets=[css])
