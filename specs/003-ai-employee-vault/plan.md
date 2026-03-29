# Implementation Plan: AI Employee Vault System

**Branch**: `003-ai-employee-vault` | **Date**: 2026-03-29 | **Spec**: [spec.md](spec.md)
**Input**: Personal AI Employee — Silver Tier with Obsidian vault, Python Watchers, MCP servers, and HITL workflows

## Summary

Build a local-first autonomous AI employee that uses Claude Code as the reasoning engine, Obsidian vault for memory/dashboard, Python Watchers for perception (Gmail, WhatsApp, filesystem), MCP servers for actions (email, browser), and a human-in-the-loop approval workflow. The system operates 24/7 via PM2 process management with watchdog monitoring and generates weekly CEO briefings.

## Technical Context

**Language/Version**: Python 3.13 (UV package manager), Node.js v24+ (MCP servers)
**Primary Dependencies**: 
- Python: google-api-python-client, google-auth-httplib2, google-auth-oauthlib (Gmail), playwright (WhatsApp), watchdog (filesystem), pydantic (config)
- Node: @anthropic/browser-mcp, custom email-mcp
**Storage**: Obsidian vault (markdown files on local filesystem), JSON audit logs
**Testing**: pytest (unit/integration), Playwright test helpers
**Target Platform**: Windows 10/11 (primary), Mac/Linux (secondary via PM2)
**Project Type**: Single project with clear src/ separation (watchers/, actions/, orchestrator/)
**Performance Goals**: 
- Gmail polling: <120s latency from arrival to vault
- WhatsApp polling: <30s latency for urgent keywords
- File drop processing: <5s latency
- Claude planning: <1 iteration (no retries needed)
**Constraints**: 
- Gmail API quota: 1B units/day (10k emails/month safe)
- WhatsApp: session persistence required, QR scan on first run only
- Rate limits: 10 emails/hr, 3 payments/hr, 5 social posts/day
- DRY_RUN=true by default until manual override
**Scale/Scope**: 
- 10k emails/month, 1k WhatsApp messages/month
- 50-100 action files/day in Needs_Action/
- 90-day audit log retention
- 99% uptime during business hours (8AM-8PM)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**AI Employee Specific Gates:**
- ✅ Local-first architecture confirmed (Obsidian vault on local machine, no external data transmission except via MCP servers with user credentials)
- ✅ Human-in-the-loop workflows designed for >$50 payments, new contacts, bulk communications (>10 recipients), file deletions
- ✅ Audit logging strategy defined: JSON logs in Logs/YYYY-MM-DD.json, one line per action, 90-day retention
- ✅ Graceful degradation paths: Gmail down → queue locally; WhatsApp crash → auto-restart; disk full → ALERT + pause watchers
- ✅ Credential storage plan: .env file only (GMAIL_CREDENTIALS, WHATSAPP_SESSION_PATH, BANK_API_TOKEN), never in vault/code/logs
- ✅ Decision boundaries established: Auto-approve known contact replies, scheduled posts; Human approve payments >$50, new payees, bulk sends
- ✅ Ethical boundaries defined: No legal/medical advice, no emotional counseling, AI disclosure in all outbound communications

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-employee-vault/
├── plan.md              # This file
├── research.md          # Phase 0 output (below)
├── data-model.md        # Phase 1 output (below)
├── quickstart.md        # Phase 1 output (below)
├── contracts/           # Phase 1 output (OpenAPI schemas)
└── tasks.md             # Phase 2 output (separate /sp.tasks command)
```

### Source Code (repository root)

```text
src/
├── config.py            # Config dataclass, ONE instance, passed everywhere
├── watchers/
│   ├── base_watcher.py  # BaseWatcher(ABC) with run() loop, DRY_RUN guard
│   ├── gmail_watcher.py # GmailWatcher(BaseWatcher), 120s interval
│   ├── whatsapp_watcher.py # WhatsAppWatcher(BaseWatcher), 30s interval
│   └── filesystem_watcher.py # DropFolderHandler(FileSystemEventHandler)
├── actions/
│   ├── audit_logger.py  # AuditLogger, ONE instance, JSON logging
│   ├── retry_handler.py # @with_retry decorator, exponential backoff
│   ├── rate_limiter.py  # RateLimiter, token bucket per action type
│   └── linkedin_poster.py # LinkedInPoster(BaseAction)
├── orchestrator.py      # Orchestrator class, folder watching + Claude trigger
├── watchdog_monitor.py  # ProcessMonitor, health checks + auto-restart
└── briefing_generator.py # BriefingGenerator, Sunday 11PM trigger

