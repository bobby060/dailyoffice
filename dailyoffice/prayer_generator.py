"""
Markdown and LaTeX Generator for Daily Office Prayer

This module converts API responses from the Daily Office 2019 API
into well-formatted Markdown documents, LaTeX documents, and PDFs.
"""

import re
import os
import subprocess
import tempfile
from typing import Dict, Any, List, Optional
from html import unescape
from datetime import date
from pathlib import Path


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

    def generate_compline(self, api_response: Dict[str, Any]) -> str:
        """
        Generate a complete compline (night prayer) Markdown document.

        Args:
            api_response: The raw API response dictionary containing modules and calendar data

        Returns:
            A formatted Markdown string containing the complete compline liturgy
        """
        return self.generate_prayer(api_response, "Compline")

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
            # Regular scripture reading - format as normal text (not blockquote/italic)
            # Remove HTML tags but keep the text
            text = re.sub(r'<[^>]+>', ' ', html_content)

            # Clean up verse numbers - make them superscript-style in markdown
            text = re.sub(r'(\d+)\s+', r'<sup>\1</sup> ', text)

            # Unescape HTML entities
            text = unescape(text)

            # Clean up excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'\n\s*\n', '\n\n', text)

            # Return as normal text (no blockquote)
            return text.strip()

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

    # ===== LaTeX Generation Methods =====

    def _escape_latex(self, text: str) -> str:
        """
        Escape special LaTeX characters and handle Unicode issues.

        Args:
            text: Text to escape

        Returns:
            LaTeX-safe text
        """
        # First, handle Unicode small caps (used for LORD/God in liturgical texts)
        # Convert Unicode small caps to regular uppercase
        # Note: Only actual Unicode small cap characters, not regular ASCII
        small_caps_map = {
            'ᴀ': 'A', 'ʙ': 'B', 'ᴄ': 'C', 'ᴅ': 'D', 'ᴇ': 'E', 'ғ': 'F', 'ɢ': 'G', 'ʜ': 'H',
            'ɪ': 'I', 'ᴊ': 'J', 'ᴋ': 'K', 'ʟ': 'L', 'ᴍ': 'M', 'ɴ': 'N', 'ᴏ': 'O', 'ᴘ': 'P',
            'ǫ': 'Q', 'ʀ': 'R', 'ꜱ': 'S', 'ᴛ': 'T', 'ᴜ': 'U', 'ᴠ': 'V', 'ᴡ': 'W',
            'ʏ': 'Y', 'ᴢ': 'Z'
        }
        for small_cap, regular in small_caps_map.items():
            text = text.replace(small_cap, regular)

        # Mapping of special characters to their LaTeX escaped versions
        replacements = {
            '\\': r'\textbackslash{}',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }

        # First handle backslash, then others
        result = text.replace('\\', replacements['\\'])
        for char, replacement in replacements.items():
            if char != '\\':
                result = result.replace(char, replacement)

        return result

    def generate_latex(self, api_response: Dict[str, Any], title: str = "Daily Office", page_size: str = "letter") -> str:
        """
        Generate a complete prayer LaTeX document.

        Args:
            api_response: The raw API response dictionary containing modules and calendar data
            title: The title for the prayer document
            page_size: Page size - "letter" (8.5x11) or "remarkable" (6.18x8.24)

        Returns:
            A formatted LaTeX string containing the complete prayer liturgy
        """
        sections = []

        # LaTeX preamble - using only basic packages for maximum compatibility
        sections.append(r'\documentclass[12pt,letterpaper]{article}')
        sections.append(r'\usepackage[utf8]{inputenc}')
        sections.append(r'\usepackage[T1]{fontenc}')
        sections.append(r'\usepackage{geometry}')

        # Set page size based on option
        if page_size == "remarkable":
            # Remarkable 2 tablet size: 6.18 x 8.24 inches (157mm x 209mm)
            sections.append(r'\geometry{paperwidth=6.18in, paperheight=8.24in, margin=0.5in}')
        else:
            # Standard US Letter size
            sections.append(r'\geometry{letterpaper, margin=1in}')

        sections.append(r'')
        sections.append(r'% Paragraph formatting')
        sections.append(r'\setlength{\parindent}{0pt}')
        sections.append(r'\setlength{\parskip}{0.5em}')
        sections.append(r'')
        sections.append(r'% Custom section formatting (centered, no numbering)')
        sections.append(r'\makeatletter')
        sections.append(r'\renewcommand\section{\@startsection{section}{1}{\z@}%')
        sections.append(r'  {-3.5ex \@plus -1ex \@minus -.2ex}%')
        sections.append(r'  {2.3ex \@plus.2ex}%')
        sections.append(r'  {\centering\normalfont\Large\bfseries}}')
        sections.append(r'\renewcommand\subsection{\@startsection{subsection}{2}{\z@}%')
        sections.append(r'  {-3.25ex\@plus -1ex \@minus -.2ex}%')
        sections.append(r'  {1.5ex \@plus .2ex}%')
        sections.append(r'  {\centering\normalfont\large\bfseries}}')
        sections.append(r'\renewcommand\subsubsection{\@startsection{subsubsection}{3}{\z@}%')
        sections.append(r'  {-3.25ex\@plus -1ex \@minus -.2ex}%')
        sections.append(r'  {1.5ex \@plus .2ex}%')
        sections.append(r'  {\normalfont\normalsize\bfseries}}')
        sections.append(r'\makeatother')
        sections.append(r'')
        sections.append(r'\begin{document}')
        sections.append(r'')

        # Add title and date
        calendar_day = api_response.get('calendar_day', {})
        date_desc = calendar_day.get('date_description', {})

        sections.append(r'\begin{center}')
        sections.append(r'{\LARGE \textbf{' + self._escape_latex(title) + r'}}\\[0.5em]')
        sections.append(r'{\large ' + self._escape_latex(self._format_date(date_desc)) + r'}')
        sections.append(r'\end{center}')
        sections.append(r'')

        # Add liturgical information
        liturg_info = self._format_liturgical_info_latex(calendar_day)
        if liturg_info:
            sections.append(liturg_info)
            sections.append(r'')

        sections.append(r'\noindent\rule{\textwidth}{0.4pt}')
        sections.append(r'')

        # Process each module
        modules = api_response.get('modules', [])
        for module in modules:
            module_tex = self._format_module_latex(module)
            if module_tex:
                sections.append(module_tex)
                sections.append(r'')

        sections.append(r'\end{document}')

        return "\n".join(sections)

    def generate_morning_prayer_latex(self, api_response: Dict[str, Any], page_size: str = "letter") -> str:
        """
        Generate a complete morning prayer LaTeX document.

        Args:
            api_response: The raw API response dictionary
            page_size: Page size - "letter" or "remarkable"

        Returns:
            A formatted LaTeX string containing the complete morning prayer liturgy
        """
        return self.generate_latex(api_response, "Daily Morning Prayer", page_size)

    def generate_evening_prayer_latex(self, api_response: Dict[str, Any], page_size: str = "letter") -> str:
        """
        Generate a complete evening prayer LaTeX document.

        Args:
            api_response: The raw API response dictionary
            page_size: Page size - "letter" or "remarkable"

        Returns:
            A formatted LaTeX string containing the complete evening prayer liturgy
        """
        return self.generate_latex(api_response, "Daily Evening Prayer", page_size)

    def generate_midday_prayer_latex(self, api_response: Dict[str, Any], page_size: str = "letter") -> str:
        """
        Generate a complete midday prayer LaTeX document.

        Args:
            api_response: The raw API response dictionary
            page_size: Page size - "letter" or "remarkable"

        Returns:
            A formatted LaTeX string containing the complete midday prayer liturgy
        """
        return self.generate_latex(api_response, "Midday Prayer", page_size)

    def generate_compline_latex(self, api_response: Dict[str, Any], page_size: str = "letter") -> str:
        """
        Generate a complete compline (night prayer) LaTeX document.

        Args:
            api_response: The raw API response dictionary
            page_size: Page size - "letter" or "remarkable"

        Returns:
            A formatted LaTeX string containing the complete compline liturgy
        """
        return self.generate_latex(api_response, "Compline", page_size)

    def _format_liturgical_info_latex(self, calendar_day: Dict[str, Any]) -> str:
        """Format liturgical season and feast information for LaTeX."""
        lines = []

        # Primary feast
        primary_feast = calendar_day.get('primary_feast', '')
        if primary_feast:
            lines.append(r'\begin{center}')
            lines.append(r'\textbf{' + self._escape_latex(primary_feast) + r'}')

        # Season
        season = calendar_day.get('season', {})
        season_name = season.get('name', '')
        colors = season.get('colors', [])
        if season_name:
            color_str = f" ({', '.join(colors)})" if colors else ""
            if not primary_feast:
                lines.append(r'\begin{center}')
            else:
                lines.append(r'\\')
            lines.append(r'\textit{' + self._escape_latex(season_name + color_str) + r'}')

        if lines:
            lines.append(r'\end{center}')

        return "\n".join(lines) if lines else ""

    def _format_module_latex(self, module: Dict[str, Any]) -> str:
        """
        Format a single module (section) of the prayer for LaTeX.

        Args:
            module: A module dictionary containing 'name' and 'lines'

        Returns:
            Formatted LaTeX for the module
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
                output.append(r'\subsection*{' + self._escape_latex(module_name) + r'}')
                output.append(r'')

        # Process each line
        # Track if the previous rubric should cause indentation
        indent_next_line = False
        for i, line in enumerate(lines):
            formatted_line = self._format_line_latex(line, indent_next_line)
            if formatted_line is not None:
                output.append(formatted_line)

            # Check if this rubric should cause the next line to be indented
            line_type = line.get('line_type', '')
            content = line.get('content', '').strip()
            if line_type == 'rubric' and content:
                # Rubrics that indicate someone is speaking should indent the next line
                content_lower = content.lower()
                indent_next_line = ('says' in content_lower or
                                   'say' in content_lower or
                                   'prays' in content_lower or
                                   'pray' in content_lower or
                                   'continues' in content_lower)
            elif line_type != 'spacer' and content:
                # Non-spacer content resets the flag
                indent_next_line = False

        return "\n".join(output)

    def _format_line_latex(self, line: Dict[str, Any], force_indent: bool = False) -> str:
        """
        Format a single line from the liturgy for LaTeX.

        Args:
            line: A line dictionary containing 'content', 'line_type', and formatting info
            force_indent: If True, force indentation regardless of the line's indented property

        Returns:
            Formatted LaTeX string for the line, or None if the line should be skipped
        """
        content = line.get('content', '').strip()
        line_type = line.get('line_type', '')
        indented = line.get('indented', False)
        preface = line.get('preface')

        # Apply forced indentation from rubric context
        if force_indent and not indented:
            indented = 'indent'

        # Skip empty spacer lines
        if line_type == 'spacer' or not content:
            return r''

        # Escape content for LaTeX
        escaped_content = self._escape_latex(content)

        # Handle different line types
        if line_type == 'heading':
            return r'\subsubsection*{' + escaped_content + r'}'

        elif line_type == 'subheading':
            # Centered subheading in italics
            return r'\centerline{\textit{' + escaped_content + r'}}'

        elif line_type == 'rubric':
            # Rubric with spacing before and after
            return r'\vspace{0.3em}\noindent\textit{' + escaped_content + r'}\\[0.3em]'

        elif line_type == 'citation':
            return r'\hfill --- ' + escaped_content

        elif line_type == 'leader_dialogue':
            # Leader dialogue: Officiant label aligned with People label using fixed-width box
            content_clean = content.rstrip()
            escaped_content = self._escape_latex(content_clean)
            # Use makebox to create fixed-width label so content aligns with People lines
            return r'\makebox[4em][l]{\textit{Officiant}}' + escaped_content + r'\\[0.5em]'

        elif line_type == 'leader':
            # Leader/officiant lines in normal text (non-dialogue)
            # Keep trailing asterisks (psalm pause markers) but escape them
            content_clean = content.rstrip()
            escaped_content = self._escape_latex(content_clean)
            # Add verse number if preface is a number (for psalms)
            if preface and isinstance(preface, (int, str)) and str(preface).isdigit():
                escaped_content = r'\textsuperscript{' + str(preface) + r'} ' + escaped_content
            return self._indent_text_latex(escaped_content, indented) + r'\\'

        elif line_type == 'congregation_dialogue':
            # Congregation dialogue: People label aligned with Officiant label using fixed-width box
            content_clean = content.rstrip()
            escaped_content = self._escape_latex(content_clean)
            # Use makebox to create fixed-width label so content aligns with Officiant lines
            return r'\makebox[4em][l]{\textit{People}}\textbf{' + escaped_content + r'}\\[0.5em]'

        elif line_type == 'congregation':
            # Congregation/people lines in bold (non-dialogue)
            # Keep trailing asterisks (psalm pause markers) but escape them
            content_clean = content.rstrip()
            escaped_content = self._escape_latex(content_clean)
            # Add verse number if preface is a number (for psalms)
            if preface and isinstance(preface, (int, str)) and str(preface).isdigit():
                escaped_content = r'\textsuperscript{' + str(preface) + r'} ' + escaped_content
            return self._indent_text_latex(r'\textbf{' + escaped_content + r'}', indented) + r'\\'

        elif line_type == 'reader':
            # Reader lines in normal text
            return self._indent_text_latex(escaped_content, indented) + r'\\'

        elif line_type == 'html':
            # Process HTML content (psalms, scripture) - these handle their own formatting
            return self._format_html_content_latex(content)

        else:
            # Default formatting for unknown types
            return self._indent_text_latex(escaped_content, indented) + r'\\'

    def _indent_text_latex(self, text: str, indented: Any) -> str:
        """
        Apply indentation to text for LaTeX based on the indented parameter.
        Uses hanging indent so wrapped lines maintain the indentation.

        Args:
            text: The text to indent (should already be escaped)
            indented: Boolean, string, or other indicator of indentation

        Returns:
            Indented text with hanging indent commands
        """
        if not indented or indented == False:
            return text

        if indented in ['indent', 'hangingIndent', 'hangingIdent', True]:
            # Use hanging indent: first line indents 2em, subsequent lines also indent 2em
            return r'{\setlength{\leftskip}{2em}\setlength{\parindent}{0em}' + text + r'}'

        return text

    def _format_html_content_latex(self, html_content: str) -> str:
        """
        Extract and format text from HTML scripture readings and psalms for LaTeX.

        Args:
            html_content: HTML content from scripture readings or psalms

        Returns:
            Cleaned, formatted LaTeX text
        """
        # Remove script tags and their content
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)

        # Check if this is psalm content
        is_psalm = 'class=\'psalm\'' in html_content or 'class="psalm"' in html_content

        if is_psalm:
            # Handle psalm formatting specially
            lines = []

            # Extract paragraphs
            paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', html_content, re.DOTALL)

            for para in paragraphs:
                # Extract verse numbers and preserve them as superscripts
                verse_num = ''
                verse_match = re.search(r'<sup[^>]*>(\d+)</sup>', para)
                if verse_match:
                    verse_num = r'\textsuperscript{' + verse_match.group(1) + r'} '
                    # Remove the sup tag from para
                    para = re.sub(r'<sup[^>]*>\d+</sup>\s*', '', para)

                # Keep asterisks but remove the span tags around them
                para = re.sub(r'<span class=["\']asterisk["\']>(\*)</span>', r'\1', para)

                # Check if this is a strong/bold line (people's response)
                has_strong = '<strong>' in para

                # Remove all HTML tags but preserve content
                text = re.sub(r'<[^>]+>', '', para)
                text = unescape(text)

                # Keep trailing asterisks
                text = text.rstrip()

                # Escape for LaTeX
                text = self._escape_latex(text)

                if text:
                    # If has strong tags, make the whole line bold with hanging indent
                    if has_strong:
                        lines.append(r'{\setlength{\leftskip}{2em}\setlength{\parindent}{0em}' + verse_num + r'\textbf{' + text + r'}}')
                    else:
                        lines.append(verse_num + text)

            return '\n\n'.join(lines)

        else:
            # Regular scripture reading - format as quote environment
            # Remove HTML tags but keep the text
            text = re.sub(r'<[^>]+>', ' ', html_content)

            # Unescape HTML entities
            text = unescape(text)

            # Clean up excessive whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()

            # Escape for LaTeX FIRST (before adding LaTeX commands)
            text = self._escape_latex(text)

            # Now add verse numbers as superscripts (after escaping, so they don't get escaped)
            text = re.sub(r'(\d+)\s+', lambda m: r'\textsuperscript{' + m.group(1) + r'} ', text)

            # Format as quote environment for scripture (no italic - use normal text)
            return r'\begin{quote}' + '\n' + text + '\n' + r'\end{quote}'

    def save_to_latex(self, latex_content: str, filename: str):
        """
        Save the generated LaTeX to a file.

        Args:
            latex_content: The LaTeX content to save
            filename: The output filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(latex_content)

    def compile_latex_to_pdf(self, latex_content: str, output_pdf: str, save_tex: bool = False, tex_filename: str = None):
        """
        Compile LaTeX content to PDF using pdflatex.

        Args:
            latex_content: The LaTeX content to compile
            output_pdf: The output PDF filename
            save_tex: Whether to save the .tex file
            tex_filename: Custom .tex filename (if save_tex is True)

        Raises:
            RuntimeError: If pdflatex is not available or compilation fails
        """
        # Check if pdflatex is available
        try:
            subprocess.run(['pdflatex', '--version'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "pdflatex is not available. Please install a LaTeX distribution:\n"
                "  - Ubuntu/Debian: sudo apt-get install texlive-latex-base\n"
                "  - macOS: brew install --cask mactex-no-gui\n"
                "  - Windows: Install MiKTeX or TeX Live"
            )

        # Determine if we should save the .tex file
        if save_tex:
            if tex_filename:
                tex_file = tex_filename
            else:
                # Generate .tex filename from PDF filename
                tex_file = str(Path(output_pdf).with_suffix('.tex'))
            self.save_to_latex(latex_content, tex_file)
            tex_path = Path(tex_file).resolve()
            temp_dir = tex_path.parent
            tex_basename = tex_path.stem
        else:
            # Use a temporary directory and file
            temp_dir = Path(tempfile.mkdtemp())
            tex_basename = 'prayer'
            tex_file = temp_dir / f'{tex_basename}.tex'
            self.save_to_latex(latex_content, str(tex_file))

        try:
            # Run pdflatex twice for proper formatting (TOC, references, etc.)
            for run in range(2):
                result = subprocess.run(
                    ['pdflatex', '-interaction=nonstopmode', f'{tex_basename}.tex'],
                    cwd=str(temp_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if result.returncode != 0:
                    # pdflatex failed
                    error_log = result.stdout + result.stderr

                    # Check for common missing package errors
                    missing_package = None
                    if 'pdftexcmds.sty' in error_log or 'hyperref' in error_log:
                        missing_package = 'hyperref/pdftexcmds'
                    elif '.sty' in error_log and 'not found' in error_log.lower():
                        # Try to extract package name
                        import re
                        match = re.search(r"File `([^']+\.sty)' not found", error_log)
                        if match:
                            missing_package = match.group(1).replace('.sty', '')

                    if missing_package:
                        raise RuntimeError(
                            f"LaTeX compilation failed: Missing LaTeX package.\n\n"
                            f"It looks like you're missing the '{missing_package}' package.\n"
                            f"Please install additional LaTeX packages:\n\n"
                            f"Ubuntu/Debian:\n"
                            f"  sudo apt-get install texlive-latex-extra\n\n"
                            f"macOS:\n"
                            f"  brew install --cask mactex\n\n"
                            f"Windows:\n"
                            f"  Install the full MiKTeX or TeX Live distribution\n\n"
                            f"Full error log:\n{error_log}"
                        )
                    else:
                        raise RuntimeError(f"LaTeX compilation failed:\n{error_log}")

            # Move the generated PDF to the desired location
            generated_pdf = temp_dir / f'{tex_basename}.pdf'
            if not generated_pdf.exists():
                raise RuntimeError("PDF was not generated by pdflatex")

            # Copy to output location
            output_path = Path(output_pdf).resolve()
            generated_pdf.replace(output_path)

        finally:
            # Clean up temporary files if not saving .tex
            if not save_tex:
                # Remove temporary directory and all its contents
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
