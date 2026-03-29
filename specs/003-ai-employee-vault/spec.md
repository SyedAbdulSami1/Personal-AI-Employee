# Feature Specification: AI Employee Vault System

**Feature Branch**: `003-ai-employee-vault`
**Created**: 2026-03-28
**Status**: Draft
**Input**: Personal AI Employee — Silver Tier with Obsidian vault, Python Watchers, MCP servers, and HITL workflows

## System Overview

**Name**: Personal AI Employee — Silver Tier (20-30 hrs scope)

**Stack**: Claude Code + Obsidian vault + Python Watchers + MCP servers

**Pattern**: Perception → Obsidian Vault → Reasoning → HITL → Action

**Silver Tier Deliverables**:
- ✓ Obsidian vault (all folders + Dashboard + Handbook + Goals)
- ✓ GmailWatcher + WhatsAppWatcher running via PM2
- ✓ LinkedIn auto-post via browser-mcp with HITL approval
- ✓ Claude reasoning loop creating Plan.md files
- ✓ email-mcp for approved email sends
- ✓ Human-in-the-loop file-move approval workflow
- ✓ Daily 8AM briefing via cron/Task Scheduler
- ✓ All features as Agent Skills
- ✓ Full audit logging + watchdog process

## Clarifications

### Session 2026-03-29

- Q: LinkedIn integration approach? → A: browser-mcp for web automation

## User Scenarios & Testing

### User Story 1 - Email Processing Workflow (Priority: P1)

As a business owner, I want emails from Gmail to automatically appear in the vault's Needs_Action folder so that I can review and process them without manually checking Gmail.

**Why this priority**: Email is the primary communication channel for business. Automating email intake is the foundation for all downstream processing.

**Independent Test**: Can be fully tested by sending an email to the monitored Gmail account and verifying a corresponding .md file appears in Needs_Action/ with correct frontmatter within 120 seconds.

**Acceptance Scenarios**:

1. **Given** GmailWatcher is running, **When** a new unread important email arrives, **Then** a file named EMAIL_<message_id>.md is created in Needs_Action/ with Schema A frontmatter
2. **Given** an email was already processed, **When** GmailWatcher polls again, **Then** the same email is not duplicated (dedup via processed_ids set)
3. **Given** DRY_RUN=true, **When** a new email arrives, **Then** log shows "[DRY RUN] Would create EMAIL_<id>.md" but no file is written

---

### User Story 2 - WhatsApp Urgent Message Detection (Priority: P1)

As a business owner, I want urgent WhatsApp messages to be automatically captured and flagged so that time-sensitive requests are not missed.

**Why this priority**: WhatsApp is used for urgent client communication. Missing urgent messages directly impacts customer satisfaction and revenue.

**Independent Test**: Can be fully tested by sending a WhatsApp message containing keyword "urgent" and verifying a file appears in Needs_Action/ within 30 seconds.

**Acceptance Scenarios**:

1. **Given** WhatsAppWatcher is running with active session, **When** a message containing keywords ('urgent', 'asap', 'invoice', 'payment', 'help', 'pricing') arrives, **Then** a file named WHATSAPP_<contact>_<timestamp>.md is created in Needs_Action/
2. **Given** first run of WhatsAppWatcher, **When** no session exists, **Then** browser opens with headless=False for QR code scan, session is saved, then subsequent runs are headless
3. **Given** browser crash during operation, **When** watchdog detects crash, **Then** browser is relaunched and error is logged with traceback

---

### User Story 3 - File Drop Processing (Priority: P2)

As a user, I want to drop files into the Inbox folder and have them automatically processed so that I don't need to manually create action items.

**Why this priority**: Manual file drops provide a flexible intake mechanism for documents that don't come from Gmail/WhatsApp.

**Independent Test**: Can be fully tested by copying a .pdf file to Inbox/ and verifying it's copied to Needs_Action/ with a sidecar .md file.

**Acceptance Scenarios**:

