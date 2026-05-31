"""
Base action class for all actions in the Personal AI Employee system.
All actions should extend this class and implement the execute method.
"""
import abc
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.actions.audit_logger import audit_logger
from src.actions.rate_limiter import rate_limiter
def get_rate_limiter(self, action_type: str):
    return rate_limiter

def check_rate_limit(self, action_type: str) -> bool:
    action_map = {
        'email': 'email_send',
        'payment': 'payment',
        'message': 'whatsapp_send',
    }
    mapped = action_map.get(action_type, action_type)
    return rate_limiter.check_and_increment(mapped)

from src.config import config

logger = logging.getLogger(__name__)


class BaseAction(abc.ABC):
    """
    Abstract base class for all actions.
    Provides DRY_RUN guard, audit logging, and rate limiting.
    """

    def __init__(self, name: str, config_instance=None):
        """
        Initialize the action.

        Args:
            name: Unique name for this action (used in logging)
            config_instance: Config instance (uses global if not provided)
        """
        self.name = name
        self.config = config_instance or config
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.audit_logger = audit_logger

    @abc.abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the action. Must be implemented by subclasses.

        Args:
            **kwargs: Action-specific parameters

        Returns:
            Dict containing result information
        """
        pass

    def get_rate_limiter(self, action_type: str):
        """
        Get the appropriate rate limiter for the action type.

        Args:
            action_type: Type of action ('email', 'payment', 'message')

        Returns:
            RateLimiter instance or None if not found
        """
        limiters = {
            'email': email_rate_limiter,
            'payment': payment_rate_limiter,
            'message': message_rate_limiter,
        }
        return limiters.get(action_type)

    def check_rate_limit(self, action_type: str) -> bool:
        """
        Check if the action is within rate limits.

        Args:
            action_type: Type of action ('email', 'payment', 'message')

        Returns:
            True if within limits, False if rate limited
        """
        limiter = self.get_rate_limiter(action_type)
        if limiter is None:
            return True  # No limiter for this type

        return limiter.check_and_increment()

    def dry_run_check(self, action_desc: str) -> bool:
        """
        Check if running in dry-run mode and log appropriately.

        Args:
            action_desc: Description of the action that would be performed

        Returns:
            True if should proceed with real execution, False if dry-run
        """
        if self.config.dry_run:
            self.logger.info(f"[DRY RUN] {self.name} would: {action_desc}")
            self.audit_logger.log_action(
                action_type=f"{self.name}_dry_run",
                actor=self.name,
                target=action_desc,
                parameters={"dry_run": True},
                approval_status="dry_run",
                result="dry_run",
                dry_run=True
            )
            return False
        return True

    def log_action_start(self, action_type: str, target: str, parameters: Dict = None) -> None:
        """Log the start of an action."""
        self.logger.info(f"Starting {action_type} action: {target}")
        self.audit_logger.log_action(
            action_type=action_type,
            actor=self.name,
            target=target,
            parameters=parameters or {},
            approval_status="pending",
            result="in_progress",
            dry_run=self.config.dry_run
        )

    def log_action_success(self, action_type: str, target: str, result_data: Dict = None) -> None:
        """Log successful completion of an action."""
        self.logger.info(f"Completed {action_type} action: {target}")
        self.audit_logger.log_action(
            action_type=action_type,
            actor=self.name,
            target=target,
            parameters=result_data or {},
            approval_status="auto_approved",
            result="success",
            dry_run=self.config.dry_run
        )

    def log_action_failure(self, action_type: str, target: str, error: str) -> None:
        """Log failure of an action."""
        self.logger.error(f"Failed {action_type} action: {target} - {error}")
        self.audit_logger.log_action(
            action_type=action_type,
            actor=self.name,
            target=target,
            parameters={"error": error},
            approval_status="system_error",
            result="failure",
            error=error,
            dry_run=self.config.dry_run
        )

    def execute_with_logging(self, action_type: str, target: str, **kwargs) -> Dict[str, Any]:
        """
        Execute an action with standard logging and error handling.

        Args:
            action_type: Type of action for logging
            target: Target of the action
            **kwargs: Parameters to pass to execute()

        Returns:
            Dict containing result information
        """
        self.log_action_start(action_type, target, kwargs)

        try:
            result = self.execute(**kwargs)
            self.log_action_success(action_type, target, result)
            return result
        except Exception as e:
            self.log_action_failure(action_type, target, str(e))
            raise
