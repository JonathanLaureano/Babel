"""
URL validation and SSRF (Server-Side Request Forgery) protection.

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
from urllib.parse import urlparse
import logging
import ipaddress
import socket

from .config import DOMAIN_PATTERN, ALLOWED_DOMAINS

logger = logging.getLogger(__name__)


def _is_valid_domain(domain: str) -> bool:
    """Check if a domain name is properly formatted.
    
    Args:
        domain: Domain name to validate
        
    Returns:
        True if domain is valid, False otherwise
    """
    if not domain or not isinstance(domain, str):
        return False
    
    # Check length (max 253 characters for full domain)
    if len(domain) > 253:
        return False
    
    # Check for invalid characters (spaces, etc.)
    if ' ' in domain or '\t' in domain or '\n' in domain:
        return False
    
    # Validate against RFC 1035/1123 pattern
    return DOMAIN_PATTERN.match(domain) is not None


def _is_safe_ip(ip_str: str) -> bool:
    """Check if an IP address is safe to connect to (not private/internal).
    
    Args:
        ip_str: IP address string to check
        
    Returns:
        True if IP is public and safe, False if private/internal
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        
        # Block private IP ranges (SSRF protection)
        if ip.is_private:
            return False
        
        # Block loopback addresses (127.0.0.0/8, ::1)
        if ip.is_loopback:
            return False
        
        # Block link-local addresses (169.254.0.0/16, fe80::/10)
        if ip.is_link_local:
            return False
        
        # Block reserved addresses
        if ip.is_reserved:
            return False
        
        # Block multicast addresses
        if ip.is_multicast:
            return False
        
        return True
    except ValueError:
        # Invalid IP address
        return False


def validate_url(url: str) -> None:
    """Validates URL format, domain whitelist, and blocks SSRF attempts.
    
    Args:
        url: The URL to validate
        
    Raises:
        ValueError: If URL is invalid, domain not allowed, or targets private network
        
    Security Note - TOCTOU (Time-of-Check-Time-of-Use) Limitation:
        DNS resolution is checked at validation time, but DNS could change between
        validation and when FlareSolverr makes the actual request (DNS rebinding attack).
        
        Example attack scenario:
        1. Attacker's DNS initially returns safe IP: 1.2.3.4
        2. This validation passes
        3. Attacker's DNS quickly changes to private IP: 192.168.1.1
        4. FlareSolverr makes request to private IP
        
        Mitigations in place:
        - Domain whitelist (when configured) limits attack surface
        - Multiple DNS resolution checks reduce attack window
        - FlareSolverr should be configured with its own SSRF protections
        
        Additional recommended protections:
        - Set SCRAPER_ALLOWED_DOMAINS to trusted domains only (production)
        - Configure FlareSolverr with network isolation/firewall rules
        - Run FlareSolverr in container with restricted network access
        - Use DNS pinning in FlareSolverr configuration if available
        - Monitor FlareSolverr logs for suspicious activity
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid URL format: {str(e)}")
    
    # Check for valid scheme
    if parsed.scheme not in ('http', 'https'):
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}. Only http and https are allowed")
    
    # Check for valid netloc (domain)
    if not parsed.netloc:
        raise ValueError("URL must contain a valid domain")
    
    # Extract hostname (remove port if present)
    hostname = parsed.netloc.split(':')[0]
    
    # Validate hostname format (unless it's an IP address)
    # IP addresses will be checked separately below
    try:
        # Try parsing as IP - if it works, skip domain validation
        ipaddress.ip_address(hostname)
    except ValueError:
        # Not an IP, validate as domain name
        if not _is_valid_domain(hostname):
            raise ValueError(
                f"Invalid domain name format: '{hostname}'. "
                f"Domain must contain only letters, digits, hyphens, and dots. "
                f"Each label must be 1-63 characters and cannot start or end with a hyphen."
            )
    
    # SSRF Protection: Block requests to private/internal IP addresses
    # First, check if hostname is already an IP address
    try:
        ip = ipaddress.ip_address(hostname)
        if not _is_safe_ip(str(ip)):
            raise ValueError(
                f"Access to private/internal IP addresses is blocked for security reasons: {hostname}"
            )
    except ValueError:
        # Not an IP address, it's a hostname - need to resolve it
        # NOTE: TOCTOU vulnerability - DNS could change between this check and 
        # FlareSolverr's actual request (DNS rebinding attack). Domain whitelist
        # is the primary defense; this check reduces but doesn't eliminate risk.
        try:
            # Resolve hostname to IP addresses
            addr_info = socket.getaddrinfo(hostname, None)
            for info in addr_info:
                # info[4] is (address, port) tuple - get address only
                ip_address_str = str(info[4][0])
                if not _is_safe_ip(ip_address_str):
                    raise ValueError(
                        f"Domain '{hostname}' resolves to private/internal IP address ({ip_address_str}), "
                        "which is blocked for security reasons (SSRF protection)"
                    )
        except socket.gaierror as e:
            # DNS resolution failed
            raise ValueError(f"Cannot resolve domain '{hostname}': {str(e)}")
        except ValueError as e:
            # Re-raise ValueError from IP check
            raise
        except Exception as e:
            # Other DNS/network errors during IP validation
            # SECURITY: If no whitelist is configured, we MUST fail securely
            # Cannot skip SSRF validation when it's the only protection layer
            if ALLOWED_DOMAINS is None:
                raise ValueError(
                    f"Cannot validate IP addresses for domain '{hostname}' due to DNS/network error: {str(e)}. "
                    f"Blocking request for security (SSRF protection). "
                    f"To allow this domain, configure SCRAPER_ALLOWED_DOMAINS in settings."
                )
            # If whitelist is configured, it will validate the domain below
            # Log the DNS error but allow whitelist check to proceed
            logger.warning(
                f"Error checking IP for domain '{hostname}': {e}. "
                f"Proceeding with domain whitelist validation."
            )
    
    # Check domain whitelist if configured
    if ALLOWED_DOMAINS is not None:
        # Check if domain or any parent domain is in whitelist
        allowed = False
        for allowed_domain in ALLOWED_DOMAINS:
            if hostname == allowed_domain or hostname.endswith(f'.{allowed_domain}'):
                allowed = True
                break
        
        if not allowed:
            raise ValueError(
                f"Domain '{hostname}' is not in the allowed domains list. "
                f"Allowed domains: {', '.join(ALLOWED_DOMAINS)}"
            )
    
    logger.debug(f"URL validation passed: {url}")
