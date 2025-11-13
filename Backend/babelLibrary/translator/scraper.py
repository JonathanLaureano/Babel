"""
Web scraping module for Korean novel websites.
Adapted from Rosetta project for Django integration.
Uses FlareSolverr to bypass Cloudflare protection.
"""
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
from django.conf import settings
from django.core.signals import request_finished
from django.dispatch import receiver
from urllib.parse import urlparse
import logging
import requests
import threading
import atexit

logger = logging.getLogger(__name__)

# FlareSolverr endpoint - configurable via Django settings
FLARESOLVERR_URL = getattr(settings, 'FLARESOLVERR_URL', 'http://localhost:8191/v1')

# Optional domain whitelist - set in Django settings as SCRAPER_ALLOWED_DOMAINS
# Example: SCRAPER_ALLOWED_DOMAINS = ['booktoki469.com', 'example.com']
ALLOWED_DOMAINS = getattr(settings, 'SCRAPER_ALLOWED_DOMAINS', None)

# Thread-local storage for FlareSolverr sessions
_thread_local = threading.local()


def _validate_url(url: str) -> None:
    """Validates URL format and domain whitelist.
    
    Args:
        url: The URL to validate
        
    Raises:
        ValueError: If URL is invalid or domain not allowed
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
    
    # Check domain whitelist if configured
    if ALLOWED_DOMAINS is not None:
        # Extract domain from netloc (remove port if present)
        domain = parsed.netloc.split(':')[0]
        
        # Check if domain or any parent domain is in whitelist
        allowed = False
        for allowed_domain in ALLOWED_DOMAINS:
            if domain == allowed_domain or domain.endswith(f'.{allowed_domain}'):
                allowed = True
                break
        
        if not allowed:
            raise ValueError(
                f"Domain '{domain}' is not in the allowed domains list. "
                f"Allowed domains: {', '.join(ALLOWED_DOMAINS)}"
            )
    
    logger.debug(f"URL validation passed: {url}")


def _create_flaresolverr_session():
    """Creates a new FlareSolverr session.
    
    Returns:
        Session ID string
        
    Raises:
        ConnectionError: If FlareSolverr is not running or unreachable
    """
    try:
        response = requests.post(
            FLARESOLVERR_URL,
            json={"cmd": "sessions.create"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        session_id = data.get('session')
        logger.info(f"Created FlareSolverr session: {session_id}")
        return session_id
    except requests.exceptions.ConnectionError as e:
        error_msg = (
            f"Cannot connect to FlareSolverr at {FLARESOLVERR_URL}. "
            "Please ensure FlareSolverr is running. "
            "See Docs/FLARESOLVERR.md for installation and setup instructions."
        )
        logger.error(error_msg)
        raise ConnectionError(error_msg) from e
    except requests.exceptions.Timeout as e:
        error_msg = (
            f"FlareSolverr at {FLARESOLVERR_URL} is not responding. "
            "Please check if the service is running properly."
        )
        logger.error(error_msg)
        raise TimeoutError(error_msg) from e
    except requests.exceptions.RequestException as e:
        error_msg = (
            f"Failed to communicate with FlareSolverr at {FLARESOLVERR_URL}: {str(e)}. "
            "Please verify FlareSolverr is installed and running correctly."
        )
        logger.error(error_msg)
        raise ConnectionError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error creating FlareSolverr session: {str(e)}"
        logger.error(error_msg)
        raise


def _get_flaresolverr_session():
    """Gets or creates a FlareSolverr session (thread-safe).
    
    Raises:
        ConnectionError: If FlareSolverr is not running or unreachable
    """
    # Get or initialize session for this thread
    if not hasattr(_thread_local, 'session'):
        _thread_local.session = None
    
    if _thread_local.session is None:
        _thread_local.session = _create_flaresolverr_session()
    
    return _thread_local.session


def _invalidate_session():
    """Invalidates the current thread's FlareSolverr session.
    
    Call this when a session becomes stale or invalid.
    """
    if hasattr(_thread_local, 'session'):
        logger.warning(f"Invalidating stale FlareSolverr session: {_thread_local.session}")
        _thread_local.session = None


def _fetch_page_content(url: str, retry_on_stale_session: bool = True) -> str:
    """Fetches page content using FlareSolverr to bypass Cloudflare.
    
    Args:
        url: The URL to fetch
        retry_on_stale_session: Whether to retry once if session is invalid
        
    Returns:
        HTML content of the page
        
    Raises:
        ValueError: If URL is invalid or domain not allowed
        ConnectionError: If FlareSolverr is not available
        Exception: If page fails to load or FlareSolverr returns an error
    """
    # Validate URL before processing
    _validate_url(url)
    
    session_id = _get_flaresolverr_session()
    
    try:
        logger.info(f"Fetching via FlareSolverr: {url}")
        
        # Request FlareSolverr to fetch the page
        payload = {
            "cmd": "request.get",
            "url": url,
            "maxTimeout": 30000
        }
        
        # Add session if available
        if session_id:
            payload["session"] = session_id
        
        response = requests.post(
            FLARESOLVERR_URL,
            json=payload,
            timeout=40  # Slightly longer than maxTimeout (30s) to account for network overhead
        )
        response.raise_for_status()
        
        data = response.json()
        
        if data.get('status') == 'ok':
            solution = data.get('solution', {})
            html = solution.get('response')
            if html:
                logger.info(f"Successfully fetched {url}")
                return html
            else:
                raise Exception("No HTML content in FlareSolverr response")
        else:
            error_msg = data.get('message', 'Unknown error')
            
            # Check if error indicates invalid session
            if 'session' in error_msg.lower() and retry_on_stale_session:
                logger.warning(f"Session appears invalid, recreating: {error_msg}")
                _invalidate_session()
                # Retry once with new session
                return _fetch_page_content(url, retry_on_stale_session=False)
            
            raise Exception(f"FlareSolverr returned an error: {error_msg}")
            
    except requests.exceptions.ConnectionError as e:
        error_msg = (
            f"Lost connection to FlareSolverr at {FLARESOLVERR_URL} while fetching {url}. "
            "Please ensure FlareSolverr is still running."
        )
        logger.error(error_msg)
        raise ConnectionError(error_msg) from e
    except requests.exceptions.Timeout as e:
        error_msg = (
            f"FlareSolverr timed out while fetching {url}. "
            "The website may be slow or FlareSolverr is overloaded."
        )
        logger.error(error_msg)
        raise TimeoutError(error_msg) from e
    except requests.exceptions.RequestException as e:
        error_msg = f"Network error while fetching {url} via FlareSolverr: {str(e)}"
        logger.error(error_msg)
        raise ConnectionError(error_msg) from e
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        raise


def cleanup_browser():
    """Cleanup FlareSolverr session for current thread.
    
    This is automatically called on request completion via Django signals
    and on application shutdown via atexit handler.
    """
    # Get session for this thread
    if not hasattr(_thread_local, 'session'):
        return
    
    if _thread_local.session:
        try:
            response = requests.post(
                FLARESOLVERR_URL,
                json={"cmd": "sessions.destroy", "session": _thread_local.session},
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Destroyed FlareSolverr session: {_thread_local.session}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not destroy FlareSolverr session: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error destroying FlareSolverr session: {e}")
        finally:
            _thread_local.session = None


# Django signal handler to cleanup sessions after request completion
@receiver(request_finished)
def cleanup_session_on_request_finished(sender, **kwargs):
    """Clean up FlareSolverr session when Django request finishes."""
    cleanup_browser()


# Register cleanup on application shutdown
atexit.register(cleanup_browser)


class FlareSolverrSession:
    """Context manager for explicit FlareSolverr session management.
    
    Usage:
        with FlareSolverrSession():
            # Session is automatically created and cleaned up
            result = scrape_novel_page(url)
    """
    
    def __enter__(self):
        """Enter context - session will be created on first use."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - cleanup session."""
        cleanup_browser()
        return False  # Don't suppress exceptions


