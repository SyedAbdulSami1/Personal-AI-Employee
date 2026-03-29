"""
Rate limiter for controlling frequency of actions.
Uses sliding window algorithm for accurate rate limiting.
"""
import time
from collections import defaultdict, deque
from threading import Lock
from typing import Dict, Deque
import logging

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Thread-safe rate limiter using sliding window algorithm.
    One instance per rate limit type (email, payment, message, etc.)
    """

    def __init__(self, max_calls: int, time_window: int = 3600):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed in time_window
            time_window: Time window in seconds (default 1 hour = 3600s)
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls: Deque[float] = deque()
        self.lock = Lock()

    def _clean_old_calls(self, now: float) -> None:
        """Remove calls older than the time window."""
        while self.calls and self.calls[0] <= now - self.time_window:
            self.calls.popleft()

    def check_and_increment(self) -> bool:
        """
        Check if an action is allowed under the rate limit.
        If allowed, increment the counter and return True.
        If not allowed, return False without incrementing.

        Returns:
            True if action is allowed, False if rate limited
        """
        with self.lock:
            now = time.time()
            self._clean_old_calls(now)

            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                logger.debug(f"Rate limit check passed: {len(self.calls)}/{self.max_calls}")
                return True
            else:
                logger.warning(f"Rate limit exceeded: {len(self.calls)}/{self.max_calls}")
                return False

    def get_current_count(self) -> int:
        """Get current number of calls in the time window."""
        with self.lock:
            now = time.time()
            self._clean_old_calls(now)
            return len(self.calls)

    def get_reset_time(self) -> float:
        """Get seconds until the rate limit resets (returns 0 if not limited)."""
        with self.lock:
            if not self.calls:
                return 0.0

            now = time.time()
            oldest_call = self.calls[0]
            reset_time = oldest_call + self.time_window - now
            return max(0.0, reset_time)


# Global rate limiter instances
email_rate_limiter = None
payment_rate_limiter = None
message_rate_limiter = None


def initialize_rate_limiters(config):
    """Initialize global rate limiter instances with config values."""
    global email_rate_limiter, payment_rate_limiter, message_rate_limiter

    email_rate_limiter = RateLimiter(
        max_calls=config.max_emails_per_hour,
        time_window=3600  # 1 hour
    )

    payment_rate_limiter = RateLimiter(
        max_calls=config.max_payments_per_hour,
        time_window=3600  # 1 hour
    )

    message_rate_limiter = RateLimiter(
        max_calls=config.max_messages_per_hour,
        time_window=3600  # 1 hour
    )

    logger.info("Rate limiters initialized")