AI_Employee_Vault/
├── Inbox/               # User drops files here
├── Needs_Action/        # Watchers write here
├── In_Progress/claude/  # Claim-by-move (no double-work)
├── Plans/               # PLAN_<task>.md files
├── Pending_Approval/    # Approval requests (Schema C)
├── Approved/            # User moves here → triggers MCP
├── Rejected/            # User moves here → Qwen logs+stops
├── Done/                # Completed tasks
├── Logs/
│   ├── app.log          # Consolidated app log
│   ├── pm2/             # PM2 sub-logs
│   └── YYYY-MM-DD.json  # Daily audit logs
├── Briefings/           # Monday_Briefing.md files
├── Accounting/          # Current_Month.md, Rates.md
├── Dashboard.md         # Live status
├── Company_Handbook.md  # 10 rules of engagement
└── Business_Goals.md    # Q1 targets, KPIs

.qwen/
├── hooks/stop.py        # Ralph Wiggum stop-hook
├── mcp.json             # MCP server config
└── model_config.yaml    # Qwen model settings

ecosystem.config.js      # PM2 config: 4 apps (orchestrator, gmail, whatsapp, watchdog)
pyproject.toml           # UV project file
.env                     # Secrets (NEVER commit)
.gitignore               # .env, __pycache__, node_modules, Logs/*.json
```

**Structure Decision**: Single project with src/ layout per QWEN.md conventions. All watcher logic in src/watchers/, all action logic in src/actions/, vault content exclusively in AI_Employee_Vault/. No frontend/backend split — this is a local-first agent system.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| 4 PM2 processes (orchestrator + 3 watchers) | Independent lifecycle management, auto-restart on crash | Single process would fail entirely if one watcher crashes |
| Ralph Wiggum loop with 10 retries | Prevents infinite loops while allowing transient error recovery | Simple retry without counter would hang forever on logic errors |
| Separate audit_logger.py with JSON schema | Required for hackathon judging (Security 15%, audit trail non-negotiable) | Plain text logs insufficient for structured querying, compliance |
| OOP hierarchy (BaseWatcher + subclasses) | DRY enforcement, consistent run() loop, DRY_RUN guard in one place | Copy-paste watcher code would violate DRY, waste tokens next session |

---

## Phase 0: Research & Decisions

*All NEEDS CLARIFICATION items resolved from spec.md. No unknowns remain.*

### Research Task 1: Gmail API OAuth2 Setup

**Decision**: Use `google-api-python-client` with OAuth2 2.0 flow, credentials stored in `credentials.json` outside vault

**Rationale**: 
- Official Google library, maintained and secure
- OAuth2 required by Gmail API (no API key-only access for read/write)
- credentials.json can be stored outside vault, referenced via GMAIL_CREDENTIALS env var
- Supports refresh tokens for long-running processes (no manual re-auth)

**Alternatives Considered**:
- Service account: Rejected — requires Google Workspace domain, not available for personal Gmail
- IMAP polling: Rejected — deprecated by Google, no support for labels/important filtering
- Third-party wrappers (e.g., GmailPy): Rejected — adds dependency layer, less control over OAuth flow

**Implementation Notes**:
- User must enable Gmail API in Google Cloud Console
- OAuth consent screen configured for "External" + testing mode
- Scopes: `https://www.googleapis.com/auth/gmail.readonly` (watcher), `https://www.googleapis.com/auth/gmail.send` (email-mcp)
- First run: browser opens for consent, refresh token saved to credentials.json
- Subsequent runs: silent refresh via refresh token

---

### Research Task 2: WhatsApp Web Automation via Playwright

**Decision**: Use Playwright with persistent browser context, session saved to WHATSAPP_SESSION_PATH

