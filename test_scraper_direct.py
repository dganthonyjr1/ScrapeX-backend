#!/usr/bin/env python3
"""
Test the scraper directly to see what's happening
"""

from universal_scraper import UniversalBusinessScraper
import json

scraper = UniversalBusinessScraper()

# Test with real small businesses that have phone numbers
test_urls = [
    "https://www.example-plumber.com",  # Will test real ones
    "https://www.joes-pizza.com",
    "https://www.local-dentist.com"
]

# For now, test with a known working URL
test_url = "https://www.ycombinator.com/companies"

print("="*70)
print("DIRECT SCRAPER TEST")
print("="*70)
print(f"\nTesting: {test_url}\n")

result = scraper.scrape_business(test_url)

print("RESULT:")
print(json.dumps(result, indent=2))

print("\n" + "="*70)
print("ANALYSIS")
print("="*70)
print(f"Phones found: {len(result.get('phone', []))}")
print(f"Emails found: {len(result.get('email', []))}")
print(f"Social media: {len(result.get('social_media', {}))}")
print(f"Completeness: {result.get('data_completeness_score', 0)}%")
print(f"Insights: {len(result.get('analysis_insights', []))}")

if result.get('analysis_insights'):
    print("\nInsights:")
    for insight in result['analysis_insights']:
        print(f"  • {insight}")
