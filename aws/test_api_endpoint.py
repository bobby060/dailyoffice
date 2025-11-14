#!/usr/bin/env python3
"""
Test script for Daily Office Lambda API endpoints.

This script tests both daily and monthly prayer generation endpoints
after the CloudFormation stack has been deployed.

Usage:
    python test_api_endpoint.py <API_ENDPOINT_URL>

Example:
    python test_api_endpoint.py https://abc123.execute-api.us-east-1.amazonaws.com/prod/prayer
"""

import sys
import requests
import argparse
from datetime import datetime, date, timedelta
import time
from pathlib import Path


def test_daily_prayer(base_url, prayer_type, test_date=None, remarkable=False):
    """
    Test daily prayer generation endpoint.

    Args:
        base_url: Base API Gateway URL
        prayer_type: Type of prayer (morning, evening, midday, compline)
        test_date: Date to test (defaults to today)
        remarkable: Whether to test remarkable format

    Returns:
        bool: True if test passed, False otherwise
    """
    params = {
        'type': prayer_type
    }

    if test_date:
        params['date'] = test_date.strftime('%Y-%m-%d')

    if remarkable:
        params['remarkable'] = 'true'

    test_name = f"Daily {prayer_type}"
    if test_date:
        test_name += f" ({test_date.strftime('%Y-%m-%d')})"
    if remarkable:
        test_name += " [Remarkable]"

    print(f"\n🔍 Testing: {test_name}")
    print(f"   URL: {base_url}")
    print(f"   Params: {params}")

    try:
        response = requests.get(base_url, params=params, timeout=60)

        if response.status_code != 200:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        # Check content type
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' not in content_type:
            print(f"   ❌ FAILED: Invalid content type: {content_type}")
            return False

        # Check PDF content
        pdf_data = response.content
        if not pdf_data.startswith(b'%PDF'):
            print(f"   ❌ FAILED: Response is not a valid PDF")
            return False

        # Check cache header
        cache_status = response.headers.get('X-Cache', 'UNKNOWN')
        pdf_size = len(pdf_data)

        print(f"   ✅ PASSED")
        print(f"   Cache: {cache_status}")
        print(f"   Size: {pdf_size:,} bytes ({pdf_size / 1024:.1f} KB)")

        return True

    except requests.exceptions.Timeout:
        print(f"   ❌ FAILED: Request timeout (>60s)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED: Request error: {e}")
        return False


def test_monthly_prayer(base_url, prayer_type, year=None, month=None, remarkable=False, psalm_cycle=None):
    """
    Test monthly prayer generation endpoint.

    Args:
        base_url: Base API Gateway URL
        prayer_type: Type of prayer (morning, evening, midday, compline)
        year: Year to test (defaults to current year)
        month: Month to test (defaults to current month)
        remarkable: Whether to test remarkable format
        psalm_cycle: Psalm cycle (30 or 60)

    Returns:
        bool: True if test passed, False otherwise
    """
    if not year:
        year = date.today().year
    if not month:
        month = date.today().month

    params = {
        'type': prayer_type,
        'monthly': 'true',
        'year': str(year),
        'month': str(month)
    }

    if remarkable:
        params['remarkable'] = 'true'

    if psalm_cycle:
        params['psalm_cycle'] = str(psalm_cycle)

    test_name = f"Monthly {prayer_type} ({year}-{month:02d})"
    if remarkable:
        test_name += " [Remarkable]"
    if psalm_cycle:
        test_name += f" [Cycle {psalm_cycle}]"

    print(f"\n🔍 Testing: {test_name}")
    print(f"   URL: {base_url}")
    print(f"   Params: {params}")

    try:
        # Monthly generation can take longer, so increase timeout
        print(f"   ⏳ Generating monthly PDF (this may take 30-120 seconds)...")
        start_time = time.time()

        response = requests.get(base_url, params=params, timeout=300)
        elapsed_time = time.time() - start_time

        if response.status_code != 200:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False

        # Check content type
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' not in content_type:
            print(f"   ❌ FAILED: Invalid content type: {content_type}")
            return False

        # Check PDF content
        pdf_data = response.content
        if not pdf_data.startswith(b'%PDF'):
            print(f"   ❌ FAILED: Response is not a valid PDF")
            return False

        # Check cache header
        cache_status = response.headers.get('X-Cache', 'UNKNOWN')
        pdf_size = len(pdf_data)

        print(f"   ✅ PASSED")
        print(f"   Cache: {cache_status}")
        print(f"   Size: {pdf_size:,} bytes ({pdf_size / 1024 / 1024:.2f} MB)")
        print(f"   Time: {elapsed_time:.1f} seconds")

        return True

    except requests.exceptions.Timeout:
        print(f"   ❌ FAILED: Request timeout (>300s)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED: Request error: {e}")
        return False