1. **Given** FilesystemWatcher is monitoring Inbox/, **When** a new .pdf, .docx, .csv, .txt, or .md file appears, **Then** file is copied to Needs_Action/ with sidecar .md using Schema A
2. **Given** a .exe file is dropped in Inbox/, **When** FilesystemWatcher detects it, **Then** file is silently ignored (only allowed types processed)
3. **Given** PermissionError when reading file, **When** watcher attempts copy, **Then** error is logged as "[ERROR] cannot read file" and ALERT_*.md is created

---

### User Story 4 - Claude Task Planning (Priority: P1)

As the system orchestrator, I want Claude to automatically create Plan.md files for tasks in Needs_Action/ so that work is structured and trackable.

**Why this priority**: Automated planning transforms unstructured inputs into actionable, step-by-step tasks with clear completion criteria.

**Independent Test**: Can be fully tested by placing a Needs_Action file and verifying a corresponding PLAN_<taskname>.md is created in Plans/ with Schema B frontmatter.

**Acceptance Scenarios**:

1. **Given** a new file in Needs_Action/, **When** Claude processes it, **Then** a Plan file is created in Plans/ with objective, steps, approval requirement, and completion condition
2. **Given** a Plan requires human approval, **When** Claude completes planning, **Then** an approval request file is created in Pending_Approval/ using Schema C
3. **Given** user moves file from Pending_Approval/ to Approved/, **Then** MCP email server is triggered to send the email

---

### User Story 5 - Human-in-the-Loop Approval Workflow (Priority: P1)

As a business owner, I want to review and approve sensitive actions (emails, payments, posts) before they execute so that I maintain control over critical operations.

**Why this priority**: HITL prevents costly mistakes and maintains human oversight for high-risk actions.

**Independent Test**: Can be fully tested by moving an approval request file to Approved/ and verifying the action executes, or to Rejected/ and verifying it's logged and stopped.

**Acceptance Scenarios**:

1. **Given** an approval request in Pending_Approval/, **When** user moves it to Approved/, **Then** the action is executed via MCP and result is logged
2. **Given** an approval request in Pending_Approval/, **When** user moves it to Rejected/, **Then** Claude logs the rejection and stops processing that task
3. **Given** an approval request created at 2026-01-07T10:00:00Z, **When** current time exceeds expires field (24 hours), **Then** request is auto-rejected and logged

---

### User Story 6 - Ralph Wiggum Iteration Control (Priority: P2)

As the system, I want to limit Claude's retry attempts to prevent infinite loops so that failed tasks are escalated to humans.

**Why this priority**: Prevents resource waste and ensures failed tasks are surfaced for human intervention.

**Independent Test**: Can be fully tested by triggering a task that cannot complete and verifying Ralph counter increments and task is moved to Done/ or ALERT is created after 10 attempts.

**Acceptance Scenarios**:

1. **Given** a task file in In_Progress/claude/, **When** Claude exits without moving file to Done/, **Then** stop.py hook increments RALPH_COUNTER and triggers re-run
2. **Given** RALPH_COUNTER reaches 10, **When** stop.py hook fires, **Then** "[Ralph] Max iterations reached ⚠️" is printed and ALERT_ralph_max_<task>.md is created in Needs_Action/
3. **Given** task file is moved to Done/, **When** stop.py hook fires, **Then** "[Ralph] Task complete ✅" is printed and Claude exits successfully

---

### User Story 7 - CEO Briefing Generation (Priority: P3)

As the CEO, I want a weekly briefing every Monday morning so that I can review last week's performance and plan accordingly.

**Why this priority**: Provides strategic oversight and ensures the AI employee's work aligns with business goals.

**Independent Test**: Can be fully tested by triggering the briefing script and verifying a file is created in Briefings/ with all 6 required sections.

**Acceptance Scenarios**:

1. **Given** it's Sunday 11:00 PM, **When** cron/Task Scheduler triggers briefing generation, **Then** a file named YYYY-MM-DD_Monday_Briefing.md is created in Briefings/
2. **Given** briefing generation, **When** reading Business_Goals.md and /Done/ files from this week, **Then** all 6 required sections are present: Executive Summary, Revenue, Completed Tasks, Bottlenecks, Proactive Suggestions, Footer
3. **Given** no tasks were completed this week, **When** briefing is generated, **Then** "Completed Tasks" section indicates "No tasks completed this week"

