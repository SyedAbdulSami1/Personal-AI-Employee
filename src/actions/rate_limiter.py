"""
RateLimiter — Token bucket rate limiter for API calls and actions.
Enforces Company Handbook rate limits across all watchers and actions.
"""
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
from threading import Lock

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter with configurable limits per action type.
    Thread-safe implementation for multi-watcher environments.
    """

    def __init__(self, vault_path: Optional[Path] = None):
        """
        Initialize rate limiter.

        Args:
            vault_path: Path to vault for persistent state (optional)
        """
        self.vault_path = vault_path
        self._lock = Lock()
        self._buckets: Dict[str, Dict[str, Any]] = {}

        # Default limits from Company Handbook
        self._default_limits = {
            'email_send': {'max_tokens': 10, 'refill_rate': 10, 'window_seconds': 3600},  # 10/hour
            'payment': {'max_tokens': 3, 'refill_rate': 3, 'window_seconds': 3600},  # 3/hour
            'social_post': {'max_tokens': 5, 'refill_rate': 5, 'window_seconds': 86400},  # 5/day
            'whatsapp_send': {'max_tokens': 30, 'refill_rate': 30, 'window_seconds': 3600},  # 30/hour
            'claude_api_call': {'max_tokens': 100, 'refill_rate': 100, 'window_seconds': 3600},  # 100/hour
        }

        # Initialize buckets
        for action_type, config in self._default_limits.items():
            self._buckets[action_type] = {
                'tokens': config['max_tokens'],
                'last_refill': datetime.now(),
                'max_tokens': config['max_tokens'],
                'refill_rate': config['refill_rate'],
                'window_seconds': config['window_seconds'],
                'total_used': 0,
                'last_used': None
            }

        logger.info(f"[RateLimiter] Initialized with {len(self._buckets)} rate limit buckets")

    def _refill_bucket(self, bucket: Dict[str, Any]) -> None:
        """Refill tokens based on elapsed time."""
        now = datetime.now()
        elapsed = (now - bucket['last_refill']).total_seconds()

        # Calculate tokens to add
        tokens_to_add = (elapsed / bucket['window_seconds']) * bucket['refill_rate']

        if tokens_to_add > 0:
            bucket['tokens'] = min(bucket['max_tokens'], bucket['tokens'] + tokens_to_add)
            bucket['last_refill'] = now

    def check_and_increment(self, action_type: str, cost: int = 1) -> bool:
        """
        Check if action is allowed and consume tokens if so.

        Args:
            action_type: Type of action (email_send, payment, etc.)
            cost: Number of tokens to consume (default 1)

        Returns:
            True if allowed (tokens consumed), False if rate limited
        """
        with self._lock:
            if action_type not in self._buckets:
                logger.warning(f"Unknown action type: {action_type}, allowing by default")
                return True

            bucket = self._buckets[action_type]
            self._refill_bucket(bucket)

            if bucket['tokens'] >= cost:
                bucket['tokens'] -= cost
                bucket['total_used'] += cost
                bucket['last_used'] = datetime.now()

                logger.debug(f"Rate limit OK for {action_type}: {bucket['tokens']:.1f} tokens remaining")
                return True
            else:
                # Calculate wait time
                tokens_needed = cost - bucket['tokens']
                wait_seconds = (tokens_needed / bucket['refill_rate']) * bucket['window_seconds']

                logger.warning(
                    f"Rate limit exceeded for {action_type}. "
                    f"Wait {wait_seconds:.0f}s before retry. "
                    f"Tokens: {bucket['tokens']:.1f}/{bucket['max_tokens']}"
                )
                return False

    def get_status(self, action_type: str) -> Dict[str, Any]:
        """
        Get current rate limit status for an action type.

        Args:
            action_type: Type of action

        Returns:
            Dictionary with tokens_remaining, max_tokens, reset_time, etc.
        """
        with self._lock:
            if action_type not in self._buckets:
                return {'error': 'Unknown action type'}

            bucket = self._buckets[action_type]
            self._refill_bucket(bucket)

            # Calculate reset time (when bucket will be full)
            tokens_needed = bucket['max_tokens'] - bucket['tokens']
            reset_seconds = (tokens_needed / bucket['refill_rate']) * bucket['window_seconds']
            reset_time = datetime.now() + timedelta(seconds=reset_seconds)

            return {
                'action_type': action_type,
                'tokens_remaining': int(bucket['tokens']),
                'max_tokens': bucket['max_tokens'],
                'total_used': bucket['total_used'],
                'last_used': bucket['last_used'].isoformat() if bucket['last_used'] else None,
                'reset_time': reset_time.isoformat(),
                'reset_seconds': int(reset_seconds)
            }

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all rate limit buckets."""
        return {
            action_type: self.get_status(action_type)
            for action_type in self._buckets
        }

    def reset_bucket(self, action_type: str) -> None:
        """
        Reset a rate limit bucket to full (for testing or manual override).

        Args:
            action_type: Type of action to reset
        """
        with self._lock:
            if action_type in self._buckets:
                bucket = self._buckets[action_type]
                bucket['tokens'] = bucket['max_tokens']
                bucket['last_refill'] = datetime.now()
                bucket['total_used'] = 0
                logger.info(f"Rate limit bucket reset: {action_type}")

    def wait_for_token(
        self,
        action_type: str,
        cost: int = 1,
        max_wait: float = 300.0,
        poll_interval: float = 1.0
    ) -> bool:
        """
        Wait until a token is available (blocking).

        Args:
            action_type: Type of action
            cost: Number of tokens needed
            max_wait: Maximum time to wait in seconds (default 300s = 5 min)
            poll_interval: How often to check (default 1s)

        Returns:
            True if token acquired, False if max_wait exceeded
        """
        start_time = time.time()

        while True:
            if self.check_and_increment(action_type, cost):
                return True

            elapsed = time.time() - start_time
            if elapsed >= max_wait:
                logger.error(f"Rate limit wait exceeded for {action_type} (max_wait={max_wait}s)")
                return False

            time.sleep(poll_interval)