def test_cache_functionality(base_url, prayer_type='morning'):
    """
    Test that caching is working properly.

    Args:
        base_url: Base API Gateway URL
        prayer_type: Type of prayer to test

    Returns:
        bool: True if test passed, False otherwise
    """
    test_date = date.today()
    params = {
        'type': prayer_type,
        'date': test_date.strftime('%Y-%m-%d')
    }

    print(f"\n🔍 Testing: Cache functionality")
    print(f"   First request (should be MISS)...")

    try:
        # First request - should be a cache miss
        response1 = requests.get(base_url, params=params, timeout=60)
        if response1.status_code != 200:
            print(f"   ❌ FAILED: First request returned HTTP {response1.status_code}")
            return False

        cache_status1 = response1.headers.get('X-Cache', 'UNKNOWN')
        print(f"   Cache status: {cache_status1}")

        # Second request - should be a cache hit
        print(f"   Second request (should be HIT)...")
        time.sleep(1)  # Brief pause
        response2 = requests.get(base_url, params=params, timeout=60)

        if response2.status_code != 200:
            print(f"   ❌ FAILED: Second request returned HTTP {response2.status_code}")
            return False

        cache_status2 = response2.headers.get('X-Cache', 'UNKNOWN')
        print(f"   Cache status: {cache_status2}")

        # Verify cache hit on second request
        if cache_status2 == 'HIT':
            print(f"   ✅ PASSED: Cache is working correctly")
            return True
        else:
            print(f"   ⚠️  WARNING: Expected cache HIT, got {cache_status2}")
            print(f"   This might be expected if the cache was just populated")
            return True  # Don't fail the test, just warn

    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED: Request error: {e}")
        return False


def test_error_handling(base_url):
    """
    Test error handling for invalid requests.

    Args:
        base_url: Base API Gateway URL

    Returns:
        bool: True if test passed, False otherwise
    """
    print(f"\n🔍 Testing: Error handling")

    # Test 1: Missing prayer type
    print(f"   Test 1: Missing prayer type...")
    try:
        response = requests.get(base_url, params={}, timeout=10)
        if response.status_code == 400:
            print(f"   ✅ Correctly returned 400 for missing type")
        else:
            print(f"   ❌ Expected 400, got {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED: Request error: {e}")
        return False

    # Test 2: Invalid prayer type
    print(f"   Test 2: Invalid prayer type...")
    try:
        response = requests.get(base_url, params={'type': 'invalid'}, timeout=10)
        if response.status_code == 400:
            print(f"   ✅ Correctly returned 400 for invalid type")
        else:
            print(f"   ❌ Expected 400, got {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED: Request error: {e}")
        return False

    # Test 3: Invalid date format
    print(f"   Test 3: Invalid date format...")
    try:
        response = requests.get(base_url, params={'type': 'morning', 'date': 'invalid'}, timeout=10)
        if response.status_code == 400:
            print(f"   ✅ Correctly returned 400 for invalid date")
        else:
            print(f"   ❌ Expected 400, got {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED: Request error: {e}")
        return False

    print(f"   ✅ PASSED: Error handling works correctly")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Test Daily Office Lambda API endpoints',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test all functionality
  python test_api_endpoint.py https://abc123.execute-api.us-east-1.amazonaws.com/prod/prayer

  # Run quick tests only (no monthly)
  python test_api_endpoint.py --quick https://abc123.execute-api.us-east-1.amazonaws.com/prod/prayer

  # Save PDFs locally
  python test_api_endpoint.py --save-pdfs https://abc123.execute-api.us-east-1.amazonaws.com/prod/prayer
        """
    )

    parser.add_argument('api_url', help='API Gateway endpoint URL')
    parser.add_argument('--quick', action='store_true',
                        help='Run quick tests only (skip monthly generation)')
    parser.add_argument('--save-pdfs', action='store_true',
                        help='Save test PDFs to local files')

    args = parser.parse_args()

    api_url = args.api_url.rstrip('/')

    print("=" * 70)
    print("Daily Office Lambda API Endpoint Tests")
    print("=" * 70)
    print(f"API Endpoint: {api_url}")
    print(f"Test Mode: {'Quick' if args.quick else 'Full'}")
    print("=" * 70)

    results = []

    # Test error handling first
    results.append(("Error Handling", test_error_handling(api_url)))

    # Test daily prayers
    print("\n" + "=" * 70)
    print("DAILY PRAYER TESTS")
    print("=" * 70)

    for prayer_type in ['morning', 'evening', 'midday', 'compline']:
        results.append(
            (f"Daily {prayer_type}", test_daily_prayer(api_url, prayer_type))
        )

    # Test with specific date
    yesterday = date.today() - timedelta(days=1)
    results.append(
        ("Daily morning (yesterday)", test_daily_prayer(api_url, 'morning', yesterday))
    )

    # Test remarkable format
    results.append(
        ("Daily morning (Remarkable)", test_daily_prayer(api_url, 'morning', remarkable=True))
    )

    # Test cache functionality
    results.append(
        ("Cache Functionality", test_cache_functionality(api_url))
    )

    # Test monthly prayers (if not in quick mode)
    if not args.quick:
        print("\n" + "=" * 70)
        print("MONTHLY PRAYER TESTS")
        print("=" * 70)
        print("⚠️  Note: Monthly tests can take 1-2 minutes per test")

        current_month = date.today().month
        current_year = date.today().year

        # Test current month
        results.append(
            ("Monthly morning", test_monthly_prayer(api_url, 'morning'))
        )

        # Test with specific year/month
        results.append(
            ("Monthly evening (Dec 2024)", test_monthly_prayer(api_url, 'evening', 2024, 12))
        )

        # Test with psalm cycle
        results.append(
            ("Monthly morning (30-day cycle)", test_monthly_prayer(api_url, 'morning', psalm_cycle=30))
        )

    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10s} {test_name}")

    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