---

### Edge Cases

- **What happens when Gmail API quota is exceeded?**: Watcher logs error, waits 60s with exponential backoff, and continues polling
- **How does system handle corrupted .md files?**: File is quarantined in Rejected/, error is logged, and ALERT_*.md is created for human review
- **What happens when disk is full?**: watchdog.py detects condition, writes ALERT_disk_full.md to Needs_Action/, and pauses all watchers
- **How are duplicate emails handled?**: GmailWatcher maintains in-memory processed_ids set (cleared on restart) to prevent duplicates
- **What if approval request expires?**: Requests older than 24 hours (per expires field) are auto-rejected and moved to Rejected/
- **How does WhatsApp session persistence work?**: Session is saved to path from WHATSAPP_SESSION_PATH env var; first run requires QR scan, subsequent runs are headless

## Requirements

### Functional Requirements

- **FR-001**: System MUST create and maintain the exact folder structure: Inbox/, Needs_Action/, In_Progress/claude/, Plans/, Pending_Approval/, Approved/, Rejected/, Done/, Logs/, Logs/pm2/, Briefings/, Accounting/
- **FR-002**: System MUST create Dashboard.md and update it after each task completion with real-time system status
- **FR-003**: System MUST create Company_Handbook.md containing rules of engagement that Claude reads before every action
- **FR-004**: System MUST create Business_Goals.md containing Q1 targets, KPIs, and subscription rules
- **FR-005**: GmailWatcher MUST poll every 120 seconds using Gmail API query "is:unread is:important"
- **FR-006**: GmailWatcher MUST create Needs_Action/EMAIL_<message_id>.md files using Schema A frontmatter
- **FR-007**: GmailWatcher MUST use OAuth2 authentication via credentials.json (path from GMAIL_CREDENTIALS env)
- **FR-008**: GmailWatcher MUST implement in-memory deduplication via processed_ids set (cleared on restart)
- **FR-009**: WhatsAppWatcher MUST poll every 30 seconds using Playwright persistent context
- **FR-010**: WhatsAppWatcher MUST filter messages by keywords: ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing']
- **FR-011**: WhatsAppWatcher MUST create Needs_Action/WHATSAPP_<contact>_<timestamp>.md files using Schema A frontmatter
- **FR-012**: WhatsAppWatcher MUST save session to path from WHATSAPP_SESSION_PATH env var
- **FR-013**: WhatsAppWatcher first run MUST open browser with headless=False for QR scan, then save session for headless operation
- **FR-014**: FilesystemWatcher MUST monitor AI_Employee_Vault/Inbox/ for new files
- **FR-015**: FilesystemWatcher MUST only process .pdf, .docx, .csv, .txt, .md files (others silently ignored)
- **FR-016**: FilesystemWatcher MUST copy new files to Needs_Action/ and create sidecar .md with Schema A frontmatter
- **FR-017**: Claude MUST create Plan files in Plans/PLAN_<taskname>.md using Schema B frontmatter
- **FR-018**: Claude MUST create approval requests in Pending_Approval/<TYPE>_<task>.md using Schema C frontmatter
- **FR-019**: System MUST enforce approval expiry: 24 hours from creation time
- **FR-020**: System MUST create daily audit logs in Logs/YYYY-MM-DD.json with one JSON per line using Schema D
- **FR-021**: email-mcp MUST handle send, draft, search operations for Gmail
- **FR-022**: browser-mcp MUST run Playwright browser for LinkedIn and payment portals
- **FR-023**: Ralph Wiggum stop-hook MUST fire every time Claude Code attempts to exit
- **FR-024**: Ralph Wiggum MUST read TASK_FILE env var and RALPH_COUNTER env var (default "0")
- **FR-025**: Ralph Wiggum MUST increment counter and trigger re-run if counter < 10 and task not in Done/
- **FR-026**: Ralph Wiggum MUST create ALERT_ralph_max_<task>.md when counter >= 10
- **FR-027**: System MUST enforce rate limits: MAX_EMAILS_PER_HOUR=10, MAX_PAYMENTS_PER_HOUR=3, MAX_SOCIAL_POSTS_PER_DAY=5
- **FR-028**: CEO briefing MUST be generated every Sunday 11:00 PM via cron (Mac/Linux) or Task Scheduler (Windows)
- **FR-029**: CEO briefing MUST include 6 sections: Executive Summary, Revenue, Completed Tasks, Bottlenecks, Proactive Suggestions, Footer
- **FR-030**: All Python files MUST use logging.basicConfig with StreamHandler and FileHandler to vault/Logs/app.log
- **FR-031**: All Python files MUST log with format: '%(asctime)s [%(name)s] %(levelname)s — %(message)s'
- **FR-032**: DRY_RUN mode MUST log "[DRY RUN] Would <action>" without executing the action
- **FR-033**: Watchers MUST print console output in format: [WatcherName] Starting... | [WatcherName] Found N <items>
- **FR-034**: Errors MUST be logged with exc_info=True to print full traceback to both console and log file

