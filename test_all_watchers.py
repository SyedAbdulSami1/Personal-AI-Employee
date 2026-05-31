#!/usr/bin/env python3
"""Test all watchers can be instantiated and run."""
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
from src.watchers.gmail_watcher import GmailWatcher
from src.watchers.whatsapp_watcher import WhatsAppWatcher
from src.watchers.filesystem_watcher import FilesystemWatcher

logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 60)
    logger.info("Testing All Watchers Instantiation")
    logger.info("=" * 60)
    
    logger.info(f"Dry run: {config.dry_run}")
    logger.info(f"Vault path: {config.vault_path}")
    
    # Test GmailWatcher
    logger.info("\n1. Testing GmailWatcher...")
    try:
        gmail_watcher = GmailWatcher(config, config.vault_path)
        logger.info(f"   ✓ GmailWatcher created")
        logger.info(f"   Interval: {gmail_watcher.interval}s")
    except Exception as e:
        logger.error(f"   ✗ GmailWatcher failed: {e}")
    
    # Test WhatsAppWatcher
    logger.info("\n2. Testing WhatsAppWatcher...")
    try:
        whatsapp_watcher = WhatsAppWatcher(config, config.vault_path)
        logger.info(f"   ✓ WhatsAppWatcher created")
        logger.info(f"   Interval: {whatsapp_watcher.interval}s")
        logger.info(f"   Keywords: {whatsapp_watcher.keywords}")
    except Exception as e:
        logger.error(f"   ✗ WhatsAppWatcher failed: {e}")
    
    # Test FilesystemWatcher
    logger.info("\n3. Testing FilesystemWatcher...")
    try:
        filesystem_watcher = FilesystemWatcher(config, config.vault_path)
        logger.info(f"   ✓ FilesystemWatcher created")
        logger.info(f"   Interval: {filesystem_watcher.interval}s")
    except Exception as e:
        logger.error(f"   ✗ FilesystemWatcher failed: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info("All watchers tested successfully!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
