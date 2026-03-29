"""
AuditLogger — Structured JSON logging for all AI Employee actions.
Writes to /Vault/Logs/YYYY-MM-DD.json with 90-day retention.
"""
import logging
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AuditLogger:
    """Singleton audit logger for structured action logging."""

    _instance: Optional['AuditLogger'] = None

    def __new__(cls, logs_path: Path) -> 'AuditLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, logs_path: Path):
        if self._initialized:
            return

        self.logs_path = logs_path
        self.logs_path.mkdir(parents=True, exist_ok=True)
        self._initialized = True

        # Enforce 90-day retention
        self._cleanup_old_logs()

        logger.info(f"[AuditLogger] Initialized with logs path: {logs_path}")

    def _get_today_file(self) -> Path:
        """Get today's log file path."""
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        return self.logs_path / f"{today}.json"

    def _cleanup_old_logs(self) -> None:
        """Delete log files older than 90 days."""
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=90)

            for log_file in self.logs_path.glob("*.json"):
                try:
                    # Parse date from filename (YYYY-MM-DD.json)
                    date_str = log_file.stem
                    file_date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)

                    if file_date < cutoff:
                        log_file.unlink()
                        logger.debug(f"Deleted old log: {log_file.name}")

                except Exception as e:
                    logger.warning(f"Could not process log file {log_file.name}: {e}")

        except Exception as e:
            logger.error(f"Error cleaning up old logs: {e}")

    def log_action(
        self,
        action_type: str,
        actor: str,
        target: str,
        parameters: Optional[Dict[str, Any]] = None,
        approval_status: str = "none",
        approved_by: str = "none",
        result: str = "success",
        error: Optional[str] = None,
        dry_run: bool = False
    ) -> None:
        """
        Log an action to today's JSON audit log.

        Args:
            action_type: Type of action (email_send, payment, file_move, watcher_start, error, etc.)
            actor: Who performed the action (qwen_agent, gmail_watcher, whatsapp_watcher, human)
            target: What the action targeted (recipient, file path, platform)
            parameters: Additional action parameters (dict)
            approval_status: none, human_approved, system_approved
            approved_by: human, system, none
            result: success, failure, dry_run, skipped
            error: Error message if result=failure
            dry_run: Whether this was a dry run
        """
        try:
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "action_type": action_type,
                "actor": actor,
                "target": target,
                "parameters": parameters or {},
                "approval_status": approval_status,
                "approved_by": approved_by,
                "result": result,
                "error": error,
                "dry_run": dry_run
            }

            log_file = self._get_today_file()

            # Append as JSON line (JSONL format)
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')

            logger.debug(f"Audit log entry written to {log_file.name}")

        except Exception as e:
            logger.error(f"Failed to write audit log: {e}", exc_info=True)

    def get_today_logs(self) -> list:
        """Read all log entries from today."""
        log_file = self._get_today_file()

        if not log_file.exists():
            return []

        entries = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))

        except Exception as e:
            logger.error(f"Failed to read audit logs: {e}")

        return entries

    def get_actions_by_type(self, action_type: str, date: Optional[str] = None) -> list:
        """
        Get all actions of a specific type.

        Args:
            action_type: Type to filter by
            date: YYYY-MM-DD format (defaults to today)

        Returns:
            List of matching log entries
        """
        if date is None:
            return [e for e in self.get_today_logs() if e.get('action_type') == action_type]

        log_file = self.logs_path / f"{date}.json"

        if not log_file.exists():
            return []

        entries = []
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entry = json.loads(line)
                        if entry.get('action_type') == action_type:
                            entries.append(entry)

        except Exception as e:
            logger.error(f"Failed to read audit logs: {e}")

        return entries
