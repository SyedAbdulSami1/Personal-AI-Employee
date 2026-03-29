---
name: watcher-creator
description: This skill should be used when creating new Watcher scripts that extend BaseWatcher. Use when user needs to monitor new data sources (email, messaging apps, file systems, APIs) and create action files in Needs_Action/ folder.
---

# Watcher Creator Skill

## Purpose

Create new Watcher scripts that follow the established BaseWatcher pattern. Watchers are responsible for:
- Polling external data sources at defined intervals
- Detecting new/updated content
- Creating standardized action files in `AI_Employee_Vault/Needs_Action/`
- Running as PM2-managed processes

## When to Use This Skill

✅ User says: "Add a new watcher for..."
✅ User needs to monitor: Slack, Discord, SMS, RSS feeds, webhooks, APIs
✅ User wants to detect: New files, messages, emails, events
✅ Existing watchers (Gmail, WhatsApp, Filesystem) don't cover the use case

❌ Don't use for: Creating Actions (use action-builder skill)
❌ Don't use for: Modifying existing watchers unless refactoring

---

## Watcher Architecture

```
src/watchers/
├── base_watcher.py          ← BaseWatcher(ABC) - DO NOT MODIFY
├── gmail_watcher.py         ← GmailWatcher(BaseWatcher)
├── whatsapp_watcher.py      ← WhatsAppWatcher(BaseWatcher)
├── filesystem_watcher.py    ← DropFolderHandler(FileSystemEventHandler)
└── <new_watcher>.py         ← Create new watchers here
```

### BaseWatcher Interface

Every watcher MUST extend `BaseWatcher` and implement:

```python
from abc import ABC, abstractmethod
import logging
logger = logging.getLogger(__name__)

class NewWatcher(BaseWatcher):
    """
    Docstring: What this watcher monitors and why.
    """
    
    # Required class attributes
    interval: int  # Seconds between checks (e.g., 30, 60, 120, 300)
    source_name: str  # Human-readable name for logging
    
    @abstractmethod
    async def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Poll the data source and return list of new items.
        Each item should contain all data needed for the action file.
        """
        pass
    
    @abstractmethod
    def create_action_file(self, item: Dict[str, Any]) -> str:
        """
        Create a Needs_Action/<TYPE>_<id>.md file using Schema A.
        Returns the created file path.
        """
        pass
```

---

## Implementation Process

### Step 1: Understand the Data Source

Ask the user:
1. **What platform/service?** (Slack, Discord, SMS, RSS, custom API)
2. **Authentication method?** (OAuth2, API key, session token, basic auth)
3. **What triggers detection?** (keywords, time range, unread status, new files)
4. **Polling frequency?** (every 30s, 2min, 5min, 15min)
5. **Rate limits?** (API calls per minute/hour)

### Step 2: Check for Existing Libraries

Search for Python packages:
```bash
# Example searches
pip search slack-sdk
pip search discord.py
pip search twilio  # for SMS
```

**Preferred libraries:**
- Official SDKs first
- Well-maintained (last commit <6 months)
- High download count
- Good documentation

### Step 3: Create the Watcher File

**File location:** `src/watchers/<source>_watcher.py`

