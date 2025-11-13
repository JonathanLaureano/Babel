"""
Web scraping module for Korean novel websites.
Adapted from Rosetta project for Django integration.
Uses FlareSolverr to bypass Cloudflare protection.

Security Considerations:
    This module implements multiple layers of SSRF (Server-Side Request Forgery)
    protection, including private IP blocking and domain whitelisting. However,
    there are inherent limitations:
    
    TOCTOU Vulnerability (Time-of-Check-Time-of-Use):
        DNS resolution can change between validation and actual request execution.
        An attacker could use DNS rebinding to bypass IP-based protections:
        - Initial DNS query returns safe public IP (passes validation)
        - DNS record changes to private IP with low TTL
        - FlareSolverr's request uses the new private IP
        
    Defense-in-Depth Strategy:
        1. Domain Whitelist: Set SCRAPER_ALLOWED_DOMAINS in production (primary defense)
        2. Private IP Blocking: Validates DNS at request time (reduces attack window)
        3. FlareSolverr Network Isolation: Run FlareSolverr with restricted network access
        4. Container Security: Use Docker network policies to limit FlareSolverr's access
        5. Monitoring: Log and monitor all scraping activity
        
    Deployment Recommendations:
        - REQUIRED: Set SCRAPER_ALLOWED_DOMAINS to trusted domains only
        - REQUIRED: Run FlareSolverr in isolated network environment
        - RECOMMENDED: Configure firewall rules blocking FlareSolverr from internal networks
        - RECOMMENDED: Use Docker network isolation for FlareSolverr container
        - RECOMMENDED: Monitor FlareSolverr logs for unusual access patterns
        
    See Docs/FLARESOLVERR.md for detailed security configuration.
"""

# Import public API
from .parsers import (
    scrape_novel_page,
    scrape_chapter_page,
    get_chapter_pages,
)

from .flaresolverr import (
    cleanup_browser,
    FlareSolverrSession,
)

# Export public API
__all__ = [
    'scrape_novel_page',
    'scrape_chapter_page',
    'get_chapter_pages',
    'cleanup_browser',
    'FlareSolverrSession',
]
