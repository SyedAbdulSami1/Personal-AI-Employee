# QWEN.md — Project Rules
# D:\D Data\Personal AI Employee Hackathon\QWEN.md
# This file OVERRIDES C:\Users\pc\.qwen\QWEN.md
# Project: Personal AI Employee — Digital FTE (Panaversity Hackathon)
# Target: Silver Tier (20-30 hrs). Rules scale to Gold/Platinum.

---

## 0. READ FIRST — every session

```
1. CONSTITUTION.md exists?  → Read before anything else.
2. SPEC.md exists?          → Read before writing any code.
3. PLAN.md / TASKS.md?      → Check [ ] pending vs [x] done tasks.
4. File you're about to edit → Read it first. Never overwrite blindly.
5. New component needed?    → Check if BaseWatcher/BaseAction already covers it.
```

---

## 1. PROJECT IDENTITY

```
Name    : Personal AI Employee — Digital FTE
Brain   : Qwen (Qwen-Max / Qwen-Coder-2.5 — sole reasoning engine)
Memory  : AI_Employee_Vault/ (local Obsidian markdown — single source of truth)
Senses  : Python Watcher scripts (Gmail, WhatsApp, filesystem)
Hands   : MCP servers (email-mcp, browser-mcp, filesystem-mcp built-in)
Loop    : Ralph Wiggum stop-hook → .qwen/hooks/stop.py (max 10 iterations)
Process : orchestrator.py (master) + watchdog_monitor.py (health)
```

---

## 2. CANONICAL FOLDER STRUCTURE — never deviate

```
project-root/
│
├── AI_Employee_Vault/            ← Obsidian vault. ONLY .md files here.
│   ├── Inbox/                    ← user manually drops files
│   ├── Needs_Action/             ← watchers WRITE here; orchestrator READS here
│   ├── In_Progress/qwen/         ← claim-by-move rule (no double-work)
│   ├── Plans/                    ← Qwen writes PLAN_<task>.md
│   ├── Pending_Approval/         ← Qwen writes approval requests; user reviews
│   ├── Approved/                 ← user moves here = approved → triggers MCP
│   ├── Rejected/                 ← user moves here = rejected; Qwen logs+stops
│   ├── Done/                     ← completed tasks; Ralph Wiggum checks this
│   ├── Logs/pm2/                 ← JSON audit logs + PM2 sub-logs
│   ├── Briefings/                ← Monday CEO briefings land here
│   ├── Accounting/               ← Finance watcher writes Current_Month.md
│   ├── Dashboard.md              ← live status; Qwen updates after every task
│   ├── Company_Handbook.md       ← 10 rules of engagement; Qwen reads before acting
│   └── Business_Goals.md         ← Q1 targets, KPIs, subscription rules
│
├── src/
│   ├── config.py                 ← Config dataclass. ONE instance. Passed everywhere.
│   ├── watchers/
│   │   ├── base_watcher.py       ← BaseWatcher(ABC). All watchers extend this.
│   │   ├── gmail_watcher.py      ← GmailWatcher(BaseWatcher). interval=120s.
│   │   ├── whatsapp_watcher.py   ← WhatsAppWatcher(BaseWatcher). interval=30s.
│   │   └── filesystem_watcher.py ← DropFolderHandler(FileSystemEventHandler)
│   ├── actions/
│   │   ├── audit_logger.py       ← AuditLogger. ONE instance. Imported everywhere.
│   │   ├── retry_handler.py      ← @with_retry decorator. ALL external calls use this.
│   │   ├── rate_limiter.py       ← RateLimiter. ONE instance per process.
│   │   └── linkedin_poster.py    ← LinkedInPoster(BaseAction)
│   ├── orchestrator.py           ← Orchestrator class. Master process.
│   ├── watchdog_monitor.py       ← ProcessMonitor class. Restarts dead watchers.
│   └── briefing_generator.py     ← BriefingGenerator. Runs Sunday 11PM.
│
├── .qwen/
│   ├── hooks/stop.py             ← Ralph Wiggum. Blocks exit until Done/ has task.
│   ├── mcp.json                  ← MCP server config
│   ├── model_config.yaml         ← Qwen model settings (max_tokens, temperature, etc.)
│   └── skills/                   ← Agent Skills (SKILL.md files)
│
├── .env                          ← secrets only. In .gitignore. Never committed.
├── .gitignore                    ← FIRST file created. Always.
├── ecosystem.config.js           ← PM2 config: 4 apps
├── pyproject.toml                ← UV project
└── QWEN.md                       ← this file
```

