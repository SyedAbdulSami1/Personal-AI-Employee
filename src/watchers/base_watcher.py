"""
BaseWatcher — Abstract base class for all watchers.
All watchers must extend this class and implement:
  - check_for_updates()
  - create_action_file()
"""
from abc import ABC, abstractmethod
import logging
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class BaseWatcher(ABC):
    """Abstract base class for all watcher implementations."""

    def __init__(self, config: Any, vault_path: Path):
        """
        Initialize base watcher.

        Args:
            config: Config dataclass with dry_run, interval, etc.
            vault_path: Path to AI_Employee_Vault directory
        """
        self.config = config
        self.vault_path = vault_path
        self.needs_action_path = vault_path / "Needs_Action"
        self.logs_path = vault_path / "Logs"
        self.dry_run = getattr(config, 'dry_run', True)
        self.interval = getattr(config, 'interval', 60)
        self._processed_ids: set = set()

        # Ensure directories exist
        self.needs_action_path.mkdir(parents=True, exist_ok=True)
        self.logs_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new updates/items from the data source.

        Returns:
            List of dictionaries containing item data to process.
            Each dict should have at minimum:
            - id: Unique identifier for deduplication
            - type: 'email' | 'whatsapp' | 'file' | etc.
            - from: Sender/originator
            - subject: Subject/preview text
            - received: ISO 8601 timestamp
            - priority: 'high' | 'medium' | 'low'
            - content: Full content/body
        """
        pass

    @abstractmethod
    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create a Needs_Action markdown file for the given item.

        Args:
            item: Dictionary from check_for_updates()

        Returns:
            Path to created file, or None if DRY_RUN or error.
        """
        pass

    def _is_duplicate(self, item_id: str) -> bool:
        """Check if item has already been processed this session."""
        return item_id in self._processed_ids

    def _mark_processed(self, item_id: str) -> None:
        """Mark an item as processed."""
        self._processed_ids.add(item_id)

    def run(self) -> None:
        """
        Main watcher loop with exponential backoff on errors.
        Runs indefinitely until interrupted.
        """
        logger.info(f"[{self.__class__.__name__}] Starting watcher loop (interval={self.interval}s, dry_run={self.dry_run})")

        consecutive_errors = 0
        max_errors = 5
        base_delay = 5

        while True:
            try:
                # Check for new items
                items = self.check_for_updates()

                if items:
                    logger.info(f"[{self.__class__.__name__}] Found {len(items)} new items")

                    for item in items:
                        if not self._is_duplicate(item.get('id', '')):
                            action_file = self.create_action_file(item)
                            if action_file:
                                self._mark_processed(item['id'])
                                logger.info(f"[{self.__class__.__name__}] Created: {action_file.name}")
                else:
                    logger.debug(f"[{self.__class__.__name__}] No new items")

                consecutive_errors = 0  # Reset on success

            except Exception as e:
                consecutive_errors += 1
                logger.error(
                    f"[{self.__class__.__name__}] Error in watcher loop (attempt {consecutive_errors}/{max_errors}): {e}",
                    exc_info=True
                )

                if consecutive_errors >= max_errors:
                    logger.critical(f"[{self.__class__.__name__}] Max consecutive errors reached. Stopping.")
                    raise

                # Exponential backoff
                delay = base_delay * (2 ** (consecutive_errors - 1))
                logger.warning(f"[{self.__class__.__name__}] Waiting {delay}s before retry...")
                time.sleep(delay)

            # Wait for next interval
            time.sleep(self.interval)

    def stop(self) -> None:
        """Cleanup method called before watcher stops."""
        logger.info(f"[{self.__class__.__name__}] Stopping watcher...")
        # Override in subclass if cleanup needed (e.g., close connections)