### Key Entities

- **Needs_Action File**: Created by Watchers; contains incoming emails, WhatsApp messages, and file drops with Schema A frontmatter (type, from, subject, received, priority, status, watcher)
- **Plan File**: Created by Claude in Plans/; contains task breakdown with Schema B frontmatter (created, task_ref, status, iterations, objective, steps, approval requirement, completion condition)
- **Approval Request**: Created by Claude in Pending_Approval/; requires human review with Schema C frontmatter (type, action, amount, recipient, reason, created, expires, status, plan_ref)
- **Audit Log Entry**: JSON entry in Logs/YYYY-MM-DD.json; records all system actions with Schema D fields (timestamp, action_type, actor, target, parameters, approval_status, approved_by, result, error, dry_run)
- **Dashboard.md**: Real-time system status file updated by Claude after each task completion
- **Company_Handbook.md**: Rules of engagement that Claude reads before every action
- **Business_Goals.md**: Q1 targets, KPIs, and subscription rules

## Success Criteria

### Measurable Outcomes

- **SC-001**: GmailWatcher creates Needs_Action files within 120 seconds of email arrival (polling interval)
- **SC-002**: WhatsAppWatcher creates Needs_Action files within 30 seconds of message arrival (polling interval)
- **SC-003**: System processes file drops from Inbox/ to Needs_Action/ within 5 seconds
- **SC-004**: Claude creates Plan files for 100% of Needs_Action files within 1 iteration (no retries needed)
- **SC-005**: Human approval workflow completes within 24 hours (approval expiry enforced)
- **SC-006**: Ralph Wiggum prevents infinite loops by limiting retries to 10 attempts maximum
- **SC-007**: Audit logs capture 100% of system actions (email_send, payment, social_post, file_move, watcher_start, error)
- **SC-008**: CEO briefing is generated every Monday at 8AM with all 6 required sections
- **SC-009**: System handles 10,000+ email messages per month without data loss (Gmail API quota compliant)
- **SC-010**: WhatsApp session persists across restarts without requiring re-scan (session saved to WHATSAPP_SESSION_PATH)
- **SC-011**: Rate limits are enforced: no more than 10 emails/hour, 3 payments/hour, 5 social posts/day
- **SC-012**: DRY_RUN mode prevents all file writes and external actions while logging intended operations
- **SC-013**: Error recovery: transient errors (network timeout, API rate limit) are retried with exponential backoff (1s, 2s, 4s, max 60s)
- **SC-014**: Authentication errors (expired token, 401/403) are logged, ALERT_*.md is created, and operations pause until human intervention
- **SC-015**: System uptime: 99% availability during business hours (8AM-8PM local time) via watchdog.py monitoring

## Assumptions

- User has a Gmail account with OAuth2 credentials (client ID, secret, credentials.json)
- User has WhatsApp Web access and can scan QR code on first run
- User has Node.js installed for email-mcp server
- User has PM2 installed globally for process management
- User has Obsidian installed (optional, for vault viewing/editing)
- Windows Task Scheduler or cron is available for scheduled tasks
- User will manually move files between folders for approval workflow (no UI provided)
- Bank API token is provided by user for payment operations
- LinkedIn account credentials are provided by user for auto-posting

