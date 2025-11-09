"""
API Client for Daily Office 2019

This module handles all communication with the Daily Office 2019 API.
"""

import requests
from datetime import date, datetime
from typing import Dict, Any, Optional
from urllib.parse import urljoin


class DailyOfficeAPIClient:
    """
    Client for interacting with the Daily Office 2019 API.

    The API provides liturgical content for daily prayer services including
    morning prayer, evening prayer, and compline from The Book of Common Prayer (2019).
    """

    BASE_URL = "https://api.dailyoffice2019.com/api/v1/"

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the API client.

        Args:
            base_url: Optional custom base URL for the API. Defaults to the official API.
        """
        self.base_url = base_url or self.BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
        })

    def get_morning_prayer(
        self,
        prayer_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Fetch morning prayer liturgy for a specific date.

        Note: The API returns psalm readings according to the 60-day cycle by default.
        The response includes psalm cycle information in the module metadata.

        Args:
            prayer_date: The date for which to fetch morning prayer.
                        Defaults to today if not specified.

        Returns:
            Dictionary containing the complete morning prayer liturgy with all
            modules (readings, psalms, prayers, etc.)

        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the response cannot be parsed
        """
        if prayer_date is None:
            prayer_date = date.today()

        # Format date as YYYY-MM-DD
        date_str = prayer_date.strftime("%Y-%m-%d")

        # Construct the endpoint URL
        endpoint = f"office/morning_prayer/{date_str}"
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            return data

        except requests.RequestException as e:
            raise requests.RequestException(
                f"Failed to fetch morning prayer for {date_str}: {e}"
            ) from e
        except ValueError as e:
            raise ValueError(
                f"Failed to parse API response for {date_str}: {e}"
            ) from e

    def get_evening_prayer(
        self,
        prayer_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Fetch evening prayer liturgy for a specific date.

        Args:
            prayer_date: The date for which to fetch evening prayer.
                        Defaults to today if not specified.

        Returns:
            Dictionary containing the complete evening prayer liturgy

        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the response cannot be parsed
        """
        if prayer_date is None:
            prayer_date = date.today()

        date_str = prayer_date.strftime("%Y-%m-%d")
        endpoint = f"office/evening_prayer/{date_str}"
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            raise requests.RequestException(
                f"Failed to fetch evening prayer for {date_str}: {e}"
            ) from e
        except ValueError as e:
            raise ValueError(
                f"Failed to parse API response for {date_str}: {e}"
            ) from e

    def get_midday_prayer(
        self,
        prayer_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Fetch midday prayer liturgy for a specific date.

        Args:
            prayer_date: The date for which to fetch midday prayer.
                        Defaults to today if not specified.

        Returns:
            Dictionary containing the complete midday prayer liturgy

        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the response cannot be parsed
        """
        if prayer_date is None:
            prayer_date = date.today()

        date_str = prayer_date.strftime("%Y-%m-%d")
        endpoint = f"office/midday_prayer/{date_str}"
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            raise requests.RequestException(
                f"Failed to fetch midday prayer for {date_str}: {e}"
            ) from e
        except ValueError as e:
            raise ValueError(
                f"Failed to parse API response for {date_str}: {e}"
            ) from e

    def get_compline(
        self,
        prayer_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Fetch compline (night prayer) liturgy for a specific date.

        Args:
            prayer_date: The date for which to fetch compline.
                        Defaults to today if not specified.

        Returns:
            Dictionary containing the complete compline liturgy

        Raises:
            requests.RequestException: If the API request fails
            ValueError: If the response cannot be parsed
        """
        if prayer_date is None:
            prayer_date = date.today()

        date_str = prayer_date.strftime("%Y-%m-%d")
        endpoint = f"office/compline/{date_str}"
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            raise requests.RequestException(
                f"Failed to fetch compline for {date_str}: {e}"
            ) from e
        except ValueError as e:
            raise ValueError(
                f"Failed to parse API response for {date_str}: {e}"
            ) from e

    def close(self):
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
