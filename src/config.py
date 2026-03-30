"""
Config — Single configuration dataclass for the entire AI Employee system.
Reads .env once at startup and passes values everywhere.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


@dataclass
class Config:
    """
    Central configuration for all AI Employee components.
    Instantiate once at entry point, pass as parameter everywhere.
    """

    # Base paths
    vault_path: Path = field(default_factory=lambda: Path("./AI_Employee_Vault"))
    project_root: Path = field(default_factory=lambda: Path("."))

    # Feature flags
    dry_run: bool = True
    dev_mode: bool = True

    # Gmail settings
    gmail_credentials_path: Optional[str] = None
    gmail_interval: int = 120  # seconds

    # WhatsApp settings
    whatsapp_session_path: Optional[str] = None
    whatsapp_interval: int = 30  # seconds

    # Rate limits (overrides defaults in RateLimiter)
    max_emails_per_hour: int = 10
    max_payments_per_hour: int = 3
    max_social_posts_per_day: int = 5
    max_whatsapp_per_hour: int = 30

    # Ralph Wiggum settings
    ralph_max_iterations: int = 10

    # Logging
    log_level: str = "DEBUG"

    # API keys (loaded from env)
    qwen_api_key: Optional[str] = None
    qwen_base_url: Optional[str] = None

    def __post_init__(self):
        """Load environment variables and populate config."""
        # Load .env file
        env_file = self.project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
        else:
            # Try default location
            load_dotenv()

        # Populate from environment
        self.dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
        self.dev_mode = os.getenv("DEV_MODE", "true").lower() == "true"

        # Paths
        vault_env = os.getenv("VAULT_PATH")
        if vault_env:
            self.vault_path = Path(vault_env)

        # Gmail
        self.gmail_credentials_path = os.getenv("GMAIL_CREDENTIALS")

        # WhatsApp
        self.whatsapp_session_path = os.getenv("WHATSAPP_SESSION_PATH")

        # API keys
        self.qwen_api_key = os.getenv("QWEN_API_KEY")
        self.qwen_base_url = os.getenv("QWEN_BASE_URL")

        # Intervals
        gmail_interval = os.getenv("GMAIL_INTERVAL")
        if gmail_interval:
            self.gmail_interval = int(gmail_interval)

        whatsapp_interval = os.getenv("WHATSAPP_INTERVAL")
        if whatsapp_interval:
            self.whatsapp_interval = int(whatsapp_interval)

        # Log level
        log_level = os.getenv("LOG_LEVEL")
        if log_level:
            self.log_level = log_level.upper()

    def validate(self) -> bool:
        """
        Validate critical configuration.

        Returns:
            True if all required config is present, False otherwise.
        """
        errors = []

        # Check vault path exists or can be created
        try:
            self.vault_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create vault path: {e}")

        # Warn if running in dry_run
        if self.dry_run:
            print("[CONFIG] Running in DRY_RUN mode - no external actions will be taken")

        # Warn if dev_mode
        if self.dev_mode:
            print("[CONFIG] Running in DEV_MODE - use test credentials only")

        if errors:
            for error in errors:
                print(f"[CONFIG ERROR] {error}")
            return False

        return True

    @property
    def inbox_path(self) -> Path:
        """Get Inbox folder path (for filesystem watcher drop folder)."""
        return self.vault_path / "Inbox"

    @property
    def needs_action_path(self) -> Path:
        """Get Needs_Action folder path."""
        return self.vault_path / "Needs_Action"

    @property
    def approved_path(self) -> Path:
        """Get Approved folder path."""
        return self.vault_path / "Approved"

    @property
    def pending_approval_path(self) -> Path:
        """Get Pending_Approval folder path."""
        return self.vault_path / "Pending_Approval"

    @property
    def done_path(self) -> Path:
        """Get Done folder path."""
        return self.vault_path / "Done"

    @property
    def logs_path(self) -> Path:
        """Get Logs folder path."""
        return self.vault_path / "Logs"

    @property
    def plans_path(self) -> Path:
        """Get Plans folder path."""
        return self.vault_path / "Plans"


# Global config instance - created once, imported everywhere
config = Config()
