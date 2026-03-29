"""
GmailWatcher — Monitors Gmail for important unread emails.
Creates action files in /Needs_Action/ for Claude to process.
"""
import logging
import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from email.parser import Parser

from .base_watcher import BaseWatcher

logger = logging.getLogger(__name__)


class GmailWatcher(BaseWatcher):
    """Watches Gmail inbox for important unread emails."""

    def __init__(self, config: Any, vault_path: Path):
        """
        Initialize Gmail watcher.

        Args:
            config: Config with gmail_credentials_path, dry_run, etc.
            vault_path: Path to AI_Employee_Vault directory
        """
        super().__init__(config, vault_path)
        self.interval = getattr(config, 'gmail_interval', 120)  # 120 seconds
        self.credentials_path = getattr(config, 'gmail_credentials_path', None)
        self.query = "is:unread is:important"
        self._service = None

    def _get_service(self):
        """Lazy-load Gmail API service with OAuth2."""
        if self._service is not None:
            return self._service

        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from google.auth.transport.requests import Request
            import pickle
            import os

            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            TOKEN_FILE = self.vault_path / "Logs" / "gmail_token.pickle"

            creds = None

            # Load existing token
            if os.path.exists(TOKEN_FILE):
                with open(TOKEN_FILE, 'rb') as token:
                    creds = pickle.load(token)

            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not self.credentials_path:
                        logger.error("Gmail credentials path not configured")
                        return None

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save token
                TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(TOKEN_FILE, 'wb') as token:
                    pickle.dump(creds, token)

            self._service = build('gmail', 'v1', credentials=creds)
            logger.info("Gmail API service initialized")
            return self._service

        except Exception as e:
            logger.error(f"Failed to initialize Gmail API: {e}", exc_info=True)
            return None

    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check Gmail for new important unread emails.

        Returns:
            List of email dictionaries ready for action file creation.
        """
        service = self._get_service()
        if not service:
            logger.warning("Gmail service not available, skipping check")
            return []

        try:
            # Search for messages
            results = service.users().messages().list(
                userId='me',
                q=self.query,
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            items = []

            for msg in messages:
                msg_id = msg['id']

                if self._is_duplicate(msg_id):
                    continue

                # Fetch full message
                full_msg = service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()

                # Parse headers
                headers = full_msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')

                # Parse body
                body = self._extract_body(full_msg)

                # Determine priority
                priority = self._determine_priority(subject, from_addr)

                items.append({
                    'id': msg_id,
                    'type': 'email',
                    'from': from_addr,
                    'subject': subject[:100],  # Max 100 chars
                    'received': self._parse_date(date_str),
                    'priority': priority,
                    'content': body,
                    'thread_id': full_msg.get('threadId', '')
                })

            return items

        except Exception as e:
            logger.error(f"Error checking Gmail: {e}", exc_info=True)
            raise

    def _extract_body(self, full_msg: Dict) -> str:
        """Extract plain text body from Gmail message."""
        try:
            payload = full_msg['payload']

            # Try multipart first
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        return base64.urlsafe_b64decode(data).decode('utf-8')

            # Try single part
            if payload['mimeType'] == 'text/plain':
                data = payload['body'].get('data', '')
                return base64.urlsafe_b64decode(data).decode('utf-8')

            # Fallback to HTML (strip tags)
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/html':
                        data = part['body'].get('data', '')
                        html = base64.urlsafe_b64decode(data).decode('utf-8')
                        # Simple HTML strip
                        return ''.join(tag for tag in html if tag not in '<>')

            return "No readable content"

        except Exception as e:
            logger.warning(f"Could not extract email body: {e}")
            return "[Could not extract message body]"

    def _determine_priority(self, subject: str, from_addr: str) -> str:
        """Determine email priority based on keywords."""
        urgent_keywords = ['urgent', 'asap', 'emergency', 'immediate', 'critical']
        high_keywords = ['invoice', 'payment', 'deadline', 'review', 'approval']

        subject_lower = subject.lower()
        from_lower = from_addr.lower()

        if any(kw in subject_lower for kw in urgent_keywords):
            return 'high'
        elif any(kw in subject_lower for kw in high_keywords):
            return 'medium'
        else:
            return 'low'

    def _parse_date(self, date_str: str) -> str:
        """Parse email date to ISO 8601 format."""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except Exception:
            return datetime.now(timezone.utc).isoformat()

    def create_action_file(self, item: Dict[str, Any]) -> Optional[Path]:
        """
        Create a Needs_Action markdown file for the email.

        Args:
            item: Email dictionary from check_for_updates()

        Returns:
            Path to created file, or None if DRY_RUN or error.
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would create EMAIL_{item['id']}.md")
            return None

        try:
            filename = f"EMAIL_{item['id']}.md"
            filepath = self.needs_action_path / filename

            timestamp = datetime.now(timezone.utc).isoformat()

            content = f"""---
type: email
from: {item['from']}
subject: {item['subject']}
received: {item['received']}
priority: {item['priority']}
status: pending
watcher: GmailWatcher
---
## Content
{item['content']}

## Suggested Actions
- [ ] Read and understand the email
- [ ] Determine appropriate response
- [ ] Draft reply (requires approval for new contacts)
- [ ] Move to /Done/ when complete
"""

            filepath.write_text(content, encoding='utf-8')
            logger.info(f"Created action file: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to create action file: {e}", exc_info=True)
            return None

    def stop(self) -> None:
        """Cleanup Gmail connections."""
        logger.info("[GmailWatcher] Stopping watcher...")
        if self._service:
            self._service = None