**Rationale**:
- WhatsApp Web has no official API for personal accounts
- Playwright supports persistent sessions (cookies/localStorage saved to disk)
- Headless mode after first QR scan enables 24/7 operation
- Keyword filtering in Python (not browser) minimizes resource usage

**Alternatives Considered**:
- WhatsApp Business API: Rejected — requires business verification, per-message pricing
- Selenium: Rejected — no built-in persistent context, harder session management
- whatsapp-web.js (Node.js library): Rejected — adds Node dependency for watcher, Python-only preferred

**Implementation Notes**:
- First run: `headless=False` → user scans QR → session saved
- Subsequent runs: `headless=True`, session loaded from WHATSAPP_SESSION_PATH
- Session path: absolute path outside vault (e.g., `C:\Users\pc\AppData\Local\whatsapp_session`)
- Browser: Chromium (default, most stable with WhatsApp Web)
- Polling: Every 30s, check for new messages containing keywords

---

### Research Task 3: Filesystem Watching with watchdog

**Decision**: Use `watchdog` library with `FileSystemEventHandler` subclass

**Rationale**:
- Native OS notifications (no polling, instant detection)
- Lightweight: <100 lines of code for full implementation
- Cross-platform: Windows ReadDirectoryChangesW, macOS FSEvents, Linux inotify
- Handles file copy, move, delete events

**Alternatives Considered**:
- Polling interval (e.g., os.listdir every 5s): Rejected — latency, CPU waste
- inotify (Linux-only): Rejected — not cross-platform
- Watchdog observers per directory: Rejected — single handler for Inbox/ sufficient

**Implementation Notes**:
- Observer runs in background thread
- Only `.pdf, .docx, .csv, .txt, .md` processed (others silently ignored)
- On new file: copy to Needs_Action/ + create sidecar .md with Schema A frontmatter
- DRY_RUN: log only, no copy

---

### Research Task 4: MCP Server Configuration for Claude Code

**Decision**: Use `.qwen/mcp.json` with builtin filesystem + custom email-mcp + browser-mcp

**Rationale**:
- Claude Code native integration (no custom API calls needed)
- Filesystem builtin: read/write vault files directly
- email-mcp: handles Gmail send/draft/search via Node.js server
- browser-mcp: Playwright for LinkedIn, payment portals (no custom browser code)

**Alternatives Considered**:
- Direct Gmail API calls in Python: Rejected — violates separation (watchers detect, MCP acts)
- Custom Python email server: Rejected — email-mcp already exists, maintained by Anthropic
- Puppeteer (Node): Rejected — browser-mcp wraps Playwright, consistent with WhatsApp watcher

**Implementation Notes**:
- email-mcp path: absolute path to `email-mcp/index.js` (user must clone/install separately)
- browser-mcp: `npx @anthropic/browser-mcp` (auto-installs on first run)
- HEADLESS=true for browser-mcp (except first WhatsApp QR scan)

---

### Research Task 5: PM2 Process Management on Windows

**Decision**: Use PM2 with `pm2 start ecosystem.config.js` + `pm2 startup`

**Rationale**:
- Cross-platform: Windows service + Mac/Linux systemd
- Auto-restart on crash (configurable max_restarts)
- Log rotation built-in (prevents disk fill)
- Single command to start all 4 processes

**Alternatives Considered**:
- Windows Task Scheduler: Rejected — no auto-restart, harder log management
- systemd (Linux-only): Rejected — not cross-platform
- Python subprocess + watchdog: Rejected — PM2 more mature, battle-tested

**Implementation Notes**:
- Install: `npm install -g pm2`
- ecosystem.config.js: 4 apps (orchestrator, gmail_watcher, whatsapp_watcher, watchdog)
- Logs: `AI_Employee_Vault/Logs/pm2/<app>.err.log` + `.out.log`
- Startup: `pm2 startup` → copies command → paste in admin terminal
- Monitor: `pm2 list`, `pm2 logs`, `pm2 restart <name>`

---

### Research Task 6: Rate Limiting Strategy

**Decision**: Token bucket algorithm in `src/actions/rate_limiter.py`

**Rationale**:
- Simple, predictable: N tokens per hour, one token per action
- Burst-safe: allows up to bucket_size actions in short burst, then enforces limit
- Stateful: tracks tokens in memory, resets on restart (safe for rate limits)

