"""
FlareSolverr session management and page fetching.

This module handles communication with FlareSolverr to bypass Cloudflare protection.
Includes thread-safe session management and automatic cleanup.
"""
from django.core.signals import request_finished
from django.dispatch import receiver
import logging
import requests
import threading
import atexit
import json

from .config import FLARESOLVERR_URL, FLARESOLVERR_TIMEOUT_MS, NETWORK_OVERHEAD_TIMEOUT_SECONDS
from .validation import validate_url

logger = logging.getLogger(__name__)

# Thread-local storage for FlareSolverr sessions
_thread_local = threading.local()

# Lock for thread-safe cleanup operations
_cleanup_lock = threading.Lock()

# Track sessions being cleaned up to prevent double cleanup
_cleaning_sessions = set()


def _create_flaresolverr_session():
    """Creates a new FlareSolverr session.
    
    Returns:
        Session ID string
        
    Raises:
        ConnectionError: If FlareSolverr is not running or unreachable
        TimeoutError: If FlareSolverr does not respond within timeout period
        ValueError: If FlareSolverr returns invalid JSON or missing session ID
    """
    try:
        response = requests.post(
            FLARESOLVERR_URL,
            json={"cmd": "sessions.create"},
            timeout=10
        )
        response.raise_for_status()
        
        # Parse JSON response with error handling
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            error_msg = (
                f"FlareSolverr returned invalid JSON response. "
                f"This may indicate FlareSolverr is misconfigured or not running properly. "
                f"Response text: {response.text[:200]}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg) from e
        
        session_id = data.get('session')
        if not session_id:
            raise ValueError(f"FlareSolverr response missing session ID. Response: {data}")
        
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
        TimeoutError: If FlareSolverr does not respond within timeout period
        ValueError: If FlareSolverr returns invalid JSON or missing session ID
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


def fetch_page_content(url: str, retry_on_stale_session: bool = True) -> str:
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
    validate_url(url)
    
    session_id = _get_flaresolverr_session()
    
    try:
        logger.info(f"Fetching via FlareSolverr: {url}")
        
        # Request FlareSolverr to fetch the page
        payload = {
            "cmd": "request.get",
            "url": url,
            "maxTimeout": FLARESOLVERR_TIMEOUT_MS
        }
        
        # Add session if available
        if session_id:
            payload["session"] = session_id
        
        response = requests.post(
            FLARESOLVERR_URL,
            json=payload,
            timeout=payload["maxTimeout"]/1000 + NETWORK_OVERHEAD_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        
        # Parse JSON response with error handling
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            error_msg = (
                f"FlareSolverr returned invalid JSON response for {url}. "
                f"This may indicate FlareSolverr is misconfigured or crashed. "
                f"Response status: {response.status_code}, "
                f"Response text: {response.text[:200]}"
            )
            logger.error(error_msg)
            raise ValueError(error_msg) from e
        
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
                return fetch_page_content(url, retry_on_stale_session=False)
            
            if not retry_on_stale_session:
                logger.error(f"Retry after session recreation failed for {url}: {error_msg}")
            
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
    and on application shutdown via atexit handler. Thread-safe to prevent
    race conditions and double cleanup.
    """
    # Get session for this thread (outside lock for performance)
    if not hasattr(_thread_local, 'session'):
        return
    
    session_id = _thread_local.session
    if not session_id:
        return
    
    # Thread-safe check-and-set to prevent double destruction
    # Uses a lock to ensure atomicity of the check + add operation
    with _cleanup_lock:
        # CRITICAL: Check again inside the lock (double-checked locking pattern)
        # Even though we checked session_id above, another thread could have:
        # 1. Started cleaning this session
        # 2. Or even the same thread could be re-entering due to signal/atexit race
        if session_id in _cleaning_sessions:
            logger.debug(f"Session {session_id} already being cleaned up, skipping")
            return
        
        # Also verify the thread-local session hasn't been cleared by another call
        # This handles edge cases where cleanup_browser() is called multiple times
        # on the same thread before the first call completes
        if not hasattr(_thread_local, 'session') or _thread_local.session != session_id:
            logger.debug(f"Session {session_id} already cleared from thread-local storage")
            return
        
        # Atomically mark session as being cleaned up
        # This prevents any other thread from entering cleanup for this session_id
        _cleaning_sessions.add(session_id)
        
        # Clear thread-local reference immediately while holding the lock
        # This prevents re-entry on the same thread
        _thread_local.session = None
    
    # Use try-finally to guarantee cleanup set is pruned even on catastrophic failure
    try:
        # Perform cleanup outside lock to avoid holding it during network call
        try:
            response = requests.post(
                FLARESOLVERR_URL,
                json={"cmd": "sessions.destroy", "session": session_id},
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Destroyed FlareSolverr session: {session_id}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not destroy FlareSolverr session {session_id}: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error destroying FlareSolverr session {session_id}: {e}")
    finally:
        # ALWAYS remove from cleaning set, even if something catastrophic happened
        # This ensures the session ID doesn't remain stuck in the set indefinitely
        with _cleanup_lock:
            _cleaning_sessions.discard(session_id)


# Django signal handler to cleanup sessions after request completion
@receiver(request_finished)
def cleanup_session_on_request_finished(sender, **kwargs):
    """Clean up FlareSolverr session when Django request finishes."""
    cleanup_browser()


# Register cleanup on application shutdown
atexit.register(cleanup_browser)


class FlareSolverrSession:
    """Context manager for explicit FlareSolverr session management.
    
    Creates a new FlareSolverr session on entry and guarantees cleanup on exit.
    Useful for isolating session lifecycle in specific code blocks.
    
    Usage:
        with FlareSolverrSession():
            # Fresh session is created and ready to use
            result = scrape_novel_page(url)
            # Session is automatically cleaned up after this block
    
    Note: For normal Django request/response cycles, sessions are managed
    automatically via signals. Use this context manager when you need explicit
    control over session lifecycle (e.g., in background tasks, scripts).
    """
    
    def __init__(self):
        """Initialize context manager."""
        self._old_session = None
    
    def __enter__(self):
        """Enter context - create new session immediately.
        
        Returns:
            self for context manager protocol
        """
        # Save any existing session for this thread
        self._old_session = getattr(_thread_local, 'session', None)
        
        # Force creation of a new session
        try:
            session_id = _create_flaresolverr_session()
            _thread_local.session = session_id
            logger.debug(f"Created FlareSolverr session in context manager: {session_id}")
        except Exception as e:
            logger.error(f"Failed to create FlareSolverr session in context manager: {e}")
            raise
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - cleanup session created by this context manager.
        
        Args:
            exc_type: Exception type if raised in context
            exc_val: Exception value if raised in context
            exc_tb: Exception traceback if raised in context
            
        Returns:
            False to propagate any exceptions
        """
        try:
            cleanup_browser()
        finally:
            # Restore previous session (if any) for this thread
            _thread_local.session = self._old_session
        
        return False  # Don't suppress exceptions
