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
from .actions.social_poster import SocialMediaPoster
from .actions.odoo_client import OdooClient
from .actions.email_action import EmailAction
from .actions.browser_action import BrowserAction

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
        
        # New action handlers
        self.social_media_poster = SocialMediaPoster(config)
        self.odoo_client = OdooClient(config)
        self.email_action = EmailAction(config)
        self.browser_action = BrowserAction(config)

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

    def _extract_field(self, content: str, field_name: str) -> Optional[str]:
        """Extract a field from YAML frontmatter."""
        try:
            # Simple YAML parsing
            lines = content.split('\n')
            in_frontmatter = False

            for line in lines:
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                    continue

                if in_frontmatter and line.startswith(f'{field_name}:'):
                    return line.split(':', 1)[1].strip()

        except Exception as e:
            logger.warning(f"Could not parse frontmatter for {field_name}: {e}")

        return None

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
            action_type = self._extract_field(content, 'action')

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
            elif action_type == 'accounting' or action_type == 'odoo':
                self._trigger_odoo_mcp(approval_file, content)
            else:
                logger.warning(f"[Orchestrator] Unknown action type: {action_type}")

        except Exception as e:
            logger.error(f"[Orchestrator] Error processing approved file: {e}", exc_info=True)

    def _trigger_email_mcp(self, approval_file: Path, content: str) -> None:
        """Trigger email MCP to send approved email."""
        logger.info(f"[Orchestrator] Triggering EmailAction for: {approval_file.name}")
        
        # Extract details from content
        to = self._extract_field(content, 'to') or "unknown@example.com"
        subject = self._extract_field(content, 'subject') or "No Subject"
        
        # Simple extraction of body
        body = content.split("## Content")[-1].strip() if "## Content" in content else content
        
        try:
            result = self.email_action.execute(to=to, subject=subject, body=body)
            logger.info(f"[Orchestrator] Email result: {result['status']}")
            
            # Move to Done if success
            if result['status'] == 'success' or self.config.dry_run:
                self._move_to_done(approval_file)
        except Exception as e:
            logger.error(f"[Orchestrator] Email failed: {e}")

    def _trigger_payment_mcp(self, approval_file: Path, content: str) -> None:
        """Trigger payment MCP for approved payment."""
        logger.info(f"[Orchestrator] Triggering BrowserAction (Payment) for: {approval_file.name}")
        
        # Extract details
        amount = self._extract_field(content, 'amount') or "0"
        recipient = self._extract_field(content, 'recipient') or "Unknown"
        
        try:
            # Simulate navigating to a bank/payment portal
            result = self.browser_action.execute(
                url="https://bank.example.com/pay",
                action_data={'type': 'payment', 'amount': amount, 'recipient': recipient}
            )
            logger.info(f"[Orchestrator] Payment result: {result['status']}")
            
            if result['status'] == 'success' or self.config.dry_run:
                self._move_to_done(approval_file)
        except Exception as e:
            logger.error(f"[Orchestrator] Payment failed: {e}")

    def _move_to_done(self, file_path: Path) -> None:
        """Move a processed file to the Done folder."""
        try:
            done_path = self.config.done_path / file_path.name
            file_path.rename(done_path)
            logger.info(f"Moved {file_path.name} to Done/")
        except Exception as e:
            logger.error(f"Failed to move file to Done: {e}")

    def _trigger_social_mcp(self, approval_file: Path, content: str) -> None:
        """Trigger social media MCP for approved post."""
        logger.info(f"[Orchestrator] Triggering SocialMediaPoster for: {approval_file.name}")
        
        # Simple extraction of platform and content
        # Expects frontmatter: platform: linkedin
        platform = self._extract_field(content, 'platform') or 'linkedin'
        post_content = content.split("## Content")[-1].strip() if "## Content" in content else content
        
        try:
            result = self.social_media_poster.execute(
                content=post_content,
                platform=platform,
                title=approval_file.stem
            )
            logger.info(f"[Orchestrator] {platform.capitalize()} post result: {result['status']}")
        except Exception as e:
            logger.error(f"[Orchestrator] {platform.capitalize()} posting failed: {e}")

    def _trigger_odoo_mcp(self, approval_file: Path, content: str) -> None:
        """Trigger Odoo MCP for approved accounting action."""
        logger.info(f"[Orchestrator] Triggering OdooClient for: {approval_file.name}")
        
        # This would typically parse JSON/YAML from the markdown content
        # For now, we simulate a search call
        try:
            # Simulation of an accounting search or create
            result = self.odoo_client.execute(
                model='res.partner',
                method='search_read',
                kwargs={'limit': 1}
            )
            logger.info(f"[Orchestrator] Odoo action completed successfully")
        except Exception as e:
            logger.error(f"[Orchestrator] Odoo action failed: {e}")

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