**Alternatives Considered**:
- Sliding window (e.g., Redis): Rejected — overkill, adds dependency
- Fixed window (e.g., count per hour): Rejected — boundary issues (59th vs 1st minute)
- Leaky bucket: Rejected — more complex, same outcome for this use case

**Implementation Notes**:
- MAX_EMAILS_PER_HOUR = 10, MAX_PAYMENTS_PER_HOUR = 3, MAX_SOCIAL_POSTS_PER_DAY = 5
- RateLimiter class: ONE instance per process, passed as parameter
- `check_and_increment(action_type)` → returns True if allowed, False if rate-limited
- On rate limit: log WARNING, queue action for retry in 60s

---

### Research Task 7: Exponential Backoff for Transient Errors

**Decision**: `@with_retry` decorator with 1s→2s→4s backoff, cap 60s

**Rationale**:
- DRY: apply decorator to any function, no inline retry loops
- Configurable: max_attempts, base_delay, max_delay per function
- Logs each retry attempt (visible in console + app.log)
- Re-raises on max attempts (caller can handle or let watchdog restart)

**Alternatives Considered**:
- tenacity library: Rejected — adds dependency, decorator is 20 lines
- Inline while loop: Rejected — violates DRY, copy-paste across watchers
- No retry (fail immediately): Rejected — transient errors common (network blips, rate limits)

**Implementation Notes**:
- Catches: `TimeoutError`, `ConnectionError`, `RateLimitError`
- Does NOT catch: `AuthError`, `ValueError` (logic errors, not transient)
- Usage: `@with_retry(max_attempts=3, base_delay=1, max_delay=60)`

---

### Research Task 8: Ralph Wiggum Stop-Hook Implementation

**Decision**: `.qwen/hooks/stop.py` fired by Claude Code hook system, increments RALPH_COUNTER env var

**Rationale**:
- Native Claude Code feature (hooks fire on exit)
- Prevents infinite loops (max 10 iterations)
- Escalates to human via ALERT_*.md when max reached
- Task file in Done/ = success, else retry or alert

**Alternatives Considered**:
- Orchestrator timeout (e.g., kill after 5min): Rejected — doesn't prevent logic loops
- No loop control: Rejected — Claude could retry forever on ambiguous tasks
- Human review every iteration: Rejected — defeats autonomy, too much friction

**Implementation Notes**:
- Env vars: TASK_FILE (absolute path), RALPH_COUNTER (default "0")
- Counter stored in .env or orchestrator memory (cleared on task change)
- On success: print `"[Ralph] Task complete ✅"`, sys.exit(0)
- On max: print `"[Ralph] Max iterations reached ⚠️"`, write ALERT, sys.exit(0)
- On retry: increment counter, sys.exit(1) (triggers re-run)

---

### Research Task 9: CEO Briefing Generation Strategy

**Decision**: `src/briefing_generator.py` triggered by cron (Mac/Linux) or Task Scheduler (Windows) Sunday 11PM

**Rationale**:
- Deterministic timing: every Sunday night, ready for Monday morning
- Inputs: Business_Goals.md (targets), /Done/ files (completed tasks), audit logs (revenue)
- Output: /Briefings/YYYY-MM-DD_Monday_Briefing.md with 6 required sections
- Claude reads brief, generates summary, fills template

**Alternatives Considered**:
- Real-time dashboard updates only: Rejected — CEO needs weekly summary, not just live status
- Manual briefing creation: Rejected — defeats automation purpose
- Daily briefings: Rejected — too frequent, weekly cadence matches business rhythm

**Implementation Notes**:
- Cron: `0 23 * * 0 cd /path && python src/briefing_generator.py`
- Task Scheduler: Sunday 11PM, trigger `python src/briefing_generator.py`
- BriefingGenerator class: reads /Done/ files filtered by date, parses audit logs for revenue
- Template: 6 sections (Executive Summary, Revenue, Completed Tasks, Bottlenecks, Proactive Suggestions, Footer)

---

**Phase 0 Complete**: All technical decisions documented. No NEEDS CLARIFICATION items remain.

---

## Phase 1: Design & Contracts

### Data Model

