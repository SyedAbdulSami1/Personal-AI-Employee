---
name: error-recovery
description: This skill should be used when debugging errors, implementing retry logic, handling failures, or recovering from crashes in the AI Employee system. Use when any component (watcher, action, orchestrator) fails or behaves unexpectedly.
---

# Error Recovery Skill

## Purpose

Provide standardized error handling, retry logic, and recovery patterns for all AI Employee components. Every error must be logged, categorized, and handled appropriately—never silently ignored.

## When to Use This Skill

✅ User says: "This is failing..." or "I'm getting an error..."
✅ Any component crashes (watcher, action, orchestrator)
✅ API calls fail (network, rate limit, auth errors)
✅ Need to implement retry logic for external calls
✅ Need to debug PM2 process failures
✅ Need to recover from vault file corruption

---

## Core Principles

### 1. Errors Must Be Loud, Never Silent

**FORBIDDEN everywhere:**
```python
except Exception: pass          # hides bugs
except Exception as e: print(e) # no traceback, no file log
```

**REQUIRED everywhere:**
```python
except SomeError as e:
    logger.error("Attempted: %s | Error: %s", context, e, exc_info=True)
```

### 2. Categorize Errors Before Handling

| Category | Examples | Handler |
|----------|----------|---------|
| **Transient** | Network timeout, API rate limit | Exponential backoff: 1s→2s→4s (max 60s) |
| **Authentication** | Expired token, 401/403 | Log ERROR + ALERT + pause (NEVER retry) |
| **Logic** | Qwen misinterprets task | Move to Rejected/ + human review |
| **Data** | Corrupted .md, missing field | Quarantine + log + continue |
| **System** | Orchestrator crash, disk full | Watchdog restarts + ALERT file |

### 3. DRY_RUN Mode for Safe Testing

```python
if self.config.dry_run:
    logger.info("[DRY RUN] %s would: %s", self.__class__.__name__, action)
    return None
# real execution below
```

**Default:** `DRY_RUN=true` in `.env`
**Production:** Set `DRY_RUN=false` only after manual end-to-end test passes

---

## Retry Handler (@with_retry)

### Implementation

**File:** `src/actions/retry_handler.py`

```python
"""
Retry decorator with exponential backoff.
All external API calls MUST use this decorator.
"""

import time
from functools import wraps
import logging
logger = logging.getLogger(__name__)


def with_retry(max_attempts=3, base_delay=1, max_delay=60):
    """
    Decorator for exponential backoff retry logic.
    
    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1)
        max_delay: Maximum delay in seconds (default: 60)
    
    Usage:
        @with_retry(max_attempts=3, base_delay=1, max_delay=60)
        async def call_external_api():
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except (TimeoutError, ConnectionError, RateLimitError) as e:
                    if attempt == max_attempts - 1:
                        logger.error(
                            "Max retries exceeded: %s | Function: %s | Args: %s",
                            e, func.__name__, args, exc_info=True
                        )
                        raise
                    
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(
                        "Attempt %d/%d failed, retrying in %ds: %s",
                        attempt + 1, max_attempts, delay, e
                    )
                    time.sleep(delay)
        return wrapper
    return decorator
```

### Usage Examples

**Watcher (Gmail API call):**
```python
from retry_handler import with_retry

class GmailWatcher(BaseWatcher):
    @with_retry(max_attempts=3, base_delay=1, max_delay=60)
    async def check_for_updates(self):
        # Gmail API call
        response = self.client.users().messages().list(...).execute()
        return response
```

**Action (Email send):**
```python
from retry_handler import with_retry

class EmailAction(BaseAction):
    @with_retry(max_attempts=3, base_delay=1, max_delay=60)
    async def execute(self, action_file):
        # SendGrid API call
        response = self.client.send(message)
        return response
```

---

## Error Categories & Handlers

### Category 1: Transient Errors (Retry with Backoff)

**Examples:**
- Network timeout
- DNS resolution failure
- API rate limit (429)
- Temporary service unavailable (503)

**Handler:**
```python
@with_retry(max_attempts=3, base_delay=1, max_delay=60)
async def call_external_api():
    try:
        response = await client.request(...)
        return response
    except TimeoutError as e:
        # Will be retried automatically
        raise
    except RateLimitError as e:
        # Check Retry-After header
        retry_after = e.headers.get('Retry-After', '60')
        logger.warning("Rate limited, retrying after %ss", retry_after)
        time.sleep(int(retry_after))
        raise
```

