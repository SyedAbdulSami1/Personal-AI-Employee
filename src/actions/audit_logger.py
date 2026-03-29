"""
Audit logging system for the Personal AI Employee.
Logs all actions to daily JSON files with 90-day retention.
"""
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AuditLogger:
    """Singleton audit logger for tracking all system actions."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config=None):
        # Prevent re-initialization
        if hasattr(self, '_initialized'):
            return

        self.config = config or self._load_config_from_env()
        self._ensure_log_directory()
        self._cleanup_old_logs()
        self._initialized = True

    def _load_config_from_env(self):
        """Load config from environment if not provided."""
        from src.config import config as global_config
        return global_config

    def _ensure_log_directory(self):
        """Ensure the logs directory exists."""
        self.config.logs_path.mkdir(parents=True, exist_ok=True)

    def _get_log_file_path(self, date: Optional[datetime] = None) -> Path:
        """Get the log file path for a given date (defaults to today)."""
        if date is None:
            date = datetime.now()
        date_str = date.strftime("%Y-%m-%d")
        return self.config.logs_path / f"{date_str}.json"

    def _cleanup_old_logs(self):
        """Delete log files older than 90 days."""
        cutoff_date = datetime.now() - timedelta(days=90)
        log_files = self.config.logs_path.glob("*.json")

        for log_file in log_files:
            try:
                # Extract date from filename (YYYY-MM-DD.json)
                date_str = log_file.stem
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                if file_date < cutoff_date:
                    log_file.unlink()
                    logger.info(f"Deleted old audit log: {log_file.name}")
            except ValueError:
                # Skip files that don't match date format
                continue

    def log_action(
        self,
        action_type: str,
        actor: str,
        target: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        approval_status: str = "unknown",
        result: str = "unknown",
        error: Optional[str] = None,
        dry_run: bool = None
    ) -> None:
        """
        Log an action to the daily audit log.

        Args:
            action_type: Type of action performed (e.g., 'email_send', 'file_move')
            actor: Who performed the action (e.g., 'claude_code', 'gmail_watcher')
            target: Target of the action (e.g., recipient email, file path)
            parameters: Additional parameters for the action
            approval_status: 'human_approved', 'human_rejected', 'auto_approved', etc.
            result: 'success', 'failure', 'pending', etc.
            error: Error message if action failed
            dry_run: Whether this was a dry run (uses config if None)
        """
        if parameters is None:
            parameters = {}

        if dry_run is None:
            dry_run = self.config.dry_run

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "target": target,
            "parameters": parameters,
            "approval_status": approval_status,
            "result": result,
            "error": error,
            "dry_run": dry_run
        }

        log_file = self._get_log_file_path()

        try:
            # Read existing logs or start fresh
            if log_file.exists():
                with open(log_file, 'r') as f:
                    try:
                        logs = json.load(f)
                        if not isinstance(logs, list):
                            logs = []
                    except json.JSONDecodeError:
                        logs = []
            else:
                logs = []

            # Append new log entry
            logs.append(log_entry)

            # Write back to file
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2, default=str)

            logger.debug(f"Logged action: {action_type} by {actor}")

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
            # Fallback to stderr logging
            print(f"AUDIT LOG ERROR: {log_entry}")

    def get_recent_actions(self, limit: int = 50) -> list:
        """Get recent actions from today's log."""
        log_file = self._get_log_file_path()

        if not log_file.exists():
            return []

        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
                return logs[-limit:] if isinstance(logs, list) else []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def get_actions_by_type(self, action_type: str, limit: int = 100) -> list:
        """Get actions of a specific type from today's log."""
        all_actions = self.get_recent_actions(limit=1000)  # Get more to filter
        return [action for action in all_actions if action.get("action_type") == action_type][:limit]


# Global audit logger instance
audit_logger = AuditLogger()