**Hard violations — each wastes tokens in next session:**
```
✗ Watcher logic outside src/watchers/
✗ Action/API logic outside src/actions/
✗ Vault content (.md files) outside AI_Employee_Vault/
✗ Second Config object anywhere — import and pass the one from src/config.py
✗ Second AuditLogger anywhere — import from src/actions/audit_logger.py
✗ Secrets in any .md, any .py, any tracked file
✗ os.getenv() scattered across files — Config reads .env once, passes values
```

---

## 3. OOP HIERARCHY — extend, never copy-paste

```
BaseWatcher(ABC)
  ├── GmailWatcher(BaseWatcher)        interval=120s, query="is:unread is:important"
  ├── WhatsAppWatcher(BaseWatcher)     interval=30s,  keywords list
  └── DropFolderHandler(FSEventHandler) watchdog, monitors Inbox/

BaseAction(ABC)
  └── LinkedInPoster(BaseAction)
  └── EmailAction(BaseAction)          add when needed

Config(dataclass)     ONE instance, entry point only, passed as param everywhere
AuditLogger           ONE instance per process, imported everywhere
RateLimiter           ONE instance per process, shared via Config or DI
```

**New watcher needed?** → extend BaseWatcher, override `check_for_updates()` and `create_action_file()`. Done. No copy of `run()` loop.
**New action needed?** → extend BaseAction, override `execute()`. DRY_RUN guard already in base.

---

## 3b. WATCHER SPECIFICATIONS

### WATCHER-001 GmailWatcher
```python
# src/watchers/gmail_watcher.py
class GmailWatcher(BaseWatcher):
    interval: 120 seconds
    Gmail API query: "is:unread is:important"
    Auth: OAuth2 via credentials.json (path from GMAIL_CREDENTIALS env)
    Output: Needs_Action/EMAIL_<message_id>.md using Schema A
    Dedup: in-memory processed_ids set (cleared on restart)
    DRY_RUN: logs "[DRY RUN] Would create EMAIL_<id>.md" — no file written
    Error handling: 
      - catch google.auth.exceptions.TransportError → retry with backoff
      - catch googleapiclient.errors.HttpError → log + alert human
    Console output: 
      - [GmailWatcher] Starting...
      - [GmailWatcher] Found N new emails
      - [GmailWatcher] Created EMAIL_<id>.md
      - [ERROR] <full message>
```

### WATCHER-002 WhatsAppWatcher
```python
# src/watchers/whatsapp_watcher.py
class WhatsAppWatcher(BaseWatcher):
    interval: 30 seconds
    Method: Playwright persistent context, headless=True after first QR scan
    Session path: from WHATSAPP_SESSION_PATH env var
    Keywords: ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing']
    Output: Needs_Action/WHATSAPP_<contact>_<timestamp>.md using Schema A
    First run: headless=False → user scans QR code → session saved → headless
    DRY_RUN: logs "[DRY RUN] Would create WHATSAPP_*.md" — no file written
    Error handling:
      - catch playwright TimeoutError → log + wait 60s before retry
      - catch browser crash → relaunch browser, log [ERROR] with traceback
    Console output:
      - [WhatsAppWatcher] Starting...
      - [WhatsAppWatcher] Found N urgent
      - [ERROR] Browser crashed: <traceback>
```

