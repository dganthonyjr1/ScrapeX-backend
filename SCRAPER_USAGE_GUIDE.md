# ScrapeX Scraper Usage Guide

Quick reference for using the FinalScraper with browser automation.

---

## 🚀 Quick Start

### Python Usage

```python
from final_scraper import FinalScraper

# Initialize scraper
scraper = FinalScraper()

# Scrape a website
result = scraper.scrape_facility_website("https://example.com")

# Check result
if result['status'] == 'success':
    print(f"Phone: {result['phone']}")
    print(f"Email: {result['email']}")
    print(f"Method: {result['scraping_method']}")
elif result['manual_required']:
    print(f"Manual entry needed: {result['message']}")
```

### API Usage

```bash
# Scrape a single facility
curl -X POST https://scrapex-backend.onrender.com/api/v1/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.ocnjirrigation.com/"}'
```

---

## 📊 Response Format

### Successful Scrape

```json
{
  "url": "https://www.ocnjirrigation.com/",
  "scraped_at": "2026-01-12T17:44:34.920562",
  "scraping_method": "browser_automation",
  "status": "success",
  "manual_required": false,
  "facility_name": "Sprinkler Services in Ocean City, NJ",
  "phone": ["(609) 628-3103"],
  "email": "admin@ocnjirrigation.com",
  "address": null,
  "hours": {
    "raw": "Mon - Fri 8:00 am - 5:00 pm"
  },
  "services": ["Irrigation", "Repair", "Maintenance"]
}
```

### Manual Required (Bot Protection)

```json
{
  "url": "https://example.com",
  "status": "blocked",
  "scraping_method": "manual_required",
  "manual_required": true,
  "message": "This website has advanced bot protection. Please manually verify the contact information.",
  "phone": [],
  "email": null,
  "facility_name": null,
  "scraped_at": "2026-01-12T17:44:41.027929"
}
```

---

## 🔍 Scraping Methods

### 1. HTTP Request (Default, Fast)

**When it's used:**
- First attempt for all URLs
- Fastest method (< 1 second)

**Success rate:** ~70%

**Example:**
```python
result = scraper._try_http_scrape("https://example.com")
```

### 2. Browser Automation (Fallback)

**When it's used:**
- HTTP request fails or returns no data
- Automatically triggered

**Success rate:** ~95%

**Example:**
```python
result = scraper._try_browser_scrape("https://example.com")
```

### 3. Manual Fallback (Last Resort)

**When it's used:**
- Both HTTP and browser fail
- Enterprise bot protection detected

**Success rate:** 100% (with user input)

---

## 🎯 Field Extraction

### Phone Numbers

**Formats supported:**
- `(609) 628-3103`
- `609-628-3103`
- `609.628.3103`
- `+1 609 628 3103`
- `tel:+16096283103`

**Extraction logic:**
1. Search HTML for `tel:` links
2. Regex pattern matching in text
3. Returns up to 5 unique numbers

### Email Addresses

**Formats supported:**
- Standard email format: `name@domain.com`

**Extraction logic:**
1. Search for `mailto:` links
2. Regex pattern matching in text
3. Returns first valid email found

### Business Hours

**Extraction logic:**
1. Search for elements with class containing "hours" or "schedule"
2. Extract text content
3. Returns raw text (up to 500 chars)

### Services

**Extraction logic:**
1. Search page text for healthcare-related keywords
2. Keywords: emergency, consultation, installation, repair, maintenance, etc.
3. Returns up to 10 unique services

---

## ⚙️ Configuration

### Timeouts

```python
scraper.timeout = 15  # HTTP timeout in seconds
```

Browser timeout is fixed at 20 seconds.

### User Agent

