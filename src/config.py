"""
Configuration management for the Personal AI Employee system.
Single instance pattern - create once and pass everywhere.
"""
from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Application configuration loaded from environment variables."""

    # Vault paths
    vault_path: Path
    inbox_path: Path
    needs_action_path: Path
    in_progress_path: Path
    plans_path: Path
    pending_approval_path: Path
    approved_path: Path
    rejected_path: Path
    done_path: Path
    logs_path: Path
    briefings_path: Path
    accounting_path: Path

    # System settings
    dry_run: bool = True
    dev_mode: bool = True
    log_level: str = "DEBUG"

    # Rate limiting
    max_emails_per_hour: int = 10
    max_payments_per_hour: int = 3
    max_messages_per_hour: int = 20

    # Watcher intervals (seconds)
    gmail_interval: int = 120
    whatsapp_interval: int = 30
    filesystem_interval: int = 10

    # Ralph Wiggum settings
    ralph_max_iterations: int = 10

    # API settings (loaded from .env)
    gmail_client_id: Optional[str] = None
    gmail_client_secret: Optional[str] = None
    gmail_credentials_path: Optional[Path] = None
    whatsapp_session_path: Optional[Path] = None

    def __post_init__(self):
        """Ensure all paths are Path objects and create directories if needed."""
        # Convert string paths to Path objects
        for field in self.__dataclass_fields__:
            value = getattr(self, field)
            if isinstance(value, str) and ('path' in field.lower() or field.endswith('_path')):
                setattr(self, field, Path(value))

        # Create directories if they don't exist
        paths_to_create = [
            self.vault_path, self.inbox_path, self.needs_action_path,
            self.in_progress_path, self.plans_path, self.pending_approval_path,
            self.approved_path, self.rejected_path, self.done_path,
            self.logs_path, self.briefings_path, self.accounting_path
        ]

        for path in paths_to_create:
            path.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    """Load configuration from environment variables and return Config instance."""
    vault_base = Path(os.getenv("VAULT_PATH", "./AI_Employee_Vault"))

    return Config(
        vault_path=vault_base,
        inbox_path=vault_base / "Inbox",
        needs_action_path=vault_base / "Needs_Action",
        in_progress_path=vault_base / "In_Progress" / "claude",
        plans_path=vault_base / "Plans",
        pending_approval_path=vault_base / "Pending_Approval",
        approved_path=vault_base / "Approved",
        rejected_path=vault_base / "Rejected",
        done_path=vault_base / "Done",
        logs_path=vault_base / "Logs",
        briefings_path=vault_base / "Briefings",
        accounting_path=vault_base / "Accounting",

        # System settings
        dry_run=os.getenv("DRY_RUN", "true").lower() == "true",
        dev_mode=os.getenv("DEV_MODE", "true").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "DEBUG"),

        # Rate limiting
        max_emails_per_hour=int(os.getenv("MAX_EMAILS_PER_HOUR", "10")),
        max_payments_per_hour=int(os.getenv("MAX_PAYMENTS_PER_HOUR", "3")),
        max_messages_per_hour=int(os.getenv("MAX_MESSAGES_PER_HOUR", "20")),

        # Watcher intervals
        gmail_interval=int(os.getenv("GMAIL_INTERVAL", "120")),
        whatsapp_interval=int(os.getenv("WHATSAPP_INTERVAL", "30")),
        filesystem_interval=int(os.getenv("FILESYSTEM_INTERVAL", "10")),

        # Ralph Wiggum
        ralph_max_iterations=int(os.getenv("RALPH_MAX_ITERATIONS", "10")),

        # API credentials
        gmail_client_id=os.getenv("GMAIL_CLIENT_ID"),
        gmail_client_secret=os.getenv("GMAIL_CLIENT_SECRET"),
        gmail_credentials_path=Path(os.getenv("GMAIL_CREDENTIALS", "")) if os.getenv("GMAIL_CREDENTIALS") else None,
        whatsapp_session_path=Path(os.getenv("WHATSAPP_SESSION_PATH", "")) if os.getenv("WHATSAPP_SESSION_PATH") else None,
    )


# Global config instance - create once and import everywhere
config = load_config()