### WATCHER-003 FilesystemWatcher
```python
# src/watchers/filesystem_watcher.py
class DropFolderHandler(FileSystemEventHandler):
    Monitors: AI_Employee_Vault/Inbox/
    File types: .pdf, .docx, .csv, .txt, .md only (others silently ignored)
    On new file: copy to Needs_Action/ + create sidecar .md with Schema A frontmatter
    DRY_RUN: logs "[DRY RUN] Would copy <file> to Needs_Action/" — no copy
    Error handling:
      - catch PermissionError → log [ERROR] cannot read file
      - catch shutil.Error → log + alert human via ALERT_*.md
    Console output:
      - [FilesystemWatcher] Watching Inbox/
      - [FilesystemWatcher] New file: <filename>
```

---

## 4. CODING RULES — project-specific

### DRY checklist — ask before writing any function:
```
□ Config already has this setting?      → config.field, not os.getenv()
□ AuditLogger covers this log?          → audit.log_action(), not new logging setup
□ @with_retry covers this retry?        → apply decorator, not inline retry loop
□ BaseWatcher covers this watcher?      → subclass, not copy of run() loop
□ RateLimiter covers this limit?        → rate_limiter.check_and_increment()
□ This logic already exists somewhere?  → find it, import it, don't rewrite
```

### Logging — configured ONCE, used everywhere:
```python
# Entry point only (orchestrator.py, each watcher's __main__):
logging.basicConfig(
    level=logging.DEBUG,   # flip to INFO before production
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("AI_Employee_Vault/Logs/app.log"),
    ],
)

# Every other file — exactly these two lines at top:
import logging
logger = logging.getLogger(__name__)

# Every except block — exactly this pattern:
except SomeSpecificError as e:
    logger.error("Attempted: %s | Error: %s", context, e, exc_info=True)
    # exc_info=True → full traceback in console AND in app.log

# FORBIDDEN in this entire codebase:
except Exception: pass              # hides bugs
except Exception as e: print(e)    # no traceback, no file log
```

### DRY_RUN — top of every external action method:
```python
if self.dry_run:   # from self.config.dry_run — NEVER re-read os.getenv() here
    logger.info("[DRY RUN] %s would: %s", self.__class__.__name__, action_desc)
    return None
# real execution below
```
`.env` default: `DRY_RUN=true`. Set `false` only after manual end-to-end test passes.

### HITL — write to Pending_Approval/ and STOP for:
```
Any payment (any amount, any recipient)
Email/WhatsApp to new (unknown) contact
Social media DM, reply, or new post
Any file deletion
Bulk sends (>1 recipient)
Any action where Company_Handbook.md has no explicit rule
```

### Ralph Wiggum stop-hook (.qwen/hooks/stop.py):
```
Exit allowed : task file exists in Done/
Exit blocked : counter < 10 → increment, re-inject prompt, sys.exit(1)
Max reached  : counter == 10 → write ALERT_ralph_max_<task>.md → sys.exit(0)
Counter var  : RALPH_COUNTER env var (reset to "0" between tasks)
```

---

## 5. VAULT FILE SCHEMAS — always use YAML frontmatter

### SCHEMA A — Needs_Action file (Watchers write this):
```yaml
---
type: email | whatsapp | file_drop
from: <sender name or number>
subject: <subject line or message preview, max 100 chars>
received: <ISO 8601 timestamp, e.g. 2026-01-07T10:30:00Z>
priority: high | medium | low
status: pending
watcher: GmailWatcher | WhatsAppWatcher | FilesystemWatcher
---
## Content
<message body or file description>
## Suggested Actions
- [ ] <action 1>
- [ ] <action 2>
```

### SCHEMA B — Plan file (/Plans/PLAN_<taskname>.md, created by Qwen):
```yaml
---
created: <ISO 8601>
task_ref: <filename from Needs_Action that triggered this>
status: pending_approval | in_progress | complete | failed
iterations: <Ralph Wiggum counter, starts at 0>
---
## Objective
<one sentence>
## Steps
- [ ] Step 1
- [ ] Step 2
## Approval Required
yes | no — <reason if yes>
## Completion Condition
<what must be true for task to move to /Done/>
```

