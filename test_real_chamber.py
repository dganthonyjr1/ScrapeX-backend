"""Test complete extraction on real Chamber of Commerce website"""

import json
from complete_business_extractor import CompleteBusinessExtractor

def test_real_chamber():
    """Test extraction on Metro Atlanta Chamber"""
    extractor = CompleteBusinessExtractor()
    
    url = 'https://metroatlantachamber.com/'
    
    print("="*80)
    print(f"TESTING: Metro Atlanta Chamber")
    print(f"URL: {url}")
    print("="*80)
    
    result = extractor.extract_complete_business_data(url, business_name='Metro Atlanta Chamber')
    
    # Display results
    print(f"\n{'EXTRACTION RESULTS':^80}")
    print("="*80)
    
    print(f"\n📋 BUSINESS INFORMATION:")
    print(f"   Name: {result.get('business_name')}")
    print(f"   Description: {result.get('description', 'N/A')[:200]}...")
    print(f"   Industries: {', '.join(result.get('industries', []))}")
    
    print(f"\n📞 CONTACT INFORMATION:")
    print(f"   Phones: {result.get('phone', [])}")
    print(f"   Emails: {result.get('email', [])}")
    print(f"   Address: {result.get('address', [])}")
    print(f"   Website: {result.get('website', 'N/A')}")
    
    print(f"\n👔 BUSINESS OWNER / EXECUTIVES:")
    print(f"   Owner Name: {result.get('business_owner_name', 'N/A')}")
    print(f"   Owner Title: {result.get('business_owner_title', 'N/A')}")
    print(f"   Key Decision Makers: {len(result.get('key_decision_makers', []))} found")
    for dm in result.get('key_decision_makers', [])[:3]:
        print(f"      - {dm}")
    
    print(f"\n💼 COMPANY DETAILS:")
    print(f"   Employee Count: {result.get('employee_count', 'N/A')}")
    print(f"   Employee Range: {result.get('employee_range', 'N/A')}")
    print(f"   Follower Count: {result.get('follower_count', 'N/A')}")
    
    print(f"\n🌐 SOCIAL MEDIA:")
    social = result.get('social_media', {})
    for platform, url in social.items():
        print(f"   {platform.title()}: {url}")
    
    print(f"\n💰 REVENUE OPPORTUNITIES:")
    rev_ops = result.get('revenue_opportunities', {})
    print(f"   Total Opportunities: {rev_ops.get('total_opportunities_found', 0)}")
    print(f"   Estimated Monthly Loss: ${rev_ops.get('estimated_monthly_revenue_loss', 0):,}")
    print(f"\n   Opportunities Found:")
    for opp in rev_ops.get('opportunities', []):
        print(f"      • {opp.get('description')} (${opp.get('estimated_loss', 0)}/mo)")
    
    print(f"\n🎯 AI ANALYSIS:")
    print(f"   Missing Services: {result.get('missing_services', [])}")
    print(f"   Technology Gaps: {result.get('technology_gaps', [])}")
    print(f"   Competitive Weaknesses: {result.get('competitive_weaknesses', [])}")
    print(f"   Ideal Solution: {result.get('ideal_solution', 'N/A')}")
    print(f"   Urgency Score: {result.get('urgency_score', 'N/A')}/10")
    
    print(f"\n📊 EXTRACTION METRICS:")
    print(f"   Methods Used: {', '.join(result.get('extraction_methods_used', []))}")
    print(f"   Data Completeness: {result.get('data_completeness_score', 0)}%")
    print(f"   Extraction Time: {result.get('scraped_at')}")
    
    print("\n" + "="*80)
    
    # Save full result
    with open('/home/ubuntu/chamber_extraction_result.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print("\n✓ Full results saved to: /home/ubuntu/chamber_extraction_result.json")
    
    # Verify all required fields
    print(f"\n{'VERIFICATION':^80}")
    print("="*80)
    
    required_checks = {
        'Business Name': bool(result.get('business_name')),
        'Phone Numbers': len(result.get('phone', [])) > 0,
        'Email Addresses': len(result.get('email', [])) > 0,
        'Business Owner': bool(result.get('business_owner_name')),
        'Description': bool(result.get('description')),
        'Revenue Opportunities': result.get('revenue_opportunities', {}).get('total_opportunities_found', 0) > 0,
        'AI Analysis': bool(result.get('urgency_score')),
        'Services': len(result.get('services', [])) > 0
    }
    
    for check, passed in required_checks.items():
        status = "✓" if passed else "✗"
        print(f"   {status} {check}")
    
    passed_count = sum(required_checks.values())
    total_count = len(required_checks)
    
    print(f"\n   Overall: {passed_count}/{total_count} checks passed ({int(passed_count/total_count*100)}%)")
    
    if passed_count == total_count:
        print("\n   🎉 ALL FEATURES WORKING!")
    else:
        print(f"\n   ⚠️  {total_count - passed_count} features need fixing")
    
    print("="*80)

if __name__ == '__main__':
    test_real_chamber()
