"""
AI Employee — Main Entry Point
Run watchers and orchestrator via PM2 or directly for testing.
"""
import logging
import sys
import argparse
from pathlib import Path

from src.config import Config
from src.actions.audit_logger import AuditLogger
from src.actions.rate_limiter import RateLimiter


def setup_logging(config: Config) -> None:
    """Configure logging for the entire application."""
    log_file = config.logs_path / "app.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file),
        ],
    )

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("googleapiclient").setLevel(logging.WARNING)


def run_watcher(watcher_name: str, config: Config) -> None:
    """
    Run a specific watcher for testing.

    Args:
        watcher_name: Name of watcher to run ('gmail', 'whatsapp', 'filesystem')
        config: Config instance
    """
    logger = logging.getLogger(__name__)

    if watcher_name == 'gmail':
        from src.watchers.gmail_watcher import GmailWatcher
        watcher = GmailWatcher(config, config.vault_path)
        logger.info("Starting GmailWatcher...")
        watcher.run()

    elif watcher_name == 'whatsapp':
        from src.watchers.whatsapp_watcher import WhatsAppWatcher
        watcher = WhatsAppWatcher(config, config.vault_path)
        logger.info("Starting WhatsAppWatcher...")
        watcher.run()

    elif watcher_name == 'filesystem':
        from src.watchers.filesystem_watcher import FilesystemWatcher
        watcher = FilesystemWatcher(config, config.vault_path)
        watcher.start_watching()
        logger.info("Starting FilesystemWatcher...")

        try:
            while True:
                pass
        except KeyboardInterrupt:
            watcher.stop_watching()

    else:
        logger.error(f"Unknown watcher: {watcher_name}")
        sys.exit(1)


def run_orchestrator(config: Config) -> None:
    """
    Run the orchestrator.

    Args:
        config: Config instance
    """
    from src.orchestrator import Orchestrator

    orchestrator = Orchestrator(config)
    orchestrator.run()


def run_watchdog(config: Config) -> None:
    """
    Run the watchdog monitor.

    Args:
        config: Config instance
    """
    from src.watchdog import ProcessMonitor

    monitor = ProcessMonitor(config)
    monitor.run()


def main():
    """Main entry point with CLI."""
    parser = argparse.ArgumentParser(description="AI Employee — Personal Digital FTE")
    parser.add_argument(
        'command',
        nargs='?',
        choices=['orchestrator', 'gmail', 'whatsapp', 'filesystem', 'watchdog'],
        help='Component to run'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Override DRY_RUN setting from .env'
    )
    parser.add_argument(
        '--vault',
        type=str,
        help='Override vault path'
    )

    args = parser.parse_args()

    # Load config
    config = Config()

    # Override from args
    if args.dry_run:
        config.dry_run = True
    if args.vault:
        config.vault_path = Path(args.vault)

    # Validate
    if not config.validate():
        sys.exit(1)

    # Setup logging
    setup_logging(config)

    logger = logging.getLogger(__name__)
    logger.info(f"AI Employee v{__import__('src').__version__}")
    logger.info(f"Vault: {config.vault_path}")
    logger.info(f"DRY_RUN: {config.dry_run}")

    # Run requested component
    if args.command == 'orchestrator':
        run_orchestrator(config)
    elif args.command == 'gmail':
        run_watcher('gmail', config)
    elif args.command == 'whatsapp':
        run_watcher('whatsapp', config)
    elif args.command == 'filesystem':
        run_watcher('filesystem', config)
    elif args.command == 'watchdog':
        run_watchdog(config)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