*Entities extracted from feature spec. All stored as markdown with YAML frontmatter.*

#### Entity 1: Needs_Action File

**Purpose**: Incoming work items from watchers (emails, WhatsApp messages, file drops)

**File Pattern**: `AI_Employee_Vault/Needs_Action/{TYPE}_{id}.md`

**Schema** (YAML frontmatter + markdown body):
```yaml
---
type: email | whatsapp | file_drop
from: <sender name or number>
subject: <subject line or message preview, max 100 chars>
received: <ISO 8601 timestamp>
priority: high | medium | low
status: pending | in_progress | completed | rejected
watcher: GmailWatcher | WhatsAppWatcher | FilesystemWatcher
---
## Content
<message body or file description>

## Suggested Actions
- [ ] <action 1>
- [ ] <action 2>
```

**Validation Rules**:
- `type` MUST be one of: email, whatsapp, file_drop
- `received` MUST be ISO 8601 format (e.g., `2026-01-07T10:30:00Z`)
- `priority` MUST be one of: high, medium, low
- `status` defaults to `pending`
- `watcher` MUST match the watcher that created the file

**State Transitions**:
```
pending → in_progress (when Claude starts processing)
in_progress → completed (when task moved to Done/)
pending → rejected (when user moves to Rejected/)
```

---

#### Entity 2: Plan File

**Purpose**: Task breakdown created by Claude for each Needs_Action item

**File Pattern**: `AI_Employee_Vault/Plans/PLAN_{taskname}.md`

**Schema**:
```yaml
---
created: <ISO 8601>
task_ref: <filename from Needs_Action that triggered this>
status: pending_approval | in_progress | complete | failed
iterations: <Ralph Wiggum counter, starts at 0>
---
## Objective
<objective sentence>

## Steps
- [ ] Step 1
- [ ] Step 2

## Approval Required
yes | no — <reason if yes>

## Completion Condition
<what must be true for task to move to /Done/>
```

**Validation Rules**:
- `task_ref` MUST reference an existing Needs_Action file
- `iterations` MUST be 0-10 (enforced by Ralph Wiggum)
- `Approval Required` MUST be `yes` or `no`

**Relationships**:
- One Plan per Needs_Action (1:1)
- Plan references task_ref (foreign key to Needs_Action filename)

---

#### Entity 3: Approval Request

**Purpose**: Human-in-the-loop approval for sensitive actions

**File Pattern**: `AI_Employee_Vault/Pending_Approval/{ACTION_TYPE}_{task}.md`

**Schema**:
```yaml
---
type: approval_request
action: send_email | payment | social_post | file_delete | whatsapp_send
amount: <dollar amount, only for payments>
recipient: <email, phone, or platform handle>
reason: <one sentence why this action is needed>
created: <ISO 8601>
expires: <ISO 8601, exactly 24 hours after created>
status: pending | approved | rejected | expired
plan_ref: <Plan filename that generated this request>
---
## Action Details
<full details of what will happen if approved>

## To APPROVE: Move this file to /Approved/
## To REJECT: Move this file to /Rejected/
```

**Validation Rules**:
- `expires` MUST be exactly 24 hours after `created`
- `action` MUST be one of: send_email, payment, social_post, file_delete, whatsapp_send
- `amount` REQUIRED if action=payment, OPTIONAL otherwise

**State Transitions**:
```
pending → approved (user moves to Approved/ → MCP executes)
pending → rejected (user moves to Rejected/ → Claude logs + stops)
pending → expired (24 hours elapsed → auto-rejected)
```

---

#### Entity 4: Audit Log Entry

**Purpose**: Immutable record of all system actions

**File Pattern**: `AI_Employee_Vault/Logs/YYYY-MM-DD.json` (one JSON line per entry)

**Schema** (JSON Lines format):
```json
{
  "timestamp": "ISO 8601",
  "action_type": "email_send|payment|social_post|file_move|watcher_start|error",
  "actor": "claude_code | gmail_watcher | whatsapp_watcher | human",
  "target": "<recipient, file path, or platform>",
  "parameters": { "<key>": "<value>" },
  "approval_status": "auto_approved | human_approved | pending | rejected | dry_run",
  "approved_by": "human | system | none",
  "result": "success | failure | dry_run | skipped",
  "error": "<full error message + traceback if result=failure, else null>",
  "dry_run": true | false
}
```

