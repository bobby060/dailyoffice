#!/usr/bin/env python3
"""
Simple script to validate Daily Office 2019 API endpoints without authentication.
Tests common patterns and endpoints to see which ones work publicly.
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://api.dailyoffice2019.com/api"

def test_endpoint(path, description):
    """Test a single endpoint and return results."""
    url = f"{BASE_URL}{path}"
    try:
        response = requests.get(url, timeout=10)
        print(f"✓ {description}")
        print(f"  URL: {url}")
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Response: Valid JSON ({len(str(data))} chars)")
                # Show first few keys if it's a dict
                if isinstance(data, dict) and data:
                    keys = list(data.keys())[:3]
                    print(f"  Keys: {keys}{'...' if len(data) > 3 else ''}")
            except:
                print(f"  Response: Non-JSON ({len(response.text)} chars)")
        elif response.status_code == 401:
            print(f"  Response: Authentication required")
        else:
            print(f"  Response: {response.reason}")
        print()
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"✗ {description}")
        print(f"  URL: {url}")
        print(f"  Error: {e}")
        print()
        return False

def main():
    """Test various API endpoints without authentication."""
    print("Testing Daily Office 2019 API - No Authentication")
    print("=" * 50)
    
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    year = today.year
    
    # Test cases: (path, description)
    test_cases = [
        # Potential public endpoints
        ("/v1/about", "About endpoint"),
        ("/v1/email_signup", "Email signup endpoint"),
        
        # Prayer services for today
        (f"/v1/office/morning_prayer/{date_str}", f"Morning Prayer for {date_str}"),
        (f"/v1/office/evening_prayer/{date_str}", f"Evening Prayer for {date_str}"),
        (f"/v1/office/compline/{date_str}", f"Compline for {date_str}"),
        (f"/v1/office/midday_prayer/{date_str}", f"Midday Prayer for {date_str}"),
        
        # Calendar and readings
        (f"/v1/calendar/{year}", f"Calendar for {year}"),
        (f"/v1/readings/{date_str}", f"Readings for {date_str}"),
        
        # Bible and Psalms
        ("/v1/psalms", "Psalms index"),
        ("/v1/bible/john.3.16/ESV", "Bible verse (John 3:16, ESV)"),
        
        # Root endpoints
        ("/", "API root"),
        ("/v1/", "API v1 root"),
    ]
    
    successful_endpoints = []
    
    for path, description in test_cases:
        if test_endpoint(path, description):
            successful_endpoints.append(path)
    
    # Summary
    print("\nSUMMARY")
    print("=" * 50)
    print(f"Total endpoints tested: {len(test_cases)}")
    print(f"Successful (200 OK): {len(successful_endpoints)}")
    print(f"Success rate: {len(successful_endpoints)/len(test_cases)*100:.1f}%")
    
    if successful_endpoints:
        print(f"\nWorking endpoints:")
        for endpoint in successful_endpoints:
            print(f"  - {endpoint}")
    else:
        print("\nNo endpoints worked without authentication.")
        print("This API likely requires authentication for all endpoints.")

if __name__ == "__main__":
    main()