Default user agent mimics Chrome on Windows:
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
```

---

## 🐛 Troubleshooting

### Issue: "Playwright not available"

**Solution:**
```bash
pip install playwright
playwright install chromium
```

### Issue: Browser automation fails

**Possible causes:**
1. Insufficient memory (need 200-300MB per browser)
2. Chromium not installed
3. Timeout too short

**Solution:**
```bash
# Reinstall Playwright browsers
playwright install --force chromium
```

### Issue: All methods return "blocked"

**Solution:**
- Website has enterprise-grade bot protection
- Use manual fallback
- Consider residential proxies for production

---

## 📈 Performance Tips

### 1. Batch Processing

For multiple URLs, process in batches:

```python
urls = ["https://site1.com", "https://site2.com", ...]

results = []
for url in urls:
    result = scraper.scrape_facility_website(url)
    results.append(result)
```

### 2. Caching

Cache results to avoid redundant scraping:

```python
cache = {}

def scrape_with_cache(url):
    if url in cache:
        return cache[url]
    
    result = scraper.scrape_facility_website(url)
    cache[url] = result
    return result
```

### 3. Concurrent Scraping

Use threading for concurrent scraping (be careful with memory):

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=2) as executor:
    results = list(executor.map(scraper.scrape_facility_website, urls))
```

**Note:** Limit concurrent browsers to 2-3 on Starter plan (512MB RAM).

---

## 🔒 Security Best Practices

### 1. Validate URLs

```python
from urllib.parse import urlparse

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# Use before scraping
if is_valid_url(url):
    result = scraper.scrape_facility_website(url)
```

### 2. Rate Limiting

```python
import time

last_request = 0
min_interval = 1  # seconds

def scrape_with_rate_limit(url):
    global last_request
    
    elapsed = time.time() - last_request
    if elapsed < min_interval:
        time.sleep(min_interval - elapsed)
    
    result = scraper.scrape_facility_website(url)
    last_request = time.time()
    return result
```

### 3. Error Handling

```python
try:
    result = scraper.scrape_facility_website(url)
    
    if result['status'] == 'success':
        # Process data
        pass
    elif result['manual_required']:
        # Request manual input
        pass
    else:
        # Log error
        print(f"Error: {result.get('error')}")
        
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## 📊 Monitoring

### Log Levels

```python
import logging

# Set log level
logging.basicConfig(level=logging.INFO)

# Logs will show:
# INFO: Scraping https://example.com
# INFO: Trying browser automation
# WARNING: HTTP scrape failed: 403 Forbidden
# INFO: Browser scrape successful
```

### Metrics to Track

1. **Success rate by method:**
   - HTTP success rate
   - Browser success rate
   - Manual fallback rate

2. **Performance:**
   - Average scraping time
   - Memory usage
   - Error rate

3. **Coverage:**
   - Phone numbers found
   - Emails found
   - Complete data rate

---

## 🎓 Examples

### Example 1: Basic Scraping

```python
from final_scraper import FinalScraper

scraper = FinalScraper()
result = scraper.scrape_facility_website("https://www.ocnjirrigation.com/")

print(f"Facility: {result['facility_name']}")
print(f"Phone: {result['phone']}")
print(f"Method: {result['scraping_method']}")
```

### Example 2: Bulk Scraping

```python
urls = [
    "https://www.ocnjirrigation.com/",
    "https://example.com",
    "https://another-site.com"
]

for url in urls:
    result = scraper.scrape_facility_website(url)
    
    if result['manual_required']:
        print(f"⚠️  {url} requires manual entry")
    else:
        print(f"✅ {url}: {result['phone']}")
```

### Example 3: API Integration

```python
from fastapi import FastAPI
from final_scraper import FinalScraper

app = FastAPI()
scraper = FinalScraper()

@app.post("/scrape")
async def scrape_endpoint(url: str):
    result = scraper.scrape_facility_website(url)
    return result
```

---

## 📞 Support

**Issues or questions?**
- Check logs for detailed error messages
- Review the troubleshooting section above
- Consult PLAYWRIGHT_IMPLEMENTATION_COMPLETE.md for technical details

**GitHub:** https://github.com/dganthonyjr1/ScrapeX-backend

---

**Last Updated:** January 12, 2026  
**Version:** 1.0.0