## Security Requirements

### Environment Variables (.env template)

```
# .env — NEVER commit. Add to .gitignore immediately.
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_CREDENTIALS=/absolute/path/to/credentials.json
BANK_API_TOKEN=
WHATSAPP_SESSION_PATH=/absolute/path/to/whatsapp_session
DRY_RUN=true
VAULT_PATH=/absolute/path/to/AI_Employee_Vault
DEV_MODE=true
```

### Rate Limits

- MAX_EMAILS_PER_HOUR = 10
- MAX_PAYMENTS_PER_HOUR = 3
- MAX_SOCIAL_POSTS_PER_DAY = 5

### Permission Boundaries

| Action | Permission Required | Approval Method |
|--------|---------------------|-----------------|
| Read emails | Auto-approved | Gmail OAuth2 |
| Send emails | Human approval | File move to Approved/ |
| Read WhatsApp | Auto-approved | Session cookie |
| Send WhatsApp | Human approval | File move to Approved/ |
| Post to LinkedIn | Human approval | File move to Approved/ |
| Process payments | Human approval | File move to Approved/ |
| Delete files | Human approval | File move to Approved/ |
| Move files between vault folders | Auto-approved | System operation |

## Error Handling Standard

### Error Categories and Handlers

| Category | Examples | Handler |
|----------|----------|---------|
| Transient | Network timeout, API rate limit | Exponential backoff: 1s, 2s, 4s (max 60s) |
| Authentication | Expired token, 401/403 | Log [ERROR], write ALERT_*.md, pause ops |
| Logic | Claude misinterprets task | Move to /Rejected/, write human review note |
| Data | Corrupted .md, missing field | Quarantine file in /Rejected/, log + alert |
| System | Orchestrator crash, disk full | watchdog.py restarts + writes ALERT_*.md |

### Console Logging Standard

All Python files MUST use:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(name)s] %(levelname)s — %(message)s',
    handlers=[
        logging.StreamHandler(),  # Always print to console
        logging.FileHandler('vault/Logs/app.log')  # Always write to file
    ]
)

# Usage:
# self.logger.info("...")
# self.logger.error("...", exc_info=True)  # exc_info=True prints full traceback to BOTH console AND log file
```

## MCP Server Configuration

**Config file**: `.claude/mcp.json`

```json
{
  "servers": [
    {
      "name": "filesystem",
      "type": "builtin",
      "note": "Built-in. Claude reads/writes vault files. No extra install."
    },
    {
      "name": "email",
      "command": "node",
      "args": ["/absolute/path/to/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/absolute/path/to/credentials.json"
      },
      "note": "Handles send, draft, search for Gmail"
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@anthropic/browser-mcp"],
      "env": {
        "HEADLESS": "true"
      },
      "note": "Playwright browser for LinkedIn web automation, payment portals"
    }
  ]
}
```

**LinkedIn Integration**: Uses browser-mcp (not LinkedIn API) to automate posting via LinkedIn web interface. No separate API approval required.

## File Schemas

### SCHEMA A — Needs_Action File (created by Watchers)

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

### SCHEMA B — Plan File (/Plans/PLAN_<taskname>.md, created by Claude)

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

### SCHEMA C — Approval Request (/Pending_Approval/<TYPE>_<task>.md)

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
## To REJECT: Move this file to /Rejected/
```

### SCHEMA D — Audit Log Entry (/Logs/YYYY-MM-DD.json, one JSON per line)

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

## Watcher Specifications

### WATCHER-001: GmailWatcher

