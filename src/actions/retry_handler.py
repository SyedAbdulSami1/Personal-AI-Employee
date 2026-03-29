"""
Retry handler with exponential backoff for external service calls.
"""
import functools
import logging
import random
import time
from typing import Callable, Type, Tuple, Union

logger = logging.getLogger(__name__)


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception
):
    """
    Decorator that adds retry logic with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including initial try)
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delay
        exceptions: Exception type(s) to catch and retry on
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    # If this was the last attempt, don't retry
                    if attempt == max_attempts - 1:
                        logger.warning(
                            f"Function {func.__name__} failed after {max_attempts} attempts. "
                            f"Last error: {e}"
                        )
                        break

                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )

                    # Add jitter if enabled
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)  # 0.5 to 1.0 multiplier

                    logger.info(
                        f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )

                    time.sleep(delay)

            # If we got here, all retries exhausted
            raise last_exception

        return wrapper
    return decorator


# Convenience decorators for common use cases
def with_retry_network(max_attempts: int = 3):
    """Retry decorator for network-related failures."""
    import requests
    return with_retry(
        max_attempts=max_attempts,
        base_delay=1.0,
        max_delay=30.0,
        exceptions=(
            ConnectionError,
            TimeoutError,
            # Add requests exceptions if available
        )
    )


def with_retry_api(max_attempts: int = 3):
    """Retry decorator for API-related failures."""
    return with_retry(
        max_attempts=max_attempts,
        base_delay=2.0,
        max_delay=60.0,
        exceptions=Exception  # Retry on any exception for APIs
    )