### Category 2: Authentication Errors (Never Retry)

**Examples:**
- Expired OAuth token (401)
- Invalid API key (403)
- Permission denied (403)

**Handler:**
```python
try:
    response = client.request(...)
except AuthError as e:
    logger.error("Authentication failed: %s", e, exc_info=True)
    
    # Write ALERT file
    alert_path = vault_path / "Needs_Action" / f"ALERT_auth_{service}.md"
    alert_content = f"""---
type: alert
severity: critical
created: {datetime.utcnow().isoformat()}Z
service: {service}
---

## Authentication Error
{str(e)}

## Required Action
1. Check credentials in .env
2. Refresh OAuth token
3. Verify API key is valid
4. Restart {service}_watcher process
"""
    alert_path.write_text(alert_content)
    
    # NEVER retry auth errors
    raise
```

### Category 3: Logic Errors (Human Review)

**Examples:**
- Qwen misinterprets task
- Wrong action type selected
- Missing business logic

**Handler:**
```python
try:
    # Process task
    result = await qwen.process(action_file)
    
    if result.get('confidence', 0) < 0.8:
        # Low confidence → move to Rejected/
        rejected_path = vault_path / "Rejected" / action_file.name
        action_file.rename(rejected_path)
        
        # Add review note
        review_note = rejected_path.with_suffix('.review.md')
        review_note.write_text(f"""
## Review Required
Qwen confidence: {result['confidence']}
Reason: {result.get('reason', 'Unclear task')}

## To Approve: Move back to Approved/
## To Reject: Delete or move to Done/ with note
""")
        
except LogicError as e:
    logger.error("Logic error: %s", e, exc_info=True)
```

### Category 4: Data Errors (Quarantine)

**Examples:**
- Corrupted markdown file
- Missing required frontmatter field
- Invalid YAML syntax

**Handler:**
```python
import yaml

def parse_frontmatter(filepath):
    try:
        content = filepath.read_text()
        parts = content.split('---', 2)
        frontmatter = yaml.safe_load(parts[1])
        return frontmatter
    except yaml.YAMLError as e:
        logger.error("Invalid YAML in %s: %s", filepath, e, exc_info=True)
        
        # Quarantine file
        quarantine_path = vault_path / "Rejected" / f"INVALID_{filepath.name}"
        filepath.rename(quarantine_path)
        
        # Log error
        logger.error("Quarantined invalid file: %s", quarantine_path)
        return None
    except IndexError:
        logger.error("Missing frontmatter in %s", filepath)
        return None
```

### Category 5: System Errors (Watchdog Restart)

**Examples:**
- Process crash
- Out of memory
- Disk full
- Unhandled exception

**Handler:**
```python
# In watchdog_monitor.py
class ProcessMonitor:
    def check_processes(self):
        result = subprocess.run(['pm2', 'list', '--json'], capture_output=True)
        processes = json.loads(result.stdout)
        
        for proc in processes:
            if proc['pm2_env']['status'] == 'errored':
                logger.error("Process %s errored, restarting...", proc['name'])
                
                # Restart process
                subprocess.run(['pm2', 'restart', proc['name']])
                
                # Write ALERT file
                alert_path = vault_path / "Needs_Action" / f"ALERT_{proc['name']}_restarted.md"
                alert_path.write_text(f"""
## Process Restarted
Process: {proc['name']}
Status: errored → restarted
Time: {datetime.utcnow().isoformat()}Z

## Check Logs
pm2 logs {proc['name']}
""")
```

---

## Logging Configuration

### Entry Point (Once Per Process)

```python
# In __main__.py or entry script
import logging
from pathlib import Path

# Ensure logs directory exists
logs_dir = Path("AI_Employee_Vault/Logs")
logs_dir.mkdir(parents=True, exist_ok=True)

# Configure root logger
logging.basicConfig(
    level=logging.DEBUG,  # Flip to INFO before production
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler(logs_dir / "app.log"),  # File output
    ],
)

# Suppress noisy libraries
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("googleapiclient").setLevel(logging.WARNING)
```

### Every Other File (Two Lines Only)

```python
# Top of file (after imports)
import logging
logger = logging.getLogger(__name__)
```

### Every Except Block (Required Pattern)