- **File**: `src/watchers/gmail_watcher.py`
- **Class**: `GmailWatcher(BaseWatcher)` — OOP, extends BaseWatcher
- **Poll interval**: 120 seconds
- **Gmail API query**: `"is:unread is:important"`
- **Auth**: OAuth2 via credentials.json (path from GMAIL_CREDENTIALS env)
- **Output**: Needs_Action/EMAIL_<message_id>.md using Schema A
- **Dedup**: in-memory processed_ids set (cleared on restart)
- **DRY_RUN**: logs `"[DRY RUN] Would create EMAIL_<id>.md"` — no file written
- **Error handling**:
  - catch `google.auth.exceptions.TransportError` → retry with backoff
  - catch `googleapiclient.errors.HttpError` → log + alert human
- **Console output**: `[GmailWatcher] Starting...` | `[GmailWatcher] Found N new emails` | `[GmailWatcher] Created EMAIL_<id>.md` | `[ERROR] <full message>`

### WATCHER-002: WhatsAppWatcher

- **File**: `src/watchers/whatsapp_watcher.py`
- **Class**: `WhatsAppWatcher(BaseWatcher)` — OOP, extends BaseWatcher
- **Poll interval**: 30 seconds
- **Method**: Playwright persistent context, headless=True after first QR scan
- **Session path**: from WHATSAPP_SESSION_PATH env var
- **Keywords**: `['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing']`
- **Output**: Needs_Action/WHATSAPP_<contact>_<timestamp>.md using Schema A
- **First run**: headless=False → user scans QR code → session saved → headless
- **DRY_RUN**: logs `"[DRY RUN] Would create WHATSAPP_*.md"` — no file written
- **Error handling**:
  - catch `playwright.TimeoutError` → log + wait 60s before retry
  - catch browser crash → relaunch browser, log `[ERROR]` with traceback
- **Console output**: `[WhatsAppWatcher] Starting...` | `[WhatsAppWatcher] Found N urgent` | `[ERROR] Browser crashed: <traceback>`

### WATCHER-003: FilesystemWatcher

- **File**: `src/watchers/filesystem_watcher.py`
- **Class**: `DropFolderHandler(FileSystemEventHandler)` — OOP, watchdog library
- **Monitors**: AI_Employee_Vault/Inbox/
- **File types**: .pdf, .docx, .csv, .txt, .md only (others silently ignored)
- **On new file**: copy to Needs_Action/ + create sidecar .md with Schema A frontmatter
- **DRY_RUN**: logs `"[DRY RUN] Would copy <file> to Needs_Action/"` — no copy
- **Error handling**:
  - catch `PermissionError` → log `[ERROR] cannot read file`
  - catch `shutil.Error` → log + alert human via ALERT_*.md
- **Console output**: `[FilesystemWatcher] Watching Inbox/` | `[FilesystemWatcher] New file: x`

## Ralph Wiggum Loop Specification

**File**: `.claude/hooks/stop.py`

**Trigger**: Fires every time Claude Code attempts to exit

**Algorithm**:
1. Read TASK_FILE env var (absolute path of current task .md)
2. Read RALPH_COUNTER env var (default "0")
3. done_path = vault/Done/basename(TASK_FILE)
4. If done_path.exists() → print `"[Ralph] Task complete ✅"` → sys.exit(0)
5. If counter >= 10 → print `"[Ralph] Max iterations reached ⚠️"` → write ALERT_ralph_max_<task>.md to /Needs_Action/ → sys.exit(0)
6. Else → counter += 1 → print `"[Ralph] Attempt <n>/10 — retrying..."` → sys.exit(1) [blocks Claude exit, triggers re-run]

## CEO Briefing Specification

**Trigger**: Every Sunday 11:00 PM (cron on Mac/Linux, Task Scheduler on Windows)

**Inputs**: 
- Business_Goals.md
- /Done/ files from this week
- Accounting/Current_Month.md

**Output**: /Briefings/YYYY-MM-DD_Monday_Briefing.md

**Required Sections**:
1. Executive Summary (2-3 sentences)
2. Revenue: This Week | MTD | vs Target | Trend
3. Completed Tasks (from /Done/ — filter by this week's dates)
4. Bottlenecks (tasks where actual time > expected time)
5. Proactive Suggestions (unused subscriptions, upcoming deadlines)
6. Footer: "Generated by AI Employee v0.1 — Review at your convenience"
