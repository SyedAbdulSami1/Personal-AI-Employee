"""
FilesystemWatcher — Monitors Inbox/ folder for new file drops.
Creates action files with sidecar metadata in /Needs_Action/.
"""
import logging
import shutil
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from .base_watcher import BaseWatcher

logger = logging.getLogger(__name__)


SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.csv', '.txt', '.md'}


class DropFolderHandler(FileSystemEventHandler):
    """Handles file creation events in the Inbox folder."""

    def __init__(self, watcher: 'FilesystemWatcher'):
        self.watcher = watcher
        self.vault_path = watcher.vault_path
        self.needs_action_path = watcher.needs_action_path

    def on_created(self, event):
        """Handle new file creation events."""
        if event.is_directory:
            return

        src_path = Path(event.src_path)

        # Check if file is in Inbox
        inbox_path = self.vault_path / "Inbox"
        if not str(src_path).startswith(str(inbox_path)):
            return

        # Check supported extensions
        if src_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            logger.debug(f"Ignoring unsupported file: {src_path.name}")
            return

        logger.info(f"[FilesystemWatcher] New file detected: {src_path.name}")

        # Process the file
        self.watcher.process_file(src_path)


class FilesystemWatcher(BaseWatcher):
    """Watches Inbox/ folder for new file drops."""

    def __init__(self, config: Any, vault_path: Path):
        """
        Initialize Filesystem watcher.

        Args:
            config: Config with dry_run, etc.
            vault_path: Path to AI_Employee_Vault directory
        """
        super().__init__(config, vault_path)
        self.interval = 1  # Watchdog handles real-time monitoring
        self._observer = None
        self._handler = None

    def start_watching(self) -> None:
        """Start the watchdog observer."""
        inbox_path = self.vault_path / "Inbox"
        inbox_path.mkdir(parents=True, exist_ok=True)

        self._handler = DropFolderHandler(self)
        self._observer = Observer()
        self._observer.schedule(self._handler, str(inbox_path), recursive=False)
        self._observer.start()

        logger.info(f"[FilesystemWatcher] Watching {inbox_path} for new files")

    def stop_watching(self) -> None:
        """Stop the watchdog observer."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            logger.info("[FilesystemWatcher] Stopped watching")

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check for new files in Inbox (called by base run loop).
        For watchdog-based watcher, this is a no-op since events are pushed.
        """
        return []

    def process_file(self, src_path: Path) -> Optional[Path]:
        """
        Process a newly dropped file.

        Args:
            src_path: Path to the new file in Inbox

        Returns:
            Path to created action file, or None if DRY_RUN or error.
        """
        try:
            # Generate unique ID
            timestamp = datetime.now(timezone.utc)
            file_id = f"{src_path.stem}_{timestamp.strftime('%Y%m%d%H%M%S')}"

            if self._is_duplicate(file_id):
                logger.debug(f"File already processed: {file_id}")
                return None

            item = {
                'id': file_id,
                'type': 'file_drop',
                'from': 'Inbox Drop',
                'subject': f"New file: {src_path.name}",
                'received': timestamp.isoformat(),
                'priority': 'medium',
                'content': f"File dropped in Inbox: {src_path.name}",
                'file_path': str(src_path),
                'file_name': src_path.name,
                'file_size': src_path.stat().st_size if src_path.exists() else 0
            }

            return self.create_action_file(item)

        except Exception as e:
            logger.error(f"Error processing file: {e}", exc_info=True)
            return None

    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create a Needs_Action markdown file for the dropped file.
        Also copies the file to Needs_Action/ folder.

        Args:
            item: File dictionary from process_file()

        Returns:
            Path to created file, or None if DRY_RUN or error.
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create FILE_{item['id']}.md and copy {item['file_name']}")
            return None

        try:
            # Sanitize filename
            safe_name = re.sub(r'[^\w\-_]', '_', item['file_name'])
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            md_filename = f"FILE_{safe_name}_{timestamp}.md"
            filepath = self.needs_action_path / md_filename

            # Copy file to Needs_Action
            src = Path(item['file_path'])
            dst = self.needs_action_path / item['file_name']
            
            if src.exists():
                shutil.copy2(src, dst)
                logger.info(f"Copied file to {dst}")

            content = f"""---
type: file_drop
from: {item['from']}
subject: {item['subject']}
received: {item['received']}
priority: {item['priority']}
status: pending
watcher: FilesystemWatcher
file_name: {item['file_name']}
file_size: {item['file_size']} bytes
---
## File Description
A new file was dropped in the Inbox folder.

**File**: `{item['file_name']}`  
**Size**: {item['file_size']} bytes  
**Location**: `Needs_Action/{item['file_name']}`

## Suggested Actions
- [ ] Review the file content
- [ ] Determine required action
- [ ] Process accordingly (reply, archive, forward, etc.)
- [ ] Move file and this action file to /Done/ when complete
"""

            filepath.write_text(content, encoding='utf-8')
            logger.info(f"Created action file: {filepath}")
            return filepath

        except PermissionError as e:
            logger.error(f"Permission denied reading file: {e}")
            return None
        except shutil.Error as e:
            logger.error(f"Failed to copy file: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Failed to create action file: {e}", exc_info=True)
            return None

    def stop(self) -> None:
        """Cleanup watchdog observer."""
        logger.info("[FilesystemWatcher] Stopping watcher...")
        self.stop_watching()
