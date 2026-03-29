"""
Orchestrator — Master process that coordinates watchers and triggers Claude Code.
Watches /Needs_Action/ for new tasks and /Approved/ for action approvals.
"""
import logging
import subprocess
import time
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

from .config import Config
from .actions.audit_logger import AuditLogger
from .actions.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)


class NeedsActionHandler(FileSystemEventHandler):
    """Handles new files in Needs_Action/ folder."""

    def __init__(self, orchestrator: 'Orchestrator'):
        self.orchestrator = orchestrator

    def on_created(self, event):
        """Handle new action file creation."""
        if event.is_directory:
            return

        src_path = Path(event.src_path)

        # Only process .md files
        if src_path.suffix.lower() != '.md':
            return

        logger.info(f"[Orchestrator] New action file detected: {src_path.name}")

        # Trigger Claude Code to process
        self.orchestrator.trigger_claude_for_task(src_path)


class ApprovedHandler(FileSystemEventHandler):
    """Handles files moved to Approved/ folder."""

    def __init__(self, orchestrator: 'Orchestrator'):
        self.orchestrator = orchestrator

    def on_created(self, event):
        """Handle new approved file."""
        if event.is_directory:
            return

        src_path = Path(event.src_path)

        if src_path.suffix.lower() != '.md':
            return

        logger.info(f"[Orchestrator] Approval detected: {src_path.name}")

        # Trigger MCP action
        self.orchestrator.process_approved_file(src_path)