def scrape_novel_page(url: str) -> Dict[str, Optional[str]]:
    """
    Scrapes a Korean novel page and extracts key information.
    
    Args:
        url: The URL of the novel page to scrape
        
    Returns:
        Dictionary containing Title, Author, Genre, and Description
    """
    try:
        # Fetch page content using FlareSolverr
        logger.info(f"Fetching novel page: {url}")
        html_content = _fetch_page_content(url)
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract information for Novel site
        result: Dict[str, Optional[str]] = {
            'Title': None,
            'Author': None,
            'Genre': None,
            'Description': None,
            'Cover_Image': None
        }
        
        # Title - located in view-content with font-size 20px
        title_elem = soup.select_one('.view-title .col-sm-8 .view-content span b')
        if title_elem:
            result['Title'] = title_elem.get_text(strip=True)
        
        # Find the view-content div that contains author, genre, and publisher info
        info_div = soup.select_one('.view-title .col-sm-8 div.view-content[style*="color: #666666"]')
        if info_div:
            
            # Extract Author (after fa-user icon)
            author_icon = info_div.find('i', class_='fa-user')
            if author_icon:
                # Get the text after the author icon
                author_text = author_icon.next_sibling
                if author_text:
                    result['Author'] = author_text.strip()
            
            # Extract Genre (after fa-tag icon)
            genre_icon = info_div.find('i', class_='fa-tag')
            if genre_icon:
                # Get text between fa-tag and the next element
                genre_text = genre_icon.next_sibling
                if genre_text:
                    result['Genre'] = genre_text.strip()
        
        # Description - the next view-content div after the info div
        desc_divs = soup.select('.view-title .col-sm-8 .view-content')
        for div in desc_divs:
            text = div.get_text(strip=True)
            # Skip the title and info divs, get the description
            if text and text != result['Title'] and not div.get('style'):
                result['Description'] = text
                break
        
        # Cover Image - extract from og:image meta tag
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            result['Cover_Image'] = og_image.get('content')
        
        logger.info(f"Successfully scraped novel page: {result.get('Title', 'Unknown')}")
        return result
        
    except (ConnectionError, TimeoutError, ValueError) as e:
        # Network/validation errors - log and re-raise to allow caller to handle
        logger.error(f"Error scraping novel page {url}: {e}")
        raise
    except Exception as e:
        # Unexpected errors - log full traceback and re-raise
        logger.exception(f"Unexpected error scraping novel page {url}: {e}")
        raise


