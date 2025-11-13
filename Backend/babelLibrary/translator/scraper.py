"""
Web scraping module for Korean novel websites.
Adapted from Rosetta project for Django integration.
Uses curl_cffi to bypass Cloudflare protection.
"""
from bs4 import BeautifulSoup
from typing import Dict, Optional, List
import logging
import time
import requests
import json

logger = logging.getLogger(__name__)

# FlareSolverr endpoint
FLARESOLVERR_URL = "http://localhost:8191/v1"

# Session ID for FlareSolverr
_flaresolverr_session = None


def _get_flaresolverr_session():
    """
    Gets or creates a FlareSolverr session.
    """
    global _flaresolverr_session
    if _flaresolverr_session is None:
        # Create a new session in FlareSolverr
        try:
            response = requests.post(
                FLARESOLVERR_URL,
                json={"cmd": "sessions.create"},
                timeout=10
            )
            data = response.json()
            _flaresolverr_session = data.get('session')
            logger.info(f"Created FlareSolverr session: {_flaresolverr_session}")
        except Exception as e:
            logger.warning(f"Could not create FlareSolverr session: {e}")
    return _flaresolverr_session


def _fetch_page_content(url: str, wait_for_selector: Optional[str] = None, retry_count: int = 0) -> str:
    """
    Fetches page content using FlareSolverr to bypass Cloudflare.
    
    Args:
        url: The URL to fetch
        wait_for_selector: Not used but kept for API compatibility
        
    Returns:
        HTML content of the page
        
    Raises:
        Exception: If page fails to load
    """
    session_id = _get_flaresolverr_session()
    
    try:
        logger.info(f"Fetching via FlareSolverr: {url}")
        
        # Request FlareSolverr to fetch the page
        payload = {
            "cmd": "request.get",
            "url": url,
            "maxTimeout": 60000
        }
        
        # Add session if available
        if session_id:
            payload["session"] = session_id
        
        response = requests.post(
            FLARESOLVERR_URL,
            json=payload,
            timeout=70  # Slightly longer than maxTimeout
        )
        
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
            raise Exception(f"FlareSolverr error: {error_msg}")
            
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        raise


def cleanup_browser():
    """
    Cleanup FlareSolverr session. Call this when shutting down the application.
    """
    global _flaresolverr_session
    
    if _flaresolverr_session:
        try:
            requests.post(
                FLARESOLVERR_URL,
                json={"cmd": "sessions.destroy", "session": _flaresolverr_session},
                timeout=10
            )
            logger.info(f"Destroyed FlareSolverr session: {_flaresolverr_session}")
        except Exception as e:
            logger.warning(f"Could not destroy FlareSolverr session: {e}")
        _flaresolverr_session = None


def scrape_novel_page(url: str) -> Dict[str, Optional[str]]:
    """
    Scrapes a Korean novel page and extracts key information.
    
    Args:
        url: The URL of the novel page to scrape
        
    Returns:
        Dictionary containing Title, Author, Genre, and Description
    """
    try:
        # Fetch page content using Playwright
        logger.info(f"Fetching novel page: {url}")
        html_content = _fetch_page_content(url, wait_for_selector='.view-title')
        
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
        
    except Exception as e:
        logger.error(f"Error scraping novel page {url}: {e}")
        error_result: Dict[str, Optional[str]] = {
            'Title': None,
            'Author': None,
            'Genre': None,
            'Description': f"Error: {str(e)}",
            'Cover_Image': None
        }
        return error_result


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
        # Fetch page content using Playwright
        logger.info(f"Fetching chapter page: {url}")
        html_content = _fetch_page_content(url, wait_for_selector='#novel_content')
        
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
        
    except Exception as e:
        logger.error(f"Error scraping chapter page {url}: {e}")
        error_result: Dict[str, Optional[str]] = {
            'Chapter Title': None,
            'Chapter Content': f"Error: {str(e)}"
        }
        return error_result


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
        html_content = _fetch_page_content(url, wait_for_selector='ul.list-body')
        
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
        
    except Exception as e:
        logger.error(f"Error getting chapter pages from {url}: {e}")
        return []