### SCHEMA C — Approval request (/Pending_Approval/<TYPE>_<task>.md):
```yaml
---
type: approval_request
action: send_email | payment | social_post | file_delete | whatsapp_send
amount: <dollar amount, only for payments>
recipient: <email, phone, or platform handle>
reason: <one sentence why this action is needed>
created: <ISO 8601>
expires: <ISO 8601, exactly 24 hours after created>
status: pending
plan_ref: <Plan filename that generated this request>
---
## Action Details
<full details of what will happen if approved>
## To APPROVE: Move this file to /Approved/
## To REJECT:  Move this file to /Rejected/
```

### SCHEMA D — Audit log entry (/Logs/YYYY-MM-DD.json, one JSON line per action):
```json
{"timestamp":"ISO 8601","action_type":"email_send|payment|social_post|file_move|watcher_start|error",
 "actor":"qwen_agent | gmail_watcher | whatsapp_watcher | human",
 "target":"<recipient, file path, or platform>","parameters":{},"approval_status":"human_approved",
 "approved_by":"human | system | none","result":"success | failure | dry_run | skipped",
 "error":"<full error message + traceback if result=failure, else null>","dry_run":false}
```
Retention: 90 days. AuditLogger.__init__ deletes older files automatically.

---

## 5b. VAULT TEMPLATES — create these on project init

### Business_Goals.md Template:
```markdown
# /Vault/Business_Goals.md
---
last_updated: 2026-01-07
review_frequency: weekly
---

## Q1 2026 Objectives

### Revenue Target
- Monthly goal: $10,000
- Current MTD: $4,500

### Key Metrics to Track
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Client response time | < 24 hours | > 48 hours |
| Invoice payment rate | > 90% | < 80% |
| Software costs | < $500/month | > $600/month |

### Active Projects
1. Project Alpha - Due Jan 15 - Budget $2,000
2. Project Beta - Due Jan 30 - Budget $3,500

### Subscription Audit Rules
Flag for review if:
- No login in 30 days
- Cost increased > 20%
- Duplicate functionality with another tool
```

### Dashboard.md Template:
```markdown
# AI Employee Dashboard
---
last_updated: <ISO 8601>
status: operational | degraded | stopped
---

## System Status
- **Watchers**: Gmail ✅ | WhatsApp ✅ | Filesystem ✅
- **Pending Actions**: <count>
- **Today's Completed**: <count>

## Revenue Tracking
- **This Week**: $X
- **MTD**: $Y (Z% of target)
- **Trend**: On track / Behind / Ahead

## Recent Activity
- [timestamp] <activity 1>
- [timestamp] <activity 2>

## Bottlenecks
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
| <task> | <time> | <time> | <delay> |

## Upcoming Deadlines
- <deadline 1>
- <deadline 2>
```

### Company_Handbook.md Template:
```markdown
# Company Handbook — Rules of Engagement
---
version: 1.0
effective_date: 2026-01-07
---

## Core Principles
1. Always be polite and professional in all communications
2. Never send payments without human approval
3. Flag any payment over $500 for manual review
4. Respond to client inquiries within 24 hours
5. Log every action taken
6. When in doubt, ask for approval
7. Never delete files without explicit permission
8. Escalate errors immediately via ALERT_*.md files
9. Respect rate limits: max 10 emails/hr, max 3 payments/hr
10. DRY_RUN=true until explicitly set to false

## Communication Guidelines
- Email tone: Professional, concise, helpful
- WhatsApp tone: Friendly, brief, responsive
- Social media: Positive, value-driven, on-brand

## Approval Thresholds
| Action | Auto | Require Approval |
|--------|------|------------------|
| Email replies | Known contacts | New contacts, bulk sends |
| Payments | < $50 recurring | All new payees, > $100 |
| Social media | Scheduled posts | Replies, DMs, new posts |
| File operations | Create, read | Delete, move outside vault |
```

---

## 6. SECURITY

### .gitignore FIRST — must include:
```
.env  credentials.json  whatsapp_session/  __pycache__/  *.pyc  Logs/*.json
```

### .env template (fill values, never commit):
```bash
# .env — NEVER commit. Add to .gitignore immediately.
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_CREDENTIALS=/absolute/path/to/credentials.json
BANK_API_TOKEN=
WHATSAPP_SESSION_PATH=/absolute/path/to/whatsapp_session
QWEN_API_KEY=
QWEN_BASE_URL=
DRY_RUN=true
DEV_MODE=true
VAULT_PATH=./AI_Employee_Vault
```

