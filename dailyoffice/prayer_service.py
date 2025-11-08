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
        prayer_date: Optional[date] = None
    ) -> str:
        """
        Generate a complete morning prayer document in Markdown format.

        Note: The API provides psalm readings according to its default cycle
        (typically the 60-day cycle). The cycle being used is indicated in
        the generated output.

        Args:
            prayer_date: The date for the prayer. Defaults to today.

        Returns:
            Complete morning prayer as a Markdown string

        Raises:
            requests.RequestException: If the API request fails
        """
        if prayer_date is None:
            prayer_date = date.today()

        # Fetch the prayer data from the API
        prayer_data = self.api_client.get_morning_prayer(prayer_date=prayer_date)

        # Generate markdown from the API response
        markdown_content = self.markdown_generator.generate_morning_prayer(prayer_data)

        return markdown_content

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
