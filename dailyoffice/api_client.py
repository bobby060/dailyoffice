"""
API Client for Daily Office 2019

This module handles all communication with the Daily Office 2019 API.
"""

import requests
import json
import hashlib
from datetime import date, datetime
from typing import Dict, Any, Optional
from urllib.parse import urljoin
from pathlib import Path


class DailyOfficeAPIClient:
    """
    Client for interacting with the Daily Office 2019 API.

    The API provides liturgical content for daily prayer services including
    morning prayer, evening prayer, and compline from The Book of Common Prayer (2019).

    Features:
    - Automatic caching of API responses to avoid repeated requests
    - Cache stored in .cache directory (gitignored)
    """

    BASE_URL = "https://api.dailyoffice2019.com/api/v1/"

    def __init__(self, base_url: Optional[str] = None, enable_cache: bool = True, cache_dir: Optional[str] = None):
        """
        Initialize the API client.

        Args:
            base_url: Optional custom base URL for the API. Defaults to the official API.
            enable_cache: Whether to enable caching of API responses. Defaults to True.
            cache_dir: Custom cache directory. Defaults to .cache in the current directory.
        """
        self.base_url = base_url or self.BASE_URL
        self.enable_cache = enable_cache

        # Set up cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.cwd() / '.cache'

        if self.enable_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/html,application/xhtml+xml',
            'Accept-Language': 'en-US,en;q=0.9',
        })

    def _get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """
        Generate a cache key for the given endpoint and parameters.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            A unique cache key string
        """
        # Create a deterministic string from endpoint and params
        param_str = json.dumps(params, sort_keys=True)
        cache_input = f"{endpoint}_{param_str}"

        # Use SHA256 hash for the filename to keep it clean
        hash_obj = hashlib.sha256(cache_input.encode())
        return hash_obj.hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from cache if it exists.

        Args:
            cache_key: The cache key

        Returns:
            Cached data or None if not found
        """
        if not self.enable_cache:
            return None

        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If cache file is corrupted, ignore it
                return None

        return None

    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """
        Save data to cache.

        Args:
            cache_key: The cache key
            data: Data to cache
        """
        if not self.enable_cache:
            return

        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError:
            # If we can't write to cache, just continue without caching
            pass

    def get_morning_prayer(
        self,
        prayer_date: Optional[date] = None,
        psalm_cycle: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch morning prayer liturgy for a specific date.

        Note: The API returns psalm readings according to the 60-day cycle by default.
        The response includes psalm cycle information in the module metadata.

        Args:
            prayer_date: The date for which to fetch morning prayer.
                        Defaults to today if not specified.
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60 if not specified.

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

        # Add query parameters if specified
        params = {}
        if psalm_cycle is not None:
            if psalm_cycle not in [30, 60]:
                raise ValueError(f"Psalm cycle must be 30 or 60, got {psalm_cycle}")
            params['psalms'] = psalm_cycle

        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data

        # Fetch from API
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Save to cache
            self._save_to_cache(cache_key, data)

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
        prayer_date: Optional[date] = None,
        psalm_cycle: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch evening prayer liturgy for a specific date.

        Args:
            prayer_date: The date for which to fetch evening prayer.
                        Defaults to today if not specified.
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60 if not specified.

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

        # Add query parameters if specified
        params = {}
        if psalm_cycle is not None:
            if psalm_cycle not in [30, 60]:
                raise ValueError(f"Psalm cycle must be 30 or 60, got {psalm_cycle}")
            params['psalms'] = psalm_cycle

        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data

        # Fetch from API
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Save to cache
            self._save_to_cache(cache_key, data)

            return data

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
        prayer_date: Optional[date] = None,
        psalm_cycle: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch midday prayer liturgy for a specific date.

        Args:
            prayer_date: The date for which to fetch midday prayer.
                        Defaults to today if not specified.
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60 if not specified.

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

        # Add query parameters if specified
        params = {}
        if psalm_cycle is not None:
            if psalm_cycle not in [30, 60]:
                raise ValueError(f"Psalm cycle must be 30 or 60, got {psalm_cycle}")
            params['psalms'] = psalm_cycle

        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data

        # Fetch from API
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Save to cache
            self._save_to_cache(cache_key, data)

            return data

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
        prayer_date: Optional[date] = None,
        psalm_cycle: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch compline (night prayer) liturgy for a specific date.

        Args:
            prayer_date: The date for which to fetch compline.
                        Defaults to today if not specified.
            psalm_cycle: The psalm cycle to use (30 or 60). Defaults to 60 if not specified.

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

        # Add query parameters if specified
        params = {}
        if psalm_cycle is not None:
            if psalm_cycle not in [30, 60]:
                raise ValueError(f"Psalm cycle must be 30 or 60, got {psalm_cycle}")
            params['psalms'] = psalm_cycle

        # Check cache first
        cache_key = self._get_cache_key(endpoint, params)
        cached_data = self._get_from_cache(cache_key)
        if cached_data is not None:
            return cached_data

        # Fetch from API
        url = urljoin(self.base_url, endpoint)

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            # Save to cache
            self._save_to_cache(cache_key, data)

            return data

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