def scrape_chapter_page(url: str) -> Dict[str, Optional[str]]:
    """
    Scrapes a Korean novel chapter page and extracts key information.
    
    Args:
        url: The URL of the chapter page to scrape
        
    Returns:
        Dictionary containing Chapter Title and Chapter Content
        Note: Chapter number is no longer extracted from the page
    """
    try:
        # Fetch page content using FlareSolverr
        logger.info(f"Fetching chapter page: {url}")
        html_content = _fetch_page_content(url)
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        result: Dict[str, Optional[str]] = {
            'Chapter Title': None,
            'Chapter Content': None
        }
        
        # Extract chapter content from the div with id="novel_content"
        novel_content = soup.select_one('#novel_content')
        if novel_content:
            # Find all direct child divs and look for one with paragraphs (skip view-img)
            for div in novel_content.find_all('div', recursive=False):
                classes = div.get('class', [])
                # Skip the view-img div
                if classes and 'view-img' not in classes:
                    # Get all paragraph tags
                    paragraphs = div.find_all('p')
                    if paragraphs:
                        first_para_text = paragraphs[0].get_text(strip=True)
                        
                        # Check if first paragraph looks like a chapter title
                        # A title typically contains "화" (chapter marker) and is short
                        if '화' in first_para_text and len(first_para_text) < 100:
                            # First paragraph is the title
                            result['Chapter Title'] = first_para_text
                            # Join remaining paragraphs (skip the title)
                            content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs[1:])
                        else:
                            # No clear title found - keep all content including first paragraph
                            result['Chapter Title'] = None
                            content = '\n\n'.join(p.get_text(strip=True) for p in paragraphs)
                        
                        result['Chapter Content'] = content
                        break
        
        logger.info(f"Successfully scraped chapter: {result.get('Chapter Title', 'No title')}")
        return result
        
    except (ConnectionError, TimeoutError, ValueError) as e:
        # Network/validation errors - log and re-raise to allow caller to handle
        logger.error(f"Error scraping chapter page {url}: {e}")
        raise
    except Exception as e:
        # Unexpected errors - log full traceback and re-raise
        logger.exception(f"Unexpected error scraping chapter page {url}: {e}")
        raise


def get_chapter_pages(url: str, limit: int = 5, start_from: int = 1) -> List[Dict[str, str]]:
    """
    Extracts chapter page links from a novel page.
    
    Args:
        url: The URL of the novel page (with full chapter list)
        limit: Maximum number of chapters to return (default: 5)
        start_from: Chapter number to start from (default: 1)
        
    Returns:
        List of dictionaries containing chapter information:
        - 'number': Auto-incremented chapter number starting from start_from
        - 'url': Full URL to the chapter page
    """
    try:
        # Fetch page content
        logger.info(f"Fetching chapter list from: {url}")
        html_content = _fetch_page_content(url)
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find the chapter list (ul.list-body)
        list_body = soup.find('ul', class_='list-body')
        
        if not list_body:
            logger.error("Could not find chapter list on the page")
            return []
        
        # Find all chapter list items
        list_items = list_body.find_all('li', class_='list-item')
        
        # Reverse the list to go from earliest (chapter 1) to latest
        list_items = list(reversed(list_items))
        
        # Build chapter list with auto-incremented numbers
        chapters = []
        chapter_counter = start_from
        
        # Skip to the starting position (start_from - 1 items)
        items_to_skip = start_from - 1
        for idx, item in enumerate(list_items):
            # Skip items before start_from
            if idx < items_to_skip:
                continue
            
            # Stop if we've collected enough chapters
            if len(chapters) >= limit:
                break
            
            # Find the chapter link
            link = item.find('a', class_='item-subject')
            if link:
                chapter_url = link.get('href')
                
                # Make sure URL is absolute
                if chapter_url and not chapter_url.startswith('http'):
                    # Extract base URL
                    from urllib.parse import urljoin
                    chapter_url = urljoin(url, chapter_url)
                
                chapters.append({
                    'number': str(chapter_counter),
                    'url': chapter_url
                })
                chapter_counter += 1
        
        logger.info(f"Found {len(chapters)} chapters to process (starting from chapter {start_from})")
        return chapters
        
    except (ConnectionError, TimeoutError, ValueError) as e:
        # Network/validation errors - log and re-raise to allow caller to handle
        logger.error(f"Error getting chapter pages from {url}: {e}")
        raise
    except Exception as e:
        # Unexpected errors - log full traceback and re-raise
        logger.exception(f"Unexpected error getting chapter pages from {url}: {e}")
        raise
