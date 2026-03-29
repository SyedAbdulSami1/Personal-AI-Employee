#!/usr/bin/env python3
"""Test script for watchers."""
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

from src.config import config
from src.watchers.filesystem_watcher import FilesystemWatcher

logger = logging.getLogger(__name__)

def main():
    logger.info("Starting watcher test")
    logger.info(f"Dry run: {config.dry_run}")
    logger.info(f"Inbox path: {config.inbox_path}")
    logger.info(f"Inbox exists: {config.inbox_path.exists()}")
    
    watcher = FilesystemWatcher(config)
    logger.info("FilesystemWatcher created")
    
    test_file = config.inbox_path / 'test_document.pdf'
    logger.info(f"Test file exists: {test_file.exists()}")
    
    if test_file.exists():
        logger.info("Processing test file...")
        watcher._process_file_drop(str(test_file))
        logger.info("File processed")
    
    # List Needs_Action contents
    logger.info(f"\nNeeds_Action contents:")
    for f in config.needs_action_path.glob("*.md"):
        logger.info(f"  - {f.name}")

if __name__ == "__main__":
    main()