```python
try:
    # Risky operation
    result = external_call()
except SpecificError as e:
    logger.error("Attempted: %s | Error: %s", context, e, exc_info=True)
    # Handle error
```

---

## Debugging Workflow

### Step 1: Check Logs

```bash
# View all logs
pm2 logs

# View specific process logs
pm2 logs gmail_watcher

# View last 100 lines
tail -100 AI_Employee_Vault/Logs/app.log

# Follow logs in real-time
tail -f AI_Employee_Vault/Logs/app.log
```

### Step 2: Check Process Status

```bash
# List all processes
pm2 list

# View detailed info
pm2 show gmail_watcher

# Check memory usage
pm2 list --sort=memory
```

### Step 3: Reproduce in Dev Mode

```bash
# Stop PM2 process
pm2 stop gmail_watcher

# Run manually with debug output
python src/watchers/gmail_watcher.py

# Enable verbose logging
export LOG_LEVEL=DEBUG
python src/watchers/gmail_watcher.py
```

### Step 4: Check Error Category

```python
# Identify error type
if "timeout" in str(e).lower():
    # Transient - retry
elif "auth" in str(e).lower() or "401" in str(e) or "403" in str(e):
    # Auth - never retry, alert human
elif "yaml" in str(e).lower() or "parse" in str(e).lower():
    # Data - quarantine
else:
    # Unknown - log full traceback, alert human
```

### Step 5: Apply Fix

```python
# Add retry decorator
@with_retry(max_attempts=3, base_delay=1, max_delay=60)
async def failing_function():
    pass

# Or add error handling
try:
    result = risky_operation()
except SpecificError as e:
    logger.error("Operation failed: %s", e, exc_info=True)
    # Handle gracefully
```

---

## PM2 Configuration

### ecosystem.config.js

```javascript
module.exports = {
  apps: [
    {
      name: "orchestrator",
      script: "python",
      args: "src/orchestrator.py",
      cwd: "/abs/path/to/project",
      env: { PYTHONPATH: "./src" },
      error_file: "AI_Employee_Vault/Logs/pm2/orchestrator.err.log",
      out_file: "AI_Employee_Vault/Logs/pm2/orchestrator.out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      restart_delay: 5000,
      max_restarts: 10,
      watch: false,
      merge_logs: true,
    },
    {
      name: "gmail_watcher",
      script: "python",
      args: "src/watchers/gmail_watcher.py",
      cwd: "/abs/path/to/project",
      env: { PYTHONPATH: "./src" },
      error_file: "AI_Employee_Vault/Logs/pm2/gmail_watcher.err.log",
      out_file: "AI_Employee_Vault/Logs/pm2/gmail_watcher.out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      restart_delay: 5000,
      max_restarts: 10,
    },
    // ... other processes
  ]
};
```

### PM2 Commands

```bash
# Start all
pm2 start ecosystem.config.js

# Restart all
pm2 restart all

# Restart specific
pm2 restart gmail_watcher

# View logs
pm2 logs

# Save process list
pm2 save

# Setup startup
pm2 startup
pm2 save
```

---

## ALERT File Templates

### Auth Error Alert

```markdown
---
type: alert
severity: critical
created: 2026-01-07T10:30:00Z
service: GmailWatcher
---

## Authentication Error
Gmail API returned 401 Unauthorized

## Error Details
google.auth.exceptions.RefreshError: The credentials did not match any expected credentials

## Required Action
1. Check GMAIL_CREDENTIALS in .env
2. Verify credentials.json is valid
3. Refresh OAuth token if expired
4. Restart gmail_watcher: `pm2 restart gmail_watcher`

## Logs
pm2 logs gmail_watcher
```

### Rate Limit Alert

```markdown
---
type: alert
severity: warning
created: 2026-01-07T10:30:00Z
service: EmailAction
---

## Rate Limit Exceeded
EmailAction hit rate limit: 10 emails/hour

## Details
- Last email sent: 2026-01-07T10:29:00Z
- Rate limit resets: 2026-01-07T11:00:00Z
- Emails sent this hour: 10/10

## Auto-Recovery
System will resume sending at 11:00:00Z

## To Override
Reduce rate limit in src/actions/rate_limiter.py
```

### Process Crash Alert

