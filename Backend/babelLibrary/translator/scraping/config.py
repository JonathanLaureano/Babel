"""
Configuration and constants for the web scraping module.
"""
from django.conf import settings
import logging
import re

logger = logging.getLogger(__name__)

# Regex for validating domain names (RFC 1035/1123 compliant)
# Allows letters, digits, hyphens; labels 1-63 chars; no leading/trailing hyphens
DOMAIN_PATTERN = re.compile(
    r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*'
    r'[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
)

# FlareSolverr endpoint - configurable via Django settings (from FLARESOLVERR_URL env var)
FLARESOLVERR_URL = getattr(settings, 'FLARESOLVERR_URL', 'http://localhost:8191/v1')

# FlareSolverr request timeout in milliseconds (30 seconds)
# This is the maximum time FlareSolverr will wait for a page to load
FLARESOLVERR_TIMEOUT_MS = 30000

# Domain whitelist for SSRF protection - configured via environment variable
# Set via: SCRAPER_ALLOWED_DOMAINS=domain1.com,domain2.com,domain3.com
# In Django settings.py, this is parsed from the environment variable automatically
# Must be None to disable domain filtering, or a non-empty list of domain strings.
# 
# Configuration Examples:
#   Environment Variable: SCRAPER_ALLOWED_DOMAINS=example.com,sub.example.com
#   Django Setting: SCRAPER_ALLOWED_DOMAINS = ['example.com', 'sub.example.com']
#
# SECURITY WARNING: When None (default), any public URL can be scraped. For production,
# strongly recommend setting a whitelist to prevent SSRF attacks.
# 
# See Docs/FLARESOLVERR.md for detailed configuration and security guidance.
ALLOWED_DOMAINS = getattr(settings, 'SCRAPER_ALLOWED_DOMAINS', None)

# Validate allowed domains configuration
if ALLOWED_DOMAINS is not None:
    if not isinstance(ALLOWED_DOMAINS, list) or not ALLOWED_DOMAINS:
        raise ValueError(
            "SCRAPER_ALLOWED_DOMAINS must be None or a non-empty list of domain strings. "
            f"Got: {ALLOWED_DOMAINS!r}"
        )
    
    # Validate each domain format
    for domain in ALLOWED_DOMAINS:
        if not isinstance(domain, str) or not domain:
            raise ValueError(
                f"Each domain in SCRAPER_ALLOWED_DOMAINS must be a non-empty string. "
                f"Invalid domain: {domain!r}"
            )
        
        # Validate domain format (no spaces, valid characters, proper structure)
        if not DOMAIN_PATTERN.match(domain):
            raise ValueError(
                f"Invalid domain format in SCRAPER_ALLOWED_DOMAINS: '{domain}'. "
                f"Domains must contain only letters, digits, hyphens, and dots. "
                f"Each label must be 1-63 characters and cannot start or end with a hyphen. "
                f"Examples: 'example.com', 'sub.example.com', 'example-site.com'"
            )
else:
    # Warn if domain whitelist is disabled in production
    if not settings.DEBUG:
        logger.warning(
            "SECURITY WARNING: SCRAPER_ALLOWED_DOMAINS is not set. "
            "Any public URL can be scraped via FlareSolverr, which may be a security risk. "
            "Consider setting SCRAPER_ALLOWED_DOMAINS to a whitelist of trusted domains."
        )
