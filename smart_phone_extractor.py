"""
Smart Phone Number Extractor
Prioritizes phone numbers based on context and filters out demo/test numbers
"""

import re
from typing import List, Tuple
from bs4 import BeautifulSoup


def extract_smart_phones(soup: BeautifulSoup, text: str, is_contact_page: bool = False) -> List[str]:
    """
    Extract phone numbers with smart prioritization
    
    Args:
        soup: BeautifulSoup object
        text: Raw HTML text
        is_contact_page: Whether this is a dedicated contact page
    
    Returns:
        List of phone numbers, ordered by priority (most likely to be correct first)
    """
    
    # Store phones with their priority scores
    phone_scores = {}  # {phone: score}
    
    invalid_patterns = [
        r'^(000|111|222|333|444|555|666|777|888|999)',
        r'^(123|234|345|456|567|678|789)',
        r'(\d)\1{6,}',
    ]
    
    def is_valid_phone(area, prefix, line):
        """Validate phone number components"""
        if area[0] in ['0', '1'] or prefix[0] in ['0', '1']:
            return False
        
        full_number = area + prefix + line
        for pattern in invalid_patterns:
            if re.match(pattern, full_number):
                return False
        
        if len(set(full_number)) == 1:
            return False
        
        return True
    
    def add_phone(phone: str, priority: int):
        """Add phone with priority score"""
        if phone not in phone_scores:
            phone_scores[phone] = 0
        phone_scores[phone] += priority
    
    # Priority 1: Phone numbers with "Phone" label nearby (HIGHEST PRIORITY)
    # Look for patterns like "Phone" followed by a phone number within 200 characters
    phone_sections = re.finditer(r'(?i)phone', text)
    for match in phone_sections:
        # Get 200 chars after "phone"
        start = match.start()
        section = text[start:start+200]
        
        # Look for phone patterns in this section
        phone_patterns = [
            r'\+?1?[\s]*([2-9]\d{2})[\s]+([2-9]\d{2})[\s]+([0-9]{4})',  # +1 302 846 7370
            r'\(?([2-9]\d{2})\)?[\s.-]*([2-9]\d{2})[\s.-]*(\d{4})',  # (302) 846-7370
        ]
        
        for pattern in phone_patterns:
            section_matches = re.findall(pattern, section)
            for m in section_matches:
                if len(m) == 3:
                    area, prefix, line = m[0], m[1], m[2]
                    if is_valid_phone(area, prefix, line):
                        formatted = f"({area}) {prefix}-{line}"
                        add_phone(formatted, 1000)  # Highest priority
    
    # Priority 2: tel: links
    for link in soup.find_all('a', href=re.compile(r'^tel:')):
        phone = link['href'].replace('tel:', '').replace('+1', '').strip()
        clean = re.sub(r'[^\d]', '', phone)
        if len(clean) == 10:
            area, prefix, line = clean[:3], clean[3:6], clean[6:]
            if is_valid_phone(area, prefix, line):
                formatted = f"({area}) {prefix}-{line}"
                add_phone(formatted, 500)
    
    # Priority 3: Phone numbers in contact sections
    contact_selectors = [
        '.contact', '#contact', '[class*="contact"]', '[id*="contact"]',
        'footer', '.footer', '#footer', 'header', '.header'
    ]
    
    patterns = [
        r'\(?([2-9]\d{2})\)?[\s.-]?([2-9]\d{2})[\s.-]?(\d{4})',
        r'([2-9]\d{2})\.([2-9]\d{2})\.(\d{4})',
        r'\+?1?[\s.-]?\(?([2-9]\d{2})\)?[\s.-]?([2-9]\d{2})[\s.-]?(\d{4})',
    ]
    
    for selector in contact_selectors:
        try:
            elements = soup.select(selector)
            for elem in elements:
                elem_text = elem.get_text()
                for pattern in patterns:
                    matches = re.findall(pattern, elem_text)
                    for match in matches:
                        if len(match) == 3:
                            area, prefix, line = match[0], match[1], match[2]
                            if is_valid_phone(area, prefix, line):
                                formatted = f"({area}) {prefix}-{line}"
                                add_phone(formatted, 200)
        except:
            continue
    
    # Priority 4: All other phone numbers (LOWEST PRIORITY)
    # Only include these if we're NOT on a contact page
    if not is_contact_page:
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 3:
                    area, prefix, line = match[0], match[1], match[2]
                    if is_valid_phone(area, prefix, line):
                        formatted = f"({area}) {prefix}-{line}"
                        add_phone(formatted, 10)
    
    # Sort by priority score (highest first)
    sorted_phones = sorted(phone_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Return phones in priority order
    return [phone for phone, score in sorted_phones]


def get_primary_phone(phones: List[str]) -> str:
    """Get the primary (most likely correct) phone number"""
    if not phones:
        return None
    return phones[0]  # Already sorted by priority
