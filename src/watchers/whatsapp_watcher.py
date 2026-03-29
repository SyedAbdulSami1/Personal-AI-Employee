"""
WhatsAppWatcher — Monitors WhatsApp Web for urgent messages.
Uses Playwright for browser automation.
Creates action files in /Needs_Action/ for Claude to process.
"""
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from .base_watcher import BaseWatcher

logger = logging.getLogger(__name__)


class WhatsAppWatcher(BaseWatcher):
    """Watches WhatsApp Web for urgent messages."""

    def __init__(self, config: Any, vault_path: Path):
        """
        Initialize WhatsApp watcher.

        Args:
            config: Config with whatsapp_session_path, dry_run, etc.
            vault_path: Path to AI_Employee_Vault directory
        """
        super().__init__(config, vault_path)
        self.interval = getattr(config, 'whatsapp_interval', 30)  # 30 seconds
        self.session_path = getattr(config, 'whatsapp_session_path', None)
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing', 'emergency']
        self._browser = None
        self._page = None

    def _init_browser(self):
        """Initialize Playwright browser with persistent context."""
        if self._browser is not None:
            return True

        try:
            from playwright.sync_api import sync_playwright

            playwright = sync_playwright().start()
            
            # Use persistent context for session storage
            user_data_dir = self.session_path or str(self.vault_path / "whatsapp_session")
            Path(user_data_dir).mkdir(parents=True, exist_ok=True)

            self._browser = playwright.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=True,  # Set to False first run for QR scan
                args=['--disable-blink-features=AutomationControlled']
            )

            self._page = self._browser.pages[0] if self._browser.pages else self._browser.new_page()
            
            # Navigate to WhatsApp Web
            self._page.goto('https://web.whatsapp.com', wait_until='networkidle')
            
            logger.info("WhatsApp Web browser initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}", exc_info=True)
            return False

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check WhatsApp for new urgent messages.

        Returns:
            List of message dictionaries ready for action file creation.
        """
        if not self._init_browser():
            logger.warning("WhatsApp browser not available, skipping check")
            return []

        try:
            items = []
            
            # Wait for chat list to load
            self._page.wait_for_selector('div[role="row"]', timeout=5000)
            
            # Get all chat rows
            chat_rows = self._page.query_selector_all('div[role="row"]')
            
            for row in chat_rows[:10]:  # Check top 10 chats
                try:
                    # Extract contact name
                    contact_elem = row.query_selector('span[title]')
                    if not contact_elem:
                        continue
                    contact = contact_elem.get_attribute('title')
                    
                    # Extract last message
                    msg_elem = row.query_selector('span[dir="auto"]')
                    if not msg_elem:
                        continue
                    message_text = msg_elem.inner_text()
                    
                    # Check if message contains urgent keywords
                    message_lower = message_text.lower()
                    if not any(kw in message_lower for kw in self.keywords):
                        continue
                    
                    # Generate unique ID
                    timestamp = datetime.now(timezone.utc)
                    msg_id = f"{contact}_{timestamp.strftime('%Y%m%d%H%M%S')}"
                    
                    if self._is_duplicate(msg_id):
                        continue

                    # Determine priority
                    priority = 'high' if any(kw in message_lower for kw in ['urgent', 'asap', 'emergency']) else 'medium'

                    items.append({
                        'id': msg_id,
                        'type': 'whatsapp',
                        'from': contact,
                        'subject': message_text[:100],
                        'received': timestamp.isoformat(),
                        'priority': priority,
                        'content': message_text,
                        'contact': contact
                    })

                except Exception as e:
                    logger.debug(f"Error processing chat row: {e}")
                    continue

            return items

        except Exception as e:
            logger.error(f"Error checking WhatsApp: {e}", exc_info=True)
            raise

    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create a Needs_Action markdown file for the WhatsApp message.

        Args:
            item: Message dictionary from check_for_updates()

        Returns:
            Path to created file, or None if DRY_RUN or error.
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create WHATSAPP_{item['id']}.md")
            return None

        try:
            # Sanitize filename
            safe_contact = re.sub(r'[^\w\-_]', '_', item['contact'])
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            filename = f"WHATSAPP_{safe_contact}_{timestamp}.md"
            filepath = self.needs_action_path / filename

            content = f"""---
type: whatsapp
from: {item['from']}
subject: {item['subject']}
received: {item['received']}
priority: {item['priority']}
status: pending
watcher: WhatsAppWatcher
contact: {item['contact']}
---
## Message Content
{item['content']}

## Suggested Actions
- [ ] Review the urgent message
- [ ] Draft appropriate response (requires approval for new contacts)
- [ ] Respond via WhatsApp (requires approval)
- [ ] Move to /Done/ when complete
"""

            filepath.write_text(content, encoding='utf-8')
            logger.info(f"Created action file: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to create action file: {e}", exc_info=True)
            return None

    def stop(self) -> None:
        """Cleanup browser connections."""
        logger.info("[WhatsAppWatcher] Stopping watcher...")
        if self._browser:
            try:
                self._browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            finally:
                self._browser = None
                self._page = None