**Retention**: 90 days (AuditLogger.__init__ deletes older files automatically)

**Validation Rules**:
- `timestamp` MUST be ISO 8601
- `action_type` MUST be one of the defined types
- `result` MUST be one of: success, failure, dry_run, skipped

---

#### Entity 5: Dashboard

**Purpose**: Real-time system status, updated after every task

**File Pattern**: `AI_Employee_Vault/Dashboard.md`

**Schema**:
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

**Update Trigger**: After every task completion (file moved to Done/)

---

### API Contracts

*Extracted from functional requirements. MCP servers implement these contracts.*

#### Contract 1: Email MCP Server

**Operations**: send, draft, search

**send_email**:
```typescript
{
  command: "send_email",
  params: {
    to: string,
    subject: string,
    body: string,
    cc?: string[],
    bcc?: string[],
    attachment?: string  // absolute path to file
  },
  returns: {
    success: boolean,
    message_id: string,
    error?: string
  }
}
```

**draft_email**:
```typescript
{
  command: "draft_email",
  params: {
    to: string,
    subject: string,
    body: string,
    attachment?: string
  },
  returns: {
    success: boolean,
    draft_id: string,
    error?: string
  }
}
```

**search_emails**:
```typescript
{
  command: "search_emails",
  params: {
    query: string,  // Gmail search query
    max_results: number  // default 10
  },
  returns: {
    success: boolean,
    emails: Array<{
      id: string,
      subject: string,
      from: string,
      date: string,
      snippet: string
    }>,
    error?: string
  }
}
```

---

#### Contract 2: Browser MCP Server

**Operations**: navigate, click, fill, screenshot, evaluate

**navigate**:
```typescript
{
  command: "navigate",
  params: {
    url: string
  },
  returns: {
    success: boolean,
    title: string,
    error?: string
  }
}
```

**click**:
```typescript
{
  command: "click",
  params: {
    selector: string  // CSS selector
  },
  returns: {
    success: boolean,
    error?: string
  }
}
```

**fill**:
```typescript
{
  command: "fill",
  params: {
    selector: string,
    value: string
  },
  returns: {
    success: boolean,
    error?: string
  }
}
```

**screenshot**:
```typescript
{
  command: "screenshot",
  params: {
    full_page?: boolean  // default false
  },
  returns: {
    success: boolean,
    screenshot: string,  // base64 encoded
    error?: string
  }
}
```

---

#### Contract 3: Filesystem MCP (Built-in)

**Operations**: read_file, write_file, list_directory, move_file, delete_file

**read_file**:
```typescript
{
  command: "read_file",
  params: {
    path: string  // absolute path
  },
  returns: {
    success: boolean,
    content: string,
    error?: string
  }
}
```

**write_file**:
```typescript
{
  command: "write_file",
  params: {
    path: string,
    content: string
  },
  returns: {
    success: boolean,
    error?: string
  }
}
```

**move_file**:
```typescript
{
  command: "move_file",
  params: {
    source: string,
    destination: string
  },
  returns: {
    success: boolean,
    error?: string
  }
}
```

---

### Quickstart Guide

*For developers setting up the project for the first time.*

#### Prerequisites

1. **Python 3.13**: Install from python.org or use `pyenv install 3.13`
2. **Node.js v24+**: Install from nodejs.org
3. **UV**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
4. **PM2**: `npm install -g pm2`
5. **Obsidian v1.10.6+**: Install from obsidian.md (optional, for vault viewing)
6. **Claude Code**: Install from claude.ai/download

#### Step 1: Clone and Initialize

```bash
cd "D:\D Data\Personal AI Employee Hackathon"
uv sync  # Install Python dependencies
```

#### Step 2: Create .env File

```bash
# Copy example
copy .env.example .env

# Edit .env with your values:
notepad .env
```

Required values:
```
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_CREDENTIALS=C:\absolute\path\to\credentials.json
WHATSAPP_SESSION_PATH=C:\absolute\path\to\whatsapp_session
DRY_RUN=true
VAULT_PATH=D:\D Data\Personal AI Employee Hackathon\AI_Employee_Vault
DEV_MODE=true
```

