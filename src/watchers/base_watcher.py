"""
Base watcher class for all file system watchers in the Personal AI Employee system.
All watchers should extend this class and implement the required methods.
"""
import abc
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.actions.audit_logger import audit_logger
from src.config import config

logger = logging.getLogger(__name__)


class BaseWatcher(abc.ABC):
    """
    Abstract base class for all watchers.
    Provides common functionality like logging, dry-run support, and audit trails.
    """

    def __init__(self, name: str, config_instance=None):
        """
        Initialize the watcher.

        Args:
            name: Unique name for this watcher (used in logging)
            config_instance: Config instance (uses global if not provided)
        """
        self.name = name
        self.config = config_instance or config
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self._last_run = None
        self._run_count = 0

    @abc.abstractmethod
    def check_for_updates(self) -> bool:
        """
        Check for new updates or items to process.
        Should return True if updates were found and processed, False otherwise.

        Returns:
            bool: True if updates were processed, False if none found
        """
        pass

    @abc.abstractmethod
    def create_action_file(self, update_data: dict) -> Optional[Path]:
        """
        Create an action file in the Needs_Action directory based on update data.

        Args:
            update_data: Dictionary containing information about the update

        Returns:
            Path: Path to the created action file, or None if creation failed
        """
        pass

    def run(self) -> None:
        """
        Main watcher loop. Called by the watcher's main entry point.
        Handles timing, error handling, and basic lifecycle.
        """
        self.logger.info(f"Starting {self.name} watcher")
        self._last_run = datetime.now()

        try:
            while True:
                self._run_count += 1
                start_time = time.time()

                try:
                    # Check for updates
                    updates_found = self.check_for_updates()

                    if updates_found:
                        self.logger.info(f"{self.name} processed updates")
                        audit_logger.log_action(
                            action_type=f"{self.name}_check",
                            actor=self.name,
                            target="system",
                            parameters={"updates_found": True, "run_count": self._run_count},
                            approval_status="auto_approved",
                            result="success",
                            dry_run=self.config.dry_run
                        )
                    else:
                        self.logger.debug(f"{self.name} check complete - no updates")
                        audit_logger.log_action(
                            action_type=f"{self.name}_check",
                            actor=self.name,
                            target="system",
                            parameters={"updates_found": False, "run_count": self._run_count},
                            approval_status="auto_approved",
                            result="success",
                            dry_run=self.config.dry_run
                        )

                except Exception as e:
                    self.logger.error(f"Error in {self.name} watcher: {e}", exc_info=True)
                    audit_logger.log_action(
                        action_type=f"{self.name}_error",
                        actor=self.name,
                        target="system",
                        parameters={"error": str(e), "run_count": self._run_count},
                        approval_status="system_error",
                        result="failure",
                        error=str(e),
                        dry_run=self.config.dry_run
                    )

                # Calculate sleep time
                elapsed = time.time() - start_time
                sleep_time = max(0, self.get_interval() - elapsed)

                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            self.logger.info(f"{self.name} watcher stopped by user")
        except Exception as e:
            self.logger.critical(f"Fatal error in {self.name} watcher: {e}", exc_info=True)
            raise

    def get_interval(self) -> int:
        """Get the check interval for this watcher (to be overridden by subclasses)."""
        return 60  # Default 1 minute

    def get_stats(self) -> dict:
        """Get watcher statistics."""
        return {
            "name": self.name,
            "last_run": self._last_run.isoformat() if self._last_run else None,
            "run_count": self._run_count,
            "interval_seconds": self.get_interval()
        }

    def _create_yaml_frontmatter(self, data: dict) -> str:
        """
        Create YAML frontmatter for action files.

        Args:
            data: Dictionary of data to include in frontmatter

        Returns:
            str: YAML frontmatter string
        """
        lines = ["---"]
        for key, value in data.items():
            if isinstance(value, str):
                lines.append(f"{key}: {value}")
            else:
                lines.append(f"{key}: {value}")
        lines.append("---")
        lines.append("")  # Empty line after frontmatter
        return "\n".join(lines)

    def _create_action_file(self, filename: str, frontmatter_data: dict, content: str = "") -> Path:
        """
        Create an action file with YAML frontmatter.

        Args:
            filename: Name of the file to create
            frontmatter_data: Data for the YAML frontmatter
            content: Content to place after the frontmatter

        Returns:
            Path: Path to the created file
        """
        if self.config.dry_run:
            self.logger.info(f"[DRY RUN] Would create action file: {filename}")
            return self.config.needs_action_path / filename

        file_path = self.config.needs_action_path / filename
        frontmatter = self._create_yaml_frontmatter(frontmatter_data)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter)
                f.write(content)
            self.logger.debug(f"Created action file: {file_path}")
            return file_path
        except Exception as e:
            self.logger.error(f"Failed to create action file {filename}: {e}")
            raise