### Rate Limits — enforce in code:
```python
MAX_EMAILS_PER_HOUR = 10
MAX_PAYMENTS_PER_HOUR = 3
MAX_SOCIAL_POSTS_PER_DAY = 5
```

### Permission Boundaries:
| Action Category | Auto-Approve Threshold | Always Require Approval |
| :---- | :---- | :---- |
| Email replies | To known contacts | New contacts, bulk sends |
| Payments | < $50 recurring | All new payees, > $100 |
| Social media | Scheduled posts | Replies, DMs, new posts |
| File operations | Create, read | Delete, move outside vault |

### Credentials Management:
```
Credentials path: OUTSIDE vault. Absolute path. Rotated monthly.
Use environment variables for API keys
For banking credentials, use OS keychain (macOS Keychain, Windows Credential Manager)
Rotate credentials monthly and after any suspected breach
```

### Logging Security:
```
Logging: never log token, password, or PII — even at DEBUG level.
Vault sync (Platinum tier): markdown/state only. .env and sessions NEVER sync.
```

### Sandboxing & Isolation:
```
DEV_MODE flag: Prevents any real external actions during development
DRY_RUN flag: All action scripts support --dry-run that logs intended actions without executing
Separate Accounts: Use test/sandbox accounts for Gmail and banking during development
```

---

## 7. MCP CONFIG — .qwen/mcp.json

```json
{
  "servers": [
    { "name": "filesystem", "type": "builtin" },
    { "name": "email",
      "command": "node", "args": ["/abs/path/email-mcp/index.js"],
      "env": { "GMAIL_CREDENTIALS": "/abs/path/credentials.json" } },
    { "name": "browser",
      "command": "npx", "args": ["@anthropic/browser-mcp"],
      "env": { "HEADLESS": "true" } }
  ],
  "model": {
    "provider": "qwen",
    "model_name": "qwen-max",
    "temperature": 0.2,
    "max_tokens": 4096,
    "top_p": 0.95
  }
}
```

---

## 7b. PM2 CONFIG — ecosystem.config.js

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
      max_restarts: 10
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
      max_restarts: 10
    },
    {
      name: "whatsapp_watcher",
      script: "python",
      args: "src/watchers/whatsapp_watcher.py",
      cwd: "/abs/path/to/project",
      env: { PYTHONPATH: "./src" },
      error_file: "AI_Employee_Vault/Logs/pm2/whatsapp_watcher.err.log",
      out_file: "AI_Employee_Vault/Logs/pm2/whatsapp_watcher.out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      restart_delay: 5000,
      max_restarts: 10
    },
    {
      name: "watchdog",
      script: "python",
      args: "src/watchdog_monitor.py",
      cwd: "/abs/path/to/project",
      env: { PYTHONPATH: "./src" },
      error_file: "AI_Employee_Vault/Logs/pm2/watchdog.err.log",
      out_file: "AI_Employee_Vault/Logs/pm2/watchdog.out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      restart_delay: 5000,
      max_restarts: 10
    }
  ]
};
```

**PM2 Commands:**
```bash
pm2 start ecosystem.config.js          # Start all 4 processes
pm2 list                               # Check status
pm2 logs                               # View all logs
pm2 save                               # Persist process list
pm2 startup                            # Auto-start on system boot
pm2 restart all                        # Restart all processes
pm2 stop <name>                        # Stop specific process
```

---

## 8. ERROR RECOVERY

### Error Categories & Handlers:
| Category       | Examples                        | Handler                                      |
|----------------|---------------------------------|----------------------------------------------|
| Transient      | Network timeout, API rate limit | Exponential backoff: 1s, 2s, 4s (max 60s)   |
| Authentication | Expired token, 401/403          | Log ERROR, write ALERT_*.md, pause ops     |
| Logic          | Qwen misinterprets task         | Move to /Rejected/, write human review note  |
| Data           | Corrupted .md, missing field    | Quarantine file in /Rejected/, log + alert   |
| System         | Orchestrator crash, disk full   | watchdog_monitor.py restarts + writes ALERT_*.md     |

### Retry Decorator (@with_retry) — ALL external calls use this:
```python
# src/actions/retry_handler.py
import time
from functools import wraps
import logging
logger = logging.getLogger(__name__)

def with_retry(max_attempts=3, base_delay=1, max_delay=60):
    """Decorator for exponential backoff retry logic."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (TimeoutError, ConnectionError, RateLimitError) as e:
                    if attempt == max_attempts - 1:
                        logger.error("Max retries exceeded: %s", e, exc_info=True)
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning("Attempt %d failed, retrying in %ds: %s", attempt+1, delay, e)
                    time.sleep(delay)
        return wrapper
    return decorator

# Usage: @with_retry(max_attempts=3, base_delay=1, max_delay=60)
```

### Specific Error Handling:
```
Network / rate-limit  → @with_retry: 1s→2s→4s backoff, cap 60s
Auth 401/403          → log ERROR, write ALERT_auth_<svc>.md to Needs_Action/, pause
Bad vault file        → move to Rejected/, log ERROR, continue next task
Watcher crash         → watchdog_monitor.py restarts + writes ALERT_<n>_restarted.md
Gmail API down        → queue in Needs_Action/, process when restored
Banking timeout       → NEVER auto-retry. Fresh human approval every time.
Qwen unavailable      → watchers keep collecting; queue grows; process on restart
API rate limit        → exponential backoff + write ALERT_rate_limit.md if >3 retries
```

### Graceful Degradation:
```
Gmail API down        → Queue outgoing emails locally, process when restored
Banking API timeout   → Never retry payments automatically, always require fresh approval
Qwen unavailable      → Watchers continue collecting, queue grows for later processing
Obsidian vault locked → Write to temporary folder, sync when available
```

---

## 8b. CEO BRIEFING — Weekly Business Audit

**Trigger:** Every Sunday 11:00 PM (cron on Mac/Linux, Task Scheduler on Windows)

**Inputs:** 
- Business_Goals.md
- /Done/ files from current week
- Accounting/Current_Month.md
- Audit logs (Logs/YYYY-MM-DD.json)

**Output:** /Briefings/YYYY-MM-DD_Monday_Briefing.md

**Required Sections:**
```markdown
# /Vault/Briefings/2026-01-06_Monday_Briefing.md
---
generated: 2026-01-06T07:00:00Z
period: 2025-12-30 to 2026-01-05
---

# Monday Morning CEO Briefing

## Executive Summary
<2-3 sentences summarizing the week>

## Revenue
- **This Week**: $X
- **MTD**: $Y (Z% of $10,000 target)
- **Trend**: On track / Behind / Ahead

## Completed Tasks
- [x] Task 1
- [x] Task 2
- [x] Task 3

## Bottlenecks
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
| Client B proposal | 2 days | 5 days | +3 days |

## Proactive Suggestions

### Cost Optimization
- **Notion**: No team activity in 45 days. Cost: $15/month.
  - [ACTION] Cancel subscription? Move to /Pending_Approval

### Upcoming Deadlines
- Project Alpha final delivery: Jan 15 (9 days)
- Quarterly tax prep: Jan 31 (25 days)

---
*Generated by AI Employee v0.1 — Review at your convenience*
```

**Implementation:** `src/briefing_generator.py` — BriefingGenerator class, runs Sunday 11PM.

---

## 9. JUDGING WEIGHTS — keep in mind when prioritizing

```
Functionality  30% → end-to-end flow must work (detection → plan → approval → action → log)
Innovation     25% → creative integrations, clean agent design
Practicality   20% → daily usability, Monday CEO briefing quality
Security       15% → credential handling, HITL coverage, audit trail
Documentation  10% → README.md, setup commands, 5-10 min demo video
```

---

## 12. END-TO-END EXAMPLE FLOW

### Scenario: Client sends WhatsApp message asking for invoice

**Step 1: Detection (WhatsApp Watcher)**
```
Detected message:
  From: Client A
  Text: "Hey, can you send me the invoice for January?"

Watcher creates:
  /Vault/Needs_Action/WHATSAPP_client_a_2026-01-07.md
```

**Step 2: Reasoning (Qwen Code)**
```
Orchestrator triggers Qwen to process Needs_Action folder.

Qwen reads the file and creates:
  /Vault/Plans/PLAN_invoice_client_a.md

---
created: 2026-01-07T10:30:00Z
status: pending_approval
---

## Objective
Generate and send January invoice to Client A

## Steps
- [x] Identify client: Client A (client_a@email.com)
- [x] Calculate amount: $1,500 (from /Accounting/Rates.md)
- [ ] Generate invoice PDF
- [ ] Send via email (REQUIRES APPROVAL)
- [ ] Log transaction

## Approval Required
Email send requires human approval. See /Pending_Approval/
```

**Step 3: Approval (Human-in-the-Loop)**
```
Qwen creates approval request:
  /Vault/Pending_Approval/EMAIL_invoice_client_a.md

---
action: send_email
to: client_a@email.com
subject: January 2026 Invoice - $1,500
attachment: /Vault/Invoices/2026-01_Client_A.pdf
---

Ready to send. Move to /Approved to proceed.

User reviews and moves file to /Approved.
```

**Step 4: Action (Email MCP)**
```
Orchestrator detects approved file and calls Email MCP:

await email_mcp.send_email({
  to: 'client_a@email.com',
  subject: 'January 2026 Invoice - $1,500',
  body: 'Please find attached your invoice for January 2026.',
  attachment: '/Vault/Invoices/2026-01_Client_A.pdf'
});

Result logged to /Vault/Logs/2026-01-07.json
```

**Step 5: Completion**
```
Qwen updates Dashboard.md and moves files to Done/:

Dashboard.md updated:
  ## Recent Activity
  - [2026-01-07 10:45] Invoice sent to Client A ($1,500)

Files moved:
  /Needs_Action/WHATSAPP_... → /Done/
  /Plans/PLAN_invoice_... → /Done/
  /Approved/EMAIL_... → /Done/
```

---

## 13. TROUBLESHOOTING FAQ

### Setup Issues

**Q: Python command not found**

A: Ensure Python 3.13+ is installed and added to PATH. Run `python --version` to verify. Use `py` launcher on Windows if needed.

**Q: Vault isn't being read by Qwen**

A: Check that you're running from the vault directory or using correct VAULT_PATH. Verify file permissions allow read access.

**Q: Gmail API returns 403 Forbidden**

A: Your OAuth consent screen may need verification, or you haven't enabled Gmail API in Google Cloud Console. Check project settings.

**Q: WhatsApp session not persisting**

A: Ensure WHATSAPP_SESSION_PATH points to a writable directory. First run must complete QR scan in headful mode.

### Runtime Issues

**Q: Watcher scripts stop running overnight**

A: Use PM2 process manager (`pm2 start ecosystem.config.js`). Implements Watchdog pattern from Section 8.

**Q: Qwen is making incorrect decisions**

A: Review Company_Handbook.md rules. Add more specific examples. Lower autonomy thresholds so more actions require approval.

**Q: MCP server won't connect**

A: Check server process is running. Verify path in mcp.json is absolute. Check Qwen logs for connection errors.

**Q: Ralph Wiggum counter not incrementing**

A: Ensure .qwen/hooks/stop.py is properly configured. Check RALPH_COUNTER env var is being passed correctly.

### Security Concerns

**Q: How do I know my credentials are safe?**

A: Never commit .env files. Use environment variables. Regularly rotate credentials. Implement audit logging to track all access.

**Q: What if Qwen tries to pay the wrong person?**

A: That's why HITL is critical for payments. Any payment action creates approval file first. Never auto-approve payments to new recipients.

**Q: Audit logs growing too large**

A: AuditLogger.__init__ automatically deletes files older than 90 days. Verify retention policy is working correctly.

---

## 10. WHERE TO FIND DETAILS — on-demand only

```
Project principles     → CONSTITUTION.md
Full specifications    → SPEC.md  (schemas, watcher specs, MCP config)
Phase-by-phase plan    → PLAN.md  (exact commands + verify steps per phase)
Task checklist         → TASKS.md (100 tasks; mark [x] as completed)
Agent skills           → .qwen/skills/*.md  (read only when relevant)
Ralph Wiggum impl      → .qwen/hooks/stop.py
Teacher requirements   → teacher-requirement.md (source of truth for hackathon)
Qwen model config      → .qwen/model_config.yaml
```

---

## 11. QWEN-SPECIFIC PROTOCOLS

```
Model Selection:
  • Default: qwen-max (best reasoning for complex orchestration tasks)
  • Code generation: qwen-coder-2.5 (use for src/ files only)
  • Fast tasks: qwen-plus (balance speed/cost for simple lookups)
  • Local fallback: qwen-2.5-7b-instruct (via Ollama/vLLM if API unavailable)

Prompt Format:
  • Always include task context + Company_Handbook.md rules in every request
  • Use JSON mode for structured outputs (plans, approvals, logs)
  • System prompt: "You are an AI Employee agent. Follow HITL rules. Log everything."

Tool Calling:
  • Qwen supports native function calling — use for MCP interactions
  • Define tools in .qwen/tools.json following OpenAI-compatible schema
  • Always validate tool outputs before proceeding to next step

Context Management:
  • Max context: 32K tokens (qwen-max)
  • Use summarization for long vault files before passing to model
  • Cache frequent references (Company_Handbook.md, Business_Goals.md) in session

Rate Limits:
  • Track tokens/minute via RateLimiter in src/actions/rate_limiter.py
  • On 429: wait + retry with backoff, log ALERT_rate_limit.md if >3 retries

Output Style:
  • Code: markdown blocks with language tags
  • Patches: unified diff format where possible
  • Tone: Direct, technical, concise — no fluff
```

---

## 12. PERFORMANCE CHECK — before every output

```
□ Is this the shortest way to say it?
□ Am I repeating context already known from PROJECT_CONTEXT.md?
□ Is this code directly runnable / copy-paste ready?
□ Did I check SPEC.md before implementing logic?
→ If NO to any, reduce output and re-check.
```

---

## 13. LEARNING RESOURCES

### Prerequisites (Complete Before Hackathon)
| Topic | Resource | Time |
| :---- | :---- | :---- |
| Presentation | [Google Slides](https://docs.google.com/presentation/d/1UGvCUk1-O8m5i-aTWQNxzg8EXoKzPa8fgcwfNh8vRjQ/edit) | 2 hours |
| Claude Code Fundamentals | [Agent Factory](https://agentfactory.panaversity.org/docs/AI-Tool-Landscape/claude-code-features-and-workflows) | 3 hours |
| Obsidian Fundamentals | [help.obsidian.md](https://help.obsidian.md/Getting+started) | 30 min |
| Python File I/O | [Real Python](https://realpython.com/read-write-files-python) | 1 hour |
| MCP Introduction | [modelcontextprotocol.io](https://modelcontextprotocol.io/introduction) | 1 hour |
| Agent Skills | [Claude Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) | 2 hours |

### Core Learning (During Hackathon)
| Topic | Resource | Type |
| :---- | :---- | :---- |
| Claude + Obsidian | [YouTube](https://www.youtube.com/watch?v=sCIS05Qt79Y) | Video |
| Building MCP Servers | [MCP Quickstart](https://modelcontextprotocol.io/quickstart) | Tutorial |
| Claude Agent Teams | [YouTube](https://www.youtube.com/watch?v=0J2_YGuNrDo) | Video |
| Gmail API Setup | [Google Docs](https://developers.google.com/gmail/api/quickstart) | Docs |
| Playwright Automation | [Playwright Docs](https://playwright.dev/python/docs/intro) | Docs |

---

```
~340 lines. Updated to cover 100% of teacher-requirement.md + SPEC.md.
Global baseline: C:\Users\pc\.qwen\QWEN.md (this file overrides it)
Final Directive: Spec Compliance > Speed > Perfection | Less Context > More Context
Qwen Agent Ready — "Bismillah, let's build." 🚀
```