class Orchestrator:
    """
    Main orchestrator for the AI Employee system.
    Coordinates watchers, triggers Claude Code, and processes approvals.
    """

    def __init__(self, config: Config):
        """
        Initialize orchestrator.

        Args:
            config: Config instance (singleton)
        """
        self.config = config
        self.audit_logger = AuditLogger(config.logs_path)
        self.rate_limiter = RateLimiter(config.vault_path)

        self._needs_action_observer: Optional[Observer] = None
        self._approved_observer: Optional[Observer] = None

        # Ensure directories exist
        self.config.needs_action_path.mkdir(parents=True, exist_ok=True)
        self.config.approved_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"[Orchestrator] Initialized with vault: {config.vault_path}")

    def start_watching(self) -> None:
        """Start watching Needs_Action/ and Approved/ folders."""
        # Watch Needs_Action/
        self._needs_action_observer = Observer()
        needs_handler = NeedsActionHandler(self)
        self._needs_action_observer.schedule(
            needs_handler,
            str(self.config.needs_action_path),
            recursive=False
        )
        self._needs_action_observer.start()
        logger.info(f"[Orchestrator] Watching {self.config.needs_action_path}")

        # Watch Approved/
        self._approved_observer = Observer()
        approved_handler = ApprovedHandler(self)
        self._approved_observer.schedule(
            approved_handler,
            str(self.config.approved_path),
            recursive=False
        )
        self._approved_observer.start()
        logger.info(f"[Orchestrator] Watching {self.config.approved_path}")

        # Log startup
        self.audit_logger.log_action(
            action_type="orchestrator_start",
            actor="orchestrator",
            target=str(self.config.vault_path),
            result="success",
            dry_run=self.config.dry_run
        )

    def stop_watching(self) -> None:
        """Stop folder watchers."""
        logger.info("[Orchestrator] Stopping watchers...")

        if self._needs_action_observer:
            self._needs_action_observer.stop()
            self._needs_action_observer.join()

        if self._approved_observer:
            self._approved_observer.stop()
            self._approved_observer.join()

        logger.info("[Orchestrator] Stopped")

    def trigger_claude_for_task(self, action_file: Path) -> None:
        """
        Trigger Claude Code to process a new task.

        Args:
            action_file: Path to the new action file in Needs_Action/
        """
        try:
            # Check rate limit
            if not self.rate_limiter.check_and_increment('claude_api_call'):
                logger.warning("Claude API rate limit exceeded, queuing task")
                return

            # Read the action file
            content = action_file.read_text(encoding='utf-8')

            # Build Claude command
            prompt = f"""
You are the AI Employee agent. Process this new task from Needs_Action/.

## Action File: {action_file.name}

{content}

## Your Tasks:
1. Read the action file and understand the request
2. Check Company_Handbook.md for relevant rules
3. Create a plan in /Plans/PLAN_<task>.md
4. If action requires approval, create file in /Pending_Approval/
5. If approved (file in /Approved/), execute the action via MCP
6. Move all related files to /Done/ when complete
7. Update Dashboard.md with activity
8. Log all actions to /Logs/

## Rules:
- DRY_RUN={self.config.dry_run}
- Follow Company_Handbook.md rules
- Always log actions
- Never skip approval for payments or new contacts
"""

            # Call Claude Code
            logger.info(f"[Orchestrator] Triggering Claude for: {action_file.name}")

            result = subprocess.run(
                ['claude', '--prompt', prompt],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.info(f"[Orchestrator] Claude completed: {action_file.name}")
            else:
                logger.error(f"[Orchestrator] Claude failed: {result.stderr}")

            # Log the action
            self.audit_logger.log_action(
                action_type="claude_triggered",
                actor="orchestrator",
                target=str(action_file),
                parameters={'stdout': result.stdout[:500] if result.stdout else ''},
                result="success" if result.returncode == 0 else "failure",
                error=result.stderr if result.returncode != 0 else None,
                dry_run=self.config.dry_run
            )

        except subprocess.TimeoutExpired:
            logger.error(f"[Orchestrator] Claude timed out for: {action_file.name}")
            self.audit_logger.log_action(
                action_type="claude_timeout",
                actor="orchestrator",
                target=str(action_file),
                result="failure",
                error="Claude Code timed out after 300s",
                dry_run=self.config.dry_run
            )

        except Exception as e:
            logger.error(f"[Orchestrator] Error triggering Claude: {e}", exc_info=True)
            self.audit_logger.log_action(
                action_type="claude_error",
                actor="orchestrator",
                target=str(action_file),
                result="failure",
                error=str(e),
                dry_run=self.config.dry_run
            )

    def process_approved_file(self, approval_file: Path) -> None:
        """
        Process an approved action file.

        Args:
            approval_file: Path to the approved file
        """
        try:
            # Read approval file
            content = approval_file.read_text(encoding='utf-8')

            # Parse frontmatter to get action type
            action_type = self._extract_action_type(content)

            if not action_type:
                logger.warning(f"[Orchestrator] Could not determine action type: {approval_file.name}")
                return

            logger.info(f"[Orchestrator] Processing approved action: {action_type}")

            # Trigger appropriate MCP based on action type
            if action_type == 'send_email':
                self._trigger_email_mcp(approval_file, content)
            elif action_type == 'payment':
                self._trigger_payment_mcp(approval_file, content)
            elif action_type == 'social_post':
                self._trigger_social_mcp(approval_file, content)
            elif action_type == 'whatsapp_send':
                self._trigger_whatsapp_mcp(approval_file, content)
            else:
                logger.warning(f"[Orchestrator] Unknown action type: {action_type}")

        except Exception as e:
            logger.error(f"[Orchestrator] Error processing approved file: {e}", exc_info=True)

    def _extract_action_type(self, content: str) -> Optional[str]:
        """Extract action type from YAML frontmatter."""
        try:
            # Simple YAML parsing
            lines = content.split('\n')
            in_frontmatter = False

            for line in lines:
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                    continue

                if in_frontmatter and line.startswith('action:'):
                    return line.split(':', 1)[1].strip()

        except Exception as e:
            logger.warning(f"Could not parse frontmatter: {e}")

        return None

    def _trigger_email_mcp(self, approval_file: Path, content: str) -> None:
        """Trigger email MCP to send approved email."""
        logger.info("[Orchestrator] Would trigger Email MCP (not implemented)")
        # TODO: Implement email-mcp integration
        self.audit_logger.log_action(
            action_type="email_mcp_triggered",
            actor="orchestrator",
            target=str(approval_file),
            result="dry_run" if self.config.dry_run else "success",
            dry_run=self.config.dry_run
        )

    def _trigger_payment_mcp(self, approval_file: Path, content: str) -> None:
        """Trigger payment MCP for approved payment."""
        logger.info("[Orchestrator] Would trigger Payment MCP (not implemented)")
        # TODO: Implement payment-mcp integration
        self.audit_logger.log_action(
            action_type="payment_mcp_triggered",
            actor="orchestrator",
            target=str(approval_file),
            result="dry_run" if self.config.dry_run else "success",
            dry_run=self.config.dry_run
        )

    def _trigger_social_mcp(self, approval_file: Path, content: str) -> None:
        """Trigger social media MCP for approved post."""
        logger.info("[Orchestrator] Would trigger Social MCP (not implemented)")
        # TODO: Implement social-mcp integration
        self.audit_logger.log_action(
            action_type="social_mcp_triggered",
            actor="orchestrator",
            target=str(approval_file),
            result="dry_run" if self.config.dry_run else "success",
            dry_run=self.config.dry_run
        )

    def _trigger_whatsapp_mcp(self, approval_file: Path, content: str) -> None:
        """Trigger WhatsApp MCP for approved message."""
        logger.info("[Orchestrator] Would trigger WhatsApp MCP (not implemented)")
        # TODO: Implement whatsapp-mcp integration
        self.audit_logger.log_action(
            action_type="whatsapp_mcp_triggered",
            actor="orchestrator",
            target=str(approval_file),
            result="dry_run" if self.config.dry_run else "success",
            dry_run=self.config.dry_run
        )

    def run(self) -> None:
        """
        Main orchestrator loop.
        Runs indefinitely until interrupted.
        """
        logger.info("[Orchestrator] Starting main loop")

        self.start_watching()

        try:
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("[Orchestrator] Interrupted, stopping...")
        finally:
            self.stop_watching()


def main():
    """Entry point for orchestrator process."""
    import sys

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("AI_Employee_Vault/Logs/app.log"),
        ],
    )

    # Load config
    config = Config()

    if not config.validate():
        logger.error("Configuration validation failed")
        sys.exit(1)

    # Run orchestrator
    orchestrator = Orchestrator(config)
    orchestrator.run()


if __name__ == "__main__":
    main()