```markdown
---
type: alert
severity: critical
created: 2026-01-07T10:30:00Z
service: WhatsAppWatcher
---

## Process Crashed
WhatsAppWatcher process crashed and was restarted by watchdog

## Error
playwright._impl._api_types.TimeoutError: Timeout 30000ms exceeded

## Restart Info
- Restarted at: 2026-01-07T10:30:15Z
- Restart count: 3/10 (max_restarts)
- Status: running

## Check Logs
pm2 logs whatsapp_watcher

## If Persists
1. Check WhatsApp session: ls -la whatsapp_session/
2. Re-scan QR code if needed
3. Consider increasing timeout
```

---

## Reference Files

- [Retry Handler](../../src/actions/retry_handler.py)
- [Audit Logger](../../src/actions/audit_logger.py)
- [Config Class](../../src/config.py)
- [PM2 Config](../../ecosystem.config.js)
- [BaseWatcher](../../src/watchers/base_watcher.py)
- [BaseAction](../../src/actions/base_action.py)

---

## Examples

### Example 1: Gmail API Rate Limit

**Problem:** Gmail API returns 429 Too Many Requests

**Solution:**
```python
from retry_handler import with_retry

class GmailWatcher(BaseWatcher):
    @with_retry(max_attempts=3, base_delay=1, max_delay=300)
    async def check_for_updates(self):
        try:
            response = self.client.users().messages().list(...).execute()
            return response
        except HttpError as e:
            if e.resp.status == 429:
                retry_after = int(e.headers.get('Retry-After', '60'))
                logger.warning("Gmail rate limit, waiting %ds", retry_after)
                time.sleep(retry_after)
                raise  # Retry decorator will handle
            raise
```

### Example 2: WhatsApp Browser Crash

**Problem:** Playwright browser crashes unexpectedly

**Solution:**
```python
class WhatsAppWatcher(BaseWatcher):
    async def check_for_updates(self):
        try:
            browser = await self.browser_context.browser()
            page = await browser.new_page()
            # ... use page
        except Exception as e:
            logger.error("Browser error: %s", e, exc_info=True)
            
            # Relaunch browser
            await self._relaunch_browser()
            
            # Write ALERT file
            self._write_alert("WhatsApp browser crashed and restarted")
            
            return []  # Continue on error
```

### Example 3: Vault File Corruption

**Problem:** Invalid YAML in action file

**Solution:**
```python
def parse_frontmatter(filepath):
    try:
        content = filepath.read_text()
        parts = content.split('---', 2)
        frontmatter = yaml.safe_load(parts[1])
        
        # Validate required fields
        required = ['type', 'from', 'subject', 'received']
        for field in required:
            if field not in frontmatter:
                raise ValueError(f"Missing required field: {field}")
        
        return frontmatter
        
    except yaml.YAMLError as e:
        logger.error("Invalid YAML in %s: %s", filepath, e, exc_info=True)
        quarantine_file(filepath)
        return None
    except ValueError as e:
        logger.error("Invalid frontmatter in %s: %s", filepath, e, exc_info=True)
        quarantine_file(filepath)
        return None

def quarantine_file(filepath):
    """Move invalid file to Rejected/ with INVALID_ prefix."""
    rejected_dir = vault_path / "Rejected"
    rejected_dir.mkdir(parents=True, exist_ok=True)
    
    new_path = rejected_dir / f"INVALID_{filepath.name}"
    filepath.rename(new_path)
    
    logger.info("Quarantined invalid file: %s", new_path)
```

---

## Anti-Patterns (Avoid These)

❌ **Silent failures** - `except: pass` is FORBIDDEN
❌ **No traceback** - Always use `exc_info=True`
❌ **Auto-retrying auth errors** - NEVER retry 401/403
❌ **Auto-retrying payments** - Always require fresh approval
❌ **Logging credentials** - Never log tokens, passwords, PII
❌ **Infinite retry loops** - Always cap at max_attempts
❌ **No DRY_RUN check** - Always guard destructive operations
❌ **Ignoring rate limits** - Respect Retry-After headers

---

## Success Metrics

✅ All errors logged with full traceback
✅ Transient errors retried with backoff
✅ Auth errors alert human (never retry)
✅ Invalid files quarantined
✅ Crashed processes auto-restarted
✅ DRY_RUN mode prevents real actions
✅ Rate limits respected
✅ ALERT files created for critical errors

---

**Created from:** AI Employee Hackathon - Error Recovery Patterns
**Reference:** QWEN.md Section 8 (Error Recovery), SPEC.md
