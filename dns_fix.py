"""
DNS Resolution Fix for Render Deployment
Adds proper DNS configuration and retry logic
"""

import socket
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger(__name__)


def configure_dns_session():
    """
    Configure requests session with proper DNS resolution and retry logic
    """
    # Force DNS resolution using system resolver
    socket.setdefaulttimeout(30)
    
    # Create session with retry logic
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    
    # Mount adapter with retry strategy
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # Set headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    })
    
    return session


def test_dns_resolution(url: str) -> bool:
    """
    Test if DNS resolution works for a given URL
    """
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        hostname = parsed.netloc or parsed.path
        
        # Try to resolve hostname
        socket.gethostbyname(hostname)
        logger.info(f"DNS resolution successful for {hostname}")
        return True
    except socket.gaierror as e:
        logger.error(f"DNS resolution failed for {hostname}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during DNS test: {e}")
        return False
