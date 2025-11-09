"""
Prayer Service - Main service layer

This module coordinates between the API client and the markdown generator
to provide a high-level interface for generating prayer documents.
"""

from datetime import date
from typing import Optional
from .api_client import DailyOfficeAPIClient
from .prayer_generator import MarkdownGenerator


class PrayerService:
    """
    Main service for generating daily office prayers.

    This class coordinates fetching data from the API and generating
    formatted output documents.
    """

    def __init__(self):
        """Initialize the prayer service."""
        self.api_client = DailyOfficeAPIClient()
        self.markdown_generator = MarkdownGenerator()

    def generate_morning_prayer_markdown(
        self,
        prayer_date: Optional[date] = None,
        psalm_cycle: Optional[int] = None
    ) -> str:
        """
        Generate a complete morning prayer document in Markdown format.

        Note: The API provides psalm readings according to its default cycle
        (typically the 60-day cycle). The cycle being used is indicated in
        the generated output.

        Args:
            prayer_date: The date for the prayer. Defaults to today.
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60.

        Returns:
            Complete morning prayer as a Markdown string

        Raises:
            requests.RequestException: If the API request fails
        """
        if prayer_date is None:
            prayer_date = date.today()

        # Fetch the prayer data from the API
        prayer_data = self.api_client.get_morning_prayer(prayer_date=prayer_date, psalm_cycle=psalm_cycle)

        # Generate markdown from the API response
        markdown_content = self.markdown_generator.generate_morning_prayer(prayer_data)

        return markdown_content

    def generate_evening_prayer_markdown(
        self,
        prayer_date: Optional[date] = None,
        psalm_cycle: Optional[int] = None
    ) -> str:
        """
        Generate a complete evening prayer document in Markdown format.

        Args:
            prayer_date: The date for the prayer. Defaults to today.
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60.

        Returns:
            Complete evening prayer as a Markdown string

        Raises:
            requests.RequestException: If the API request fails
        """
        if prayer_date is None:
            prayer_date = date.today()

        prayer_data = self.api_client.get_evening_prayer(prayer_date=prayer_date, psalm_cycle=psalm_cycle)
        markdown_content = self.markdown_generator.generate_evening_prayer(prayer_data)
        return markdown_content

    def generate_midday_prayer_markdown(
        self,
        prayer_date: Optional[date] = None,
        psalm_cycle: Optional[int] = None
    ) -> str:
        """
        Generate a complete midday prayer document in Markdown format.

        Args:
            prayer_date: The date for the prayer. Defaults to today.
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60.

        Returns:
            Complete midday prayer as a Markdown string

        Raises:
            requests.RequestException: If the API request fails
        """
        if prayer_date is None:
            prayer_date = date.today()

        prayer_data = self.api_client.get_midday_prayer(prayer_date=prayer_date, psalm_cycle=psalm_cycle)
        markdown_content = self.markdown_generator.generate_midday_prayer(prayer_data)
        return markdown_content

    def generate_compline_markdown(
        self,
        prayer_date: Optional[date] = None,
        psalm_cycle: Optional[int] = None
    ) -> str:
        """
        Generate a complete compline (night prayer) document in Markdown format.

        Args:
            prayer_date: The date for the prayer. Defaults to today.
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60.

        Returns:
            Complete compline as a Markdown string

        Raises:
            requests.RequestException: If the API request fails
        """
        if prayer_date is None:
            prayer_date = date.today()

        prayer_data = self.api_client.get_compline(prayer_date=prayer_date, psalm_cycle=psalm_cycle)
        markdown_content = self.markdown_generator.generate_compline(prayer_data)
        return markdown_content

    def generate_morning_prayer_latex(
        self,
        prayer_date: Optional[date] = None,
        page_size: str = "letter",
        psalm_cycle: Optional[int] = None
    ) -> str:
        """
        Generate a complete morning prayer document in LaTeX format.

        Args:
            prayer_date: The date for the prayer. Defaults to today.
            page_size: Page size - "letter" or "remarkable"
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60.

        Returns:
            Complete morning prayer as a LaTeX string

        Raises:
            requests.RequestException: If the API request fails
        """
        if prayer_date is None:
            prayer_date = date.today()

        # Fetch the prayer data from the API
        prayer_data = self.api_client.get_morning_prayer(prayer_date=prayer_date, psalm_cycle=psalm_cycle)

        # Generate LaTeX from the API response
        latex_content = self.markdown_generator.generate_morning_prayer_latex(prayer_data, page_size)

        return latex_content

    def generate_evening_prayer_latex(
        self,
        prayer_date: Optional[date] = None,
        page_size: str = "letter",
        psalm_cycle: Optional[int] = None
    ) -> str:
        """
        Generate a complete evening prayer document in LaTeX format.

        Args:
            prayer_date: The date for the prayer. Defaults to today.
            page_size: Page size - "letter" or "remarkable"
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60.

        Returns:
            Complete evening prayer as a LaTeX string

        Raises:
            requests.RequestException: If the API request fails
        """
        if prayer_date is None:
            prayer_date = date.today()

        prayer_data = self.api_client.get_evening_prayer(prayer_date=prayer_date, psalm_cycle=psalm_cycle)
        latex_content = self.markdown_generator.generate_evening_prayer_latex(prayer_data, page_size)
        return latex_content

    def generate_midday_prayer_latex(
        self,
        prayer_date: Optional[date] = None,
        page_size: str = "letter",
        psalm_cycle: Optional[int] = None
    ) -> str:
        """
        Generate a complete midday prayer document in LaTeX format.

        Args:
            prayer_date: The date for the prayer. Defaults to today.
            page_size: Page size - "letter" or "remarkable"
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60.

        Returns:
            Complete midday prayer as a LaTeX string

        Raises:
            requests.RequestException: If the API request fails
        """
        if prayer_date is None:
            prayer_date = date.today()

        prayer_data = self.api_client.get_midday_prayer(prayer_date=prayer_date, psalm_cycle=psalm_cycle)
        latex_content = self.markdown_generator.generate_midday_prayer_latex(prayer_data, page_size)
        return latex_content

    def generate_compline_latex(
        self,
        prayer_date: Optional[date] = None,
        page_size: str = "letter",
        psalm_cycle: Optional[int] = None
    ) -> str:
        """
        Generate a complete compline (night prayer) document in LaTeX format.

        Args:
            prayer_date: The date for the prayer. Defaults to today.
            page_size: Page size - "letter" or "remarkable"
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60.

        Returns:
            Complete compline as a LaTeX string

        Raises:
            requests.RequestException: If the API request fails
        """
        if prayer_date is None:
            prayer_date = date.today()

        prayer_data = self.api_client.get_compline(prayer_date=prayer_date, psalm_cycle=psalm_cycle)
        latex_content = self.markdown_generator.generate_compline_latex(prayer_data, page_size)
        return latex_content

    def save_prayer(
        self,
        filename: str,
        prayer_type: str = 'morning',
        prayer_date: Optional[date] = None,
        as_pdf: bool = False
    ):
        """
        Generate and save a prayer document to a file.

        Args:
            filename: The output filename (should end in .md or .pdf)
            prayer_type: Type of prayer ('morning', 'evening', or 'midday')
            prayer_date: The date for the prayer. Defaults to today.
            as_pdf: If True, save as PDF instead of Markdown

        Raises:
            requests.RequestException: If the API request fails
            IOError: If the file cannot be written
            ValueError: If prayer_type is invalid
        """
        # Generate appropriate markdown based on prayer type
        if prayer_type == 'morning':
            markdown_content = self.generate_morning_prayer_markdown(prayer_date=prayer_date)
        elif prayer_type == 'evening':
            markdown_content = self.generate_evening_prayer_markdown(prayer_date=prayer_date)
        elif prayer_type == 'midday':
            markdown_content = self.generate_midday_prayer_markdown(prayer_date=prayer_date)
        else:
            raise ValueError(f"Invalid prayer type: {prayer_type}. Must be 'morning', 'evening', or 'midday'")

        # Save as PDF or Markdown
        if as_pdf:
            self.markdown_generator.save_to_pdf(markdown_content, filename)
        else:
            self.markdown_generator.save_to_file(markdown_content, filename)

    def save_morning_prayer(
        self,
        filename: str,
        prayer_date: Optional[date] = None
    ):
        """
        Generate and save a morning prayer document to a file.

        Args:
            filename: The output filename (should end in .md)
            prayer_date: The date for the prayer. Defaults to today.

        Raises:
            requests.RequestException: If the API request fails
            IOError: If the file cannot be written
        """
        markdown_content = self.generate_morning_prayer_markdown(
            prayer_date=prayer_date
        )

        self.markdown_generator.save_to_file(markdown_content, filename)

    def close(self):
        """Close any open resources."""
        self.api_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