**Template:**
```python
"""
<Source> Watcher - Monitors <source> for <trigger condition>.

Interval: <N> seconds
Authentication: <method>
Output: Needs_Action/<TYPE>_<id>.md
"""

import os
import time
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path

from base_watcher import BaseWatcher
from config import Config

import logging
logger = logging.getLogger(__name__)


class <Source>Watcher(BaseWatcher):
    """
    Monitors <source> for <trigger condition>.
    
    Creates action files when:
    - <condition 1>
    - <condition 2>
    """
    
    interval = <N>  # seconds
    source_name = "<Source>"
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.vault_path = Path(config.vault_path)
        self.needs_action_dir = self.vault_path / "Needs_Action"
        self.processed_ids: set = set()  # Dedup in-memory
        
        # Initialize client
        self.client = self._init_client()
    
    def _init_client(self):
        """Initialize the <source> API client."""
        # Load credentials from config (NOT os.getenv directly)
        api_key = self.config.<SOURCE>_API_KEY
        # Initialize and return client
        pass
    
    async def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Poll <source> and return list of new items.
        
        Returns:
            List of dicts with keys: id, from, subject, received, priority, content
        """
        logger.info("[%s] Checking for updates...", self.source_name)
        
        try:
            # Query API
            items = await self._fetch_items()
            
            # Filter to only new items (dedup)
            new_items = [
                item for item in items
                if item['id'] not in self.processed_ids
            ]
            
            # Update processed set
            for item in new_items:
                self.processed_ids.add(item['id'])
            
            logger.info("[%s] Found %d new items", self.source_name, len(new_items))
            return new_items
            
        except Exception as e:
            logger.error("[%s] Error checking updates: %s", self.source_name, e, exc_info=True)
            return []
    
    def create_action_file(self, item: Dict[str, Any]) -> str:
        """
        Create Needs_Action/<TYPE>_<id>.md using Schema A.
        
        Schema A frontmatter:
        ---
        type: <source>
        from: <sender>
        subject: <subject/max 100 chars>
        received: <ISO 8601>
        priority: high|medium|low
        status: pending
        watcher: <Source>Watcher
        ---
        """
        timestamp = datetime.fromisoformat(item['received']).strftime('%Y-%m-%d')
        filename = f"{item.get('type', 'MESSAGE')}_{item['id']}_{timestamp}.md"
        filepath = self.needs_action_dir / filename
        
        # Ensure directory exists
        self.needs_action_dir.mkdir(parents=True, exist_ok=True)
        
        # Build markdown content
        content = f"""---
type: {item.get('type', 'message')}
from: {item['from']}
subject: {item['subject'][:100]}
received: {item['received']}
priority: {item.get('priority', 'medium')}
status: pending
watcher: {self.source_name}Watcher
---

## Content
{item['content']}

## Suggested Actions
- [ ] Review and respond
- [ ] {item.get('suggested_action', 'Take appropriate action')}
"""
        
        # DRY_RUN check
        if self.config.dry_run:
            logger.info("[DRY RUN] %s would create: %s", self.source_name, filename)
            return str(filepath)
        
        # Write file
        filepath.write_text(content, encoding='utf-8')
        logger.info("[%s] Created: %s", self.source_name, filename)
        
        return str(filepath)
    
    async def _fetch_items(self) -> List[Dict[str, Any]]:
        """
        Internal method to fetch items from API.
        Implement API-specific logic here.
        """
        pass
    
    def run(self):
        """
        Main loop - inherited from BaseWatcher.
        DO NOT OVERRIDE unless absolutely necessary.
        """
        logger.info("[%s] Starting... (interval: %ds)", self.source_name, self.interval)
        
        while True:
            try:
                # Check for updates
                new_items = asyncio.run(self.check_for_updates())
                
                # Create action files
                for item in new_items:
                    self.create_action_file(item)
                
                # Wait for next interval
                time.sleep(self.interval)
                
            except KeyboardInterrupt:
                logger.info("[%s] Stopped by user", self.source_name)
                break
            except Exception as e:
                logger.error("[%s] Loop error: %s", self.source_name, e, exc_info=True)
                time.sleep(self.interval)  # Continue on error


if __name__ == "__main__":
    from config import Config
    config = Config()
    watcher = <Source>Watcher(config)
    watcher.run()
```

### Step 4: Add to PM2 Config

Update `ecosystem.config.js`:

```javascript
{
  name: "<source>_watcher",
  script: "python",
  args: "src/watchers/<source>_watcher.py",
  cwd: "/abs/path/to/project",
  env: { PYTHONPATH: "./src" },
  error_file: "AI_Employee_Vault/Logs/pm2/<source>_watcher.err.log",
  out_file: "AI_Employee_Vault/Logs/pm2/<source>_watcher.out.log",
  log_date_format: "YYYY-MM-DD HH:mm:ss",
  restart_delay: 5000,
  max_restarts: 10
}
```

### Step 5: Add Environment Variables

Update `.env.example`:

```bash
# <Source> Watcher
<SOURCE>_API_KEY=
<SOURCE>_SECRET=
<SOURCE>_TOKEN=
```

### Step 6: Update Config Class

Add new fields to `src/config.py`:

```python
@dataclass
class Config:
    # ... existing fields ...
    
    # <Source> Watcher
    <source>_api_key: str = field(default_factory=lambda: os.getenv('<SOURCE>_API_KEY', ''))
    <source>_secret: str = field(default_factory=lambda: os.getenv('<SOURCE>_SECRET', ''))
```

---

## Testing Checklist

Before marking watcher as complete:

### Unit Tests
- [ ] `_init_client()` returns valid client
- [ ] `check_for_updates()` returns list (even if empty)
- [ ] `create_action_file()` creates valid Schema A markdown
- [ ] DRY_RUN mode doesn't write files
- [ ] Deduplication works (processed_ids prevents duplicates)

### Integration Tests
- [ ] Watcher starts without errors
- [ ] Polling interval is respected
- [ ] Action files appear in `Needs_Action/`
- [ ] PM2 can manage the process
- [ ] Logs appear in `Logs/pm2/<source>_watcher.*.log`

### Error Handling
- [ ] Network errors are caught and logged
- [ ] Auth errors trigger ALERT file
- [ ] Rate limits trigger backoff
- [ ] Process restarts on crash (watchdog)

---

## Common Watcher Patterns

### Pattern 1: OAuth2 (Gmail-style)
```python
def _init_client(self):
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    
    creds = Credentials.from_authorized_user_file(
        self.config.<SOURCE>_CREDENTIALS_PATH
    )
    return build('<service>', 'v1', credentials=creds)
```

### Pattern 2: API Key (Simple REST)
```python
def _init_client(self):
    import requests
    self.session = requests.Session()
    self.session.headers.update({
        'Authorization': f'Bearer {self.config.<SOURCE>_API_KEY}'
    })
    return self.session
```

### Pattern 3: WebSocket (Real-time)
```python
async def check_for_updates(self):
    # Maintain persistent connection
    async with websockets.connect(self.ws_url) as ws:
        async for message in ws:
            yield self._parse_message(message)
```

