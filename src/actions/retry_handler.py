"""
RetryHandler — Exponential backoff retry decorator for external API calls.
All external calls (API, network, file I/O) must use this decorator.
"""
import logging
import time
from functools import wraps
from typing import Callable, Any, Tuple, Type

logger = logging.getLogger(__name__)


# Default retryable exceptions
DEFAULT_RETRYABLE_EXCEPTIONS = (
    ConnectionError,
    TimeoutError,
    OSError,
)


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retryable_exceptions: Tuple[Type[Exception], ...] = DEFAULT_RETRYABLE_EXCEPTIONS,
    log_level: int = logging.WARNING
):
    """
    Decorator for exponential backoff retry logic.

    Usage:
        @with_retry(max_attempts=3, base_delay=1, max_delay=60)
        def call_external_api():
            ...

    Args:
        max_attempts: Maximum number of retry attempts (total = 1 + retries)
        base_delay: Initial delay in seconds (1s)
        max_delay: Maximum delay cap (60s)
        retryable_exceptions: Tuple of exception types to retry on
        log_level: Logging level for retry attempts (WARNING by default)

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_attempts - 1:
                        # Last attempt failed
                        logger.error(
                            f"{func.__name__}: Max retries ({max_attempts}) exceeded. Last error: {e}",
                            exc_info=True
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (2 ** attempt), max_delay)

                    logger.log(
                        log_level,
                        f"{func.__name__}: Attempt {attempt + 1}/{max_attempts} failed. "
                        f"Retrying in {delay:.1f}s. Error: {e}"
                    )

                    time.sleep(delay)

                except Exception as e:
                    # Non-retryable exception - log and re-raise immediately
                    logger.error(f"{func.__name__}: Non-retryable error: {e}", exc_info=True)
                    raise

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


# Convenience decorator for rate limit errors
def with_rate_limit_retry(
    max_attempts: int = 5,
    base_delay: float = 2.0,
    max_delay: float = 300.0  # 5 minutes
):
    """
    Specialized retry decorator for API rate limiting.
    Longer delays suitable for 429 Too Many Requests responses.

    Usage:
        @with_rate_limit_retry
        def call_rate_limited_api():
            ...
    """
    return with_retry(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        log_level=logging.INFO
    )


# Decorator for authentication errors (no retry, just alert)
def no_retry_on_auth_error(func: Callable) -> Callable:
    """
    Decorator that logs authentication errors without retrying.
    Use for 401/403 responses where retry won't help.

    Usage:
        @no_retry_on_auth_error
        def call_auth_required_api():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)

        except Exception as e:
            error_str = str(e).lower()

            # Check for auth-related errors
            if any(indicator in error_str for indicator in ['401', '403', 'unauthorized', 'forbidden', 'authentication']):
                logger.error(
                    f"{func.__name__}: Authentication error (no retry): {e}",
                    exc_info=True
                )
                # Re-raise for caller to handle (should create ALERT file)
                raise
            else:
                # Non-auth error - re-raise normally
                raise

    return wrapper
