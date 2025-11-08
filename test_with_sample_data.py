#!/usr/bin/env python3
"""
Test the markdown generator with sample API data.

This script demonstrates the markdown generation using real API data
(from 2025-11-08) without making actual API requests.
"""

import json
from dailyoffice.prayer_generator import MarkdownGenerator

# Sample API response (partial, for demonstration)
SAMPLE_API_RESPONSE = {
    "modules": [
        {
            "name": "Opening Sentence",
            "lines": [
                {
                    "content": "Opening Sentence",
                    "line_type": "heading",
                    "indented": False,
                },
                {
                    "content": "The hour is coming, and is now here, when the true worshipers will worship the Father in spirit and truth, for the Father is seeking such people to worship him.",
                    "line_type": "leader",
                    "indented": False,
                },
                {
                    "content": "JOHN 4:23",
                    "line_type": "citation",
                    "indented": False,
                }
            ]
        },
        {
            "name": "The Prayers",
            "lines": [
                {
                    "content": "The Prayers",
                    "line_type": "heading",
                    "indented": False,
                },
                {
                    "content": "The Lord be with you.",
                    "line_type": "leader_dialogue",
                    "indented": False,
                    "preface": "Officiant",
                },
                {
                    "content": "And with your spirit.",
                    "line_type": "congregation_dialogue",
                    "indented": False,
                    "preface": "People",
                },
            ]
        }
    ],
    "calendar_day": {
        "date": "2025-11-08",
        "date_description": {
            "date": "2025-11-8",
            "weekday": "Saturday",
            "month": "11",
            "month_name": "November",
            "day": "8",
            "year": "2025"
        },
        "season": {
            "name": "Season After Pentecost",
            "colors": ["green"]
        },
        "primary_feast": "Saturday after the Twenty-first Sunday after Pentecost, or the Twentieth Sunday after Trinity (Proper 26)"
    }
}


def main():
    """Test the markdown generator with sample data."""
    print("Testing Markdown Generator with sample API data...")
    print("="*80)

    generator = MarkdownGenerator()
    markdown = generator.generate_morning_prayer(SAMPLE_API_RESPONSE)

    print(markdown)
    print("\n" + "="*80)
    print("\nTest completed successfully!")
    print("\nNote: This is a partial sample. The full API response includes:")
    print("  - Confession of Sin")
    print("  - Preces")
    print("  - Invitatory (Venite)")
    print("  - Psalms (with cycle indication)")
    print("  - Scripture Readings (OT and NT)")
    print("  - Canticles (Te Deum, Benedictus)")
    print("  - The Apostles' Creed")
    print("  - Collects and Final Prayers")


if __name__ == "__main__":
    main()
