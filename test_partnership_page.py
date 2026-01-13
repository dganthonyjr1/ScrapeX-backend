"""
Test the Chamber/Tourism partnership page for accuracy and completeness
"""

import os

def test_partnership_page():
    """Test the partnership page content"""
    
    page_path = "/home/ubuntu/scrapex-backend/CHAMBER_TOURISM_PARTNERSHIP.md"
    
    if not os.path.exists(page_path):
        print("❌ Partnership page does not exist")
        return False
    
    with open(page_path, 'r') as f:
        content = f.read()
    
    print("=" * 70)
    print("PARTNERSHIP PAGE TEST")
    print("=" * 70)
    
    # Required elements
    required_elements = [
        ("50% discount", "50% member discount"),
        ("15% revenue", "15% revenue giveback"),
        ("multi-lingual", "multi-lingual capabilities"),
        ("chamber", "chambers of commerce"),
        ("tourism", "tourism boards"),
        ("roi", "ROI examples"),
        ("community", "community impact"),
        ("no long-term", "no long-term commitment"),
    ]
    
    issues = []
    
    for keyword, description in required_elements:
        if keyword.lower() not in content.lower():
            issues.append(f"❌ Missing: {description}")
        else:
            print(f"✓ Found: {description}")
    
    # Check for technology mentions (should be minimal)
    tech_terms = ["AI", "software", "automation", "technology"]
    tech_count = sum(content.lower().count(term.lower()) for term in tech_terms)
    
    if tech_count > 5:
        issues.append(f"⚠️  Too much technology focus ({tech_count} mentions)")
    else:
        print(f"✓ Appropriate technology focus ({tech_count} mentions)")
    
    # Check for ROI examples
    if "$" not in content or "revenue" not in content.lower():
        issues.append("❌ Missing concrete ROI examples with dollar amounts")
    else:
        print("✓ Contains concrete ROI examples")
    
    # Check for contact information
    if "contact" not in content.lower():
        issues.append("❌ Missing contact information")
    else:
        print("✓ Contains contact information")
    
    print("\n" + "=" * 70)
    
    if not issues:
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        return True
    else:
        print("❌ ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        print("=" * 70)
        return False


if __name__ == "__main__":
    passed = test_partnership_page()
    exit(0 if passed else 1)