#### Step 3: Setup Gmail OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json` to path in GMAIL_CREDENTIALS
6. First run of GmailWatcher will open browser for consent

#### Step 4: Create Vault Structure

```bash
# Run vault setup script (or create manually)
mkdir AI_Employee_Vault\Inbox
mkdir AI_Employee_Vault\Needs_Action
mkdir AI_Employee_Vault\In_Progress\claude
mkdir AI_Employee_Vault\Plans
mkdir AI_Employee_Vault\Pending_Approval
mkdir AI_Employee_Vault\Approved
mkdir AI_Employee_Vault\Rejected
mkdir AI_Employee_Vault\Done
mkdir AI_Employee_Vault\Logs\pm2
mkdir AI_Employee_Vault\Briefings
mkdir AI_Employee_Vault\Accounting

# Create template files
copy specs\003-ai-employee-vault\templates\Dashboard.md AI_Employee_Vault\
copy specs\003-ai-employee-vault\templates\Company_Handbook.md AI_Employee_Vault\
copy specs\003-ai-employee-vault\templates\Business_Goals.md AI_Employee_Vault\
```

#### Step 5: Test Watchers (Dry Run)

```bash
# GmailWatcher test
uv run python src/watchers/gmail_watcher.py

# Expected output:
# [GmailWatcher] Starting...
# [GmailWatcher] [DRY RUN] Would create EMAIL_<id>.md

# WhatsAppWatcher test (first run opens browser)
uv run python src/watchers/whatsapp_watcher.py

# Expected output:
# [WhatsAppWatcher] Starting...
# [WhatsAppWatcher] [DRY RUN] Would create WHATSAPP_*.md

# FilesystemWatcher test
# Drop a .pdf file in AI_Employee_Vault\Inbox\
# Watcher will log: [FilesystemWatcher] [DRY RUN] Would copy <file> to Needs_Action/
```

#### Step 6: Configure MCP Servers

Edit `.qwen/mcp.json`:
```json
{
  "servers": [
    { "name": "filesystem", "type": "builtin" },
    {
      "name": "email",
      "command": "node",
      "args": ["C:\\absolute\\path\\to\\email-mcp\\index.js"],
      "env": { "GMAIL_CREDENTIALS": "C:\\absolute\\path\\to\\credentials.json" }
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@anthropic/browser-mcp"],
      "env": { "HEADLESS": "true" }
    }
  ]
}
```

Test email-mcp:
```bash
node C:\absolute\path\to\email-mcp\index.js
# Should start without errors
```

#### Step 7: Deploy with PM2

```bash
# Start all 4 processes
pm2 start ecosystem.config.js

# Check status
pm2 list

# View logs
pm2 logs

# Save process list (auto-start on boot)
pm2 save
pm2 startup  # Copy/paste the command in admin terminal
```

#### Step 8: Verify End-to-End

1. Send a test email to monitored Gmail account with subject "Test"
2. Wait 120 seconds
3. Check `AI_Employee_Vault\Needs_Action\` for EMAIL_*.md file
4. Claude should process it and create `Plans\PLAN_test.md`
5. If approval required, file appears in `Pending_Approval\`
6. Move to `Approved\` → action executes → file moves to `Done\`

#### Common Issues

**GmailWatcher returns 403**:
- Ensure Gmail API is enabled in Google Cloud Console
- Check OAuth consent screen is configured for "External" + testing mode
- Verify credentials.json path is absolute and file exists

**WhatsApp session not persisting**:
- Ensure WHATSAPP_SESSION_PATH is absolute and writable
- First run must complete QR scan in headful mode
- Check browser isn't blocked by antivirus

**PM2 processes won't start**:
- Run `pm2 delete all` and retry
- Check Python path in ecosystem.config.js is correct
- Run `pm2 logs` for error details

**Claude can't read vault**:
- Verify VAULT_PATH in .env matches actual vault location
- Check file permissions allow read/write
- Test with simple file operation: `cat AI_Employee_Vault\Dashboard.md`

---

**Phase 1 Complete**: data-model.md, contracts, and quickstart.md documented.