### Pattern 4: Polling with Cursor (Pagination)
```python
async def _fetch_items(self):
    items = []
    cursor = self._load_cursor()  # From last run
    
    while True:
        resp = await self.client.get(f'/items?cursor={cursor}')
        batch = resp.json()['items']
        items.extend(batch)
        
        if not resp.json().get('has_more'):
            break
        cursor = resp.json()['next_cursor']
    
    self._save_cursor(cursor)
    return items
```

---

## Error Recovery

All watchers MUST implement:

```python
@with_retry(max_attempts=3, base_delay=1, max_delay=60)
async def check_for_updates(self):
    # External API calls wrapped with retry decorator
    pass
```

**Error categories:**

| Error Type | Handler |
|------------|---------|
| Network timeout | Retry with backoff |
| Rate limit (429) | Retry after `Retry-After` header |
| Auth 401/403 | Log ERROR + write ALERT + pause |
| Parse error | Log ERROR + skip item + continue |
| API down | Queue locally + process when restored |

---

## Console Output Standards

Every watcher MUST log:

```
[<Source>Watcher] Starting...
[<Source>Watcher] Found N new items
[<Source>Watcher] Created <filename>.md
[ERROR] <full message with traceback>
```

**Logging configuration:**
```python
# Entry point only (in __main__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("AI_Employee_Vault/Logs/app.log"),
    ],
)

# In watcher file (top only)
import logging
logger = logging.getLogger(__name__)
```

---

## Reference Files

- [BaseWatcher Implementation](../../src/watchers/base_watcher.py)
- [GmailWatcher Example](../../src/watchers/gmail_watcher.py)
- [WhatsAppWatcher Example](../../src/watchers/whatsapp_watcher.py)
- [Schema A Template](../vault-schema/reference/schema-a.md)
- [Retry Handler](../../src/actions/retry_handler.py)
- [Config Class](../../src/config.py)
- [PM2 Config](../../ecosystem.config.js)

---

## Examples

### Example 1: Slack Watcher

**User request:** "Monitor Slack for urgent messages"

**Implementation:**
```python
class SlackWatcher(BaseWatcher):
    interval = 30  # seconds
    source_name = "Slack"
    
    def _init_client(self):
        from slack_sdk import WebClient
        return WebClient(token=self.config.SLACK_BOT_TOKEN)
    
    async def check_for_updates(self):
        # Search for messages with keywords
        keywords = ['urgent', 'asap', 'help', 'emergency']
        items = []
        
        for keyword in keywords:
            result = self.client.search_messages(
                query=f'{keyword} in:all',
                count=10
            )
            for msg in result['messages']['matches']:
                items.append({
                    'id': msg['iid'],  # Unique ID
                    'type': 'SLACK',
                    'from': msg['user'],
                    'subject': msg['text'][:50],
                    'received': datetime.utcnow().isoformat() + 'Z',
                    'priority': 'high',
                    'content': msg['text'],
                    'channel': msg['channel']['name']
                })
        
        return items
```

### Example 2: RSS Feed Watcher

**User request:** "Monitor RSS feeds for breaking news"

**Implementation:**
```python
class RSSWatcher(BaseWatcher):
    interval = 300  # 5 minutes
    source_name = "RSS"
    
    def __init__(self, config: Config):
        super().__init__(config)
        self.feeds = [
            'https://example.com/rss',
            'https://news.com/feed',
        ]
        self.processed_urls: set = set()
    
    async def check_for_updates(self):
        import feedparser
        items = []
        
        for feed_url in self.feeds:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                if entry.link not in self.processed_urls:
                    items.append({
                        'id': hashlib.md5(entry.link.encode()).hexdigest()[:8],
                        'type': 'RSS',
                        'from': feed.feed.title,
                        'subject': entry.title,
                        'received': datetime.utcnow().isoformat() + 'Z',
                        'priority': 'medium',
                        'content': entry.get('summary', entry.title),
                        'url': entry.link
                    })
                    self.processed_urls.add(entry.link)
        
        return items
```

---

## Anti-Patterns (Avoid These)

❌ **Hardcoding credentials** - Always use `config.<FIELD>`
❌ **Scattered `os.getenv()` calls** - Config reads .env once
❌ **No DRY_RUN check** - Always guard external actions
❌ **Silent failures** - Always log with `exc_info=True`
❌ **Infinite loops without sleep** - Always `time.sleep(interval)`
❌ **No deduplication** - Track processed IDs
❌ **Copying BaseWatcher code** - Extend, don't copy
❌ **Ignoring rate limits** - Implement backoff

---

## Success Metrics

✅ New watcher follows BaseWatcher pattern exactly
✅ Action files use Schema A format
✅ DRY_RUN mode works (no files written when true)
✅ PM2 can manage the process
✅ Logs appear in correct locations
✅ Error handling covers all categories
✅ No credentials in code
✅ Deduplication prevents duplicates

---

**Created from:** AI Employee Hackathon - Watcher Architecture
**Pattern proven:** GmailWatcher, WhatsAppWatcher, FilesystemWatcher
