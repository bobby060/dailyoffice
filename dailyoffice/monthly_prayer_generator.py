"""
Monthly Prayer Generator

This module generates combined prayer documents for an entire month,
with a title page, index, and hyperlinked navigation.
"""

import calendar
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
import subprocess
import tempfile
import shutil

from .prayer_service import PrayerService


class MonthlyPrayerGenerator:
    """
    Generate combined monthly prayer documents.

    This class creates a comprehensive prayer document for an entire month,
    with features including:
    - Title page for the month
    - Index (table of contents) with hyperlinks to each day
    - Navigation links from each prayer back to the index
    - Navigation links on each page to the first page of that day's prayer
    """

    def __init__(self):
        """Initialize the monthly prayer generator."""
        self.prayer_service = PrayerService()

    def generate_monthly_latex(
        self,
        year: int,
        month: int,
        prayer_type: str = 'morning',
        page_size: str = 'letter',
        psalm_cycle: Optional[int] = None
    ) -> str:
        """
        Generate a complete monthly prayer document in LaTeX format.

        Args:
            year: The year (e.g., 2025)
            month: The month (1-12)
            prayer_type: Type of prayer ('morning', 'evening', 'midday', 'compline')
            page_size: Page size - "letter" or "remarkable"
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60.

        Returns:
            Complete LaTeX document as a string

        Raises:
            ValueError: If month is not 1-12 or prayer_type is invalid
            requests.RequestException: If API requests fail
        """
        if not 1 <= month <= 12:
            raise ValueError(f"Month must be 1-12, got {month}")

        if prayer_type not in ['morning', 'evening', 'midday', 'compline']:
            raise ValueError(f"Invalid prayer type: {prayer_type}")

        # Get the number of days in the month
        _, num_days = calendar.monthrange(year, month)

        # Generate LaTeX content for each day
        daily_latex_content = []
        month_name = calendar.month_name[month]

        psalm_info = f" ({psalm_cycle}-day psalm cycle)" if psalm_cycle else ""
        print(f"Generating {prayer_type} prayers for {month_name} {year}{psalm_info}...")

        for day in range(1, num_days + 1):
            prayer_date = date(year, month, day)
            print(f"  Fetching day {day}/{num_days}: {prayer_date.strftime('%B %d, %Y')}...")

            # Create label for this day
            day_label = f'day{day}'

            # Get the LaTeX content for this day
            if prayer_type == 'morning':
                latex = self.prayer_service.generate_morning_prayer_latex(
                    prayer_date=prayer_date,
                    page_size=page_size,
                    psalm_cycle=psalm_cycle,
                    label=day_label
                )
            elif prayer_type == 'evening':
                latex = self.prayer_service.generate_evening_prayer_latex(
                    prayer_date=prayer_date,
                    page_size=page_size,
                    psalm_cycle=psalm_cycle,
                    label=day_label
                )
            elif prayer_type == 'midday':
                latex = self.prayer_service.generate_midday_prayer_latex(
                    prayer_date=prayer_date,
                    page_size=page_size,
                    psalm_cycle=psalm_cycle,
                    label=day_label
                )
            elif prayer_type == 'compline':
                latex = self.prayer_service.generate_compline_latex(
                    prayer_date=prayer_date,
                    page_size=page_size,
                    psalm_cycle=psalm_cycle,
                    label=day_label
                )

            # Extract just the body content (between \begin{document} and \end{document})
            body_start = latex.find(r'\begin{document}')
            body_end = latex.find(r'\end{document}')

            if body_start != -1 and body_end != -1:
                # Extract content after \begin{document}
                body_content = latex[body_start + len(r'\begin{document}'):body_end].strip()
                daily_latex_content.append({
                    'day': day,
                    'date': prayer_date,
                    'content': body_content
                })

        print(f"Combining {len(daily_latex_content)} days into monthly document...")

        # Combine all content into a single document with title page and index
        combined_latex = self._build_monthly_document(
            year=year,
            month=month,
            prayer_type=prayer_type,
            page_size=page_size,
            daily_content=daily_latex_content
        )

        return combined_latex

    def _build_monthly_document(
        self,
        year: int,
        month: int,
        prayer_type: str,
        page_size: str,
        daily_content: List[Dict[str, Any]]
    ) -> str:
        """
        Build the combined monthly LaTeX document with title page and index.

        Args:
            year: The year
            month: The month (1-12)
            prayer_type: Type of prayer
            page_size: Page size
            daily_content: List of dicts with 'day', 'date', and 'content' keys

        Returns:
            Complete LaTeX document
        """
        sections = []
        month_name = calendar.month_name[month]

        # Prayer type titles
        prayer_titles = {
            'morning': 'Daily Morning Prayer',
            'evening': 'Daily Evening Prayer',
            'midday': 'Midday Prayer',
            'compline': 'Compline'
        }
        prayer_title = prayer_titles.get(prayer_type, 'Daily Office')

        # LaTeX preamble with hyperref for links
        sections.append(r'\documentclass[12pt,letterpaper]{article}')
        sections.append(r'\usepackage[utf8]{inputenc}')
        sections.append(r'\usepackage[T1]{fontenc}')
        sections.append(r'\usepackage{geometry}')
        sections.append(r'\usepackage{hyperref}')
        sections.append(r'\usepackage{fancyhdr}')
        sections.append(r'')

        # Configure hyperref for better link appearance
        sections.append(r'\hypersetup{')
        sections.append(r'  colorlinks=true,')
        sections.append(r'  linkcolor=blue,')
        sections.append(r'  urlcolor=blue,')
        sections.append(r'  pdfauthor={Daily Office 2019},')
        sections.append(r'  pdftitle={' + f'{prayer_title} - {month_name} {year}' + r'},')
        sections.append(r'}')
        sections.append(r'')

        # Set page size based on option
        if page_size == "remarkable":
            sections.append(r'\geometry{paperwidth=6.18in, paperheight=8.24in, left=0.5in, right=0.5in, top=1in, bottom=0.5in, headheight=14pt}')
        else:
            sections.append(r'\geometry{letterpaper, margin=1in, headheight=14pt}')
        sections.append(r'')

        # Paragraph formatting
        sections.append(r'\setlength{\parindent}{0pt}')
        sections.append(r'\setlength{\parskip}{0.5em}')
        sections.append(r'')

        # Custom section formatting (centered, no numbering)
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

        # Configure headers and footers with navigation
        sections.append(r'\fancypagestyle{fancy}{%')
        sections.append(r'  \fancyhf{}')
        sections.append(r'  \fancyhead[L]{\small\hyperref[index]{Index}}')  # Left header: link to index
        sections.append(r'  \fancyhead[C]{\small\nouppercase{\leftmark}}')  # Center header: current section
        sections.append(r'  \fancyhead[R]{\small\thepage}')  # Right header: page number
        sections.append(r'  \renewcommand{\headrulewidth}{0.4pt}')
        sections.append(r'}')
        sections.append(r'')
        sections.append(r'\pagestyle{fancy}')
        sections.append(r'')

        sections.append(r'\begin{document}')
        sections.append(r'')

        # Title page
        sections.append(r'\begin{titlepage}')
        sections.append(r'\centering')
        sections.append(r'\vspace*{2in}')
        sections.append(r'{\Huge\bfseries ' + prayer_title + r'\\[1em]}')
        sections.append(r'{\LARGE ' + f'{month_name} {year}' + r'\\[2em]}')
        sections.append(r'\vfill')
        sections.append(r'{\large The Book of Common Prayer (2019)}')
        sections.append(r'\end{titlepage}')
        sections.append(r'')
        sections.append(r'\newpage')
        sections.append(r'')

        # Index page
        sections.append(r'\section*{Index}\label{index}')
        sections.append(r'\addcontentsline{toc}{section}{Index}')
        sections.append(r'')
        sections.append(r'\begin{itemize}')
        sections.append(r'\setlength{\itemsep}{0.5em}')

        for item in daily_content:
            day_num = item['day']
            prayer_date = item['date']
            date_str = prayer_date.strftime('%A, %B %d, %Y')
            # Create hyperlink to each day
            sections.append(r'\item \hyperref[day' + str(day_num) + r']{' + date_str + r'}')

        sections.append(r'\end{itemize}')
        sections.append(r'')
        sections.append(r'\newpage')
        sections.append(r'')

        # Add each day's content
        for item in daily_content:
            day_num = item['day']
            prayer_date = item['date']
            content = item['content']
            date_str = prayer_date.strftime('%B %d')

            # Update section mark for header
            sections.append(r'\markboth{' + date_str + r'}{' + date_str + r'}')
            sections.append(r'')

            # Add the day's content (label is generated within the content)
            sections.append(content)

            # Add page break after each day (except the last one)
            if day_num < len(daily_content):
                sections.append(r'\newpage')
            sections.append(r'')

        sections.append(r'\end{document}')

        return '\n'.join(sections)

    def compile_to_pdf(
        self,
        year: int,
        month: int,
        output_pdf: str,
        prayer_type: str = 'morning',
        page_size: str = 'letter',
        psalm_cycle: Optional[int] = None,
        save_tex: bool = False,
        tex_filename: Optional[str] = None
    ):
        """
        Generate and compile a monthly prayer document to PDF.

        Args:
            year: The year (e.g., 2025)
            month: The month (1-12)
            output_pdf: Output PDF filename
            prayer_type: Type of prayer ('morning', 'evening', 'midday', 'compline')
            page_size: Page size - "letter" or "remarkable"
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60.
            save_tex: Whether to save the .tex source file
            tex_filename: Custom .tex filename (if save_tex is True)

        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If LaTeX compilation fails
            requests.RequestException: If API requests fail
        """
        # Generate the LaTeX content
        latex_content = self.generate_monthly_latex(
            year=year,
            month=month,
            prayer_type=prayer_type,
            page_size=page_size,
            psalm_cycle=psalm_cycle
        )

        # Use the MarkdownGenerator's compile method
        print(f"Compiling to PDF...")
        self.prayer_service.markdown_generator.compile_latex_to_pdf(
            latex_content=latex_content,
            output_pdf=output_pdf,
            save_tex=save_tex,
            tex_filename=tex_filename
        )

    def close(self):
        """Close the prayer service and free resources."""
        self.prayer_service.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
