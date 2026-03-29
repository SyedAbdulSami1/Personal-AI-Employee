# Feature Specification: Write SPEC.md with all 8 sections

**Feature Branch**: `002-spec`
**Created**: 2026-03-28
**Status**: Draft
**Input**: User description: """nts double-work)
├── Plans/              ← Claude writes PLAN_<taskname>.md files here
├── Pending_Approval/   ← Claude writes approval requests; user reviews
├── Approved/           ← User moves file here = approved; triggers MCP
├── Rejected/           ← User moves file here = rejected; Claude logs+stops
├── Done/               ← Completed tasks; Ralph Wiggum checks this folder
├── Logs/               ← All JSON action logs + PM2 logs
│   └── pm2/            ← PM2 process logs per watcher
├── Briefings/          ← Monday CEO briefings generated here
├── Accounting/         ← Finance Watcher writes Current_Month.md here
├── Dashboard.md        ← Real-time system status; Claude updates after each task
├── Company_Handbook.md ← Rules of engagement; Claude reads before every action
└── Business_Goals.md   ← Q1 targets, KPIs, subscription rules

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPEC-002: FILE SCHEMAS (exact YAML frontmatter for every file type)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Document these 4 schemas with all required fields:

SCHEMA A — Needs_Action file (created by Watchers):
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

SCHEMA B — Plan file (/Plans/PLAN_<taskname>.md, created by Claude):
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

SCHEMA C — Approval request (/Pending_Approval/<TYPE>_<task>.md):
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

SCHEMA D — Audit log entry (/Logs/YYYY-MM-DD.json, one JSON per line):
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

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPEC-003: WATCHER SPECIFICATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Document these 3 watchers:

WATCHER-001 GmailWatcher
  File           : src/watchers/gmail_watcher.py
  Class          : GmailWatcher(BaseWatcher) — OOP, extends BaseWatcher
  Poll interval  : 120 seconds
  Gmail API query: "is:unread is:important"
  Auth           : OAuth2 via credentials.json (path from GMAIL_CREDENTIALS env)
  Output         : Needs_Action/EMAIL_<message_id>.md using Schema A
  Dedup          : in-memory processed_ids set (cleared on restart)
  DRY_RUN        : logs "[DRY RUN] Would create EMAIL_<id>.md" — no file written
  Error handling : catch google.auth.exceptions.TransportError → retry with backoff
                   catch googleapiclient.errors.HttpError → log + alert human
  Console output : [GmailWatcher] Starting... | [GmailWatcher] Found N new emails
                   [GmailWatcher] Created EMAIL_<id>.md | [ERROR] <full message>

WATCHER-002 WhatsAppWatcher
  File           : src/watchers/whatsapp_watcher.py
  Class          : WhatsAppWatcher(BaseWatcher) — OOP, extends BaseWatcher
  Poll interval  : 30 seconds
  Method         : Playwright persistent context, headless=True after first QR scan
  Session path   : from WHATSAPP_SESSION_PATH env var
  Keywords       : ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing']
  Output         : Needs_Action/WHATSAPP_<contact>_<timestamp>.md using Schema A
  First run      : headless=False → user scans QR code → session saved → headless
  DRY_RUN        : logs "[DRY RUN] Would create WHATSAPP_*.md" — no file written
  Error handling : catch playwright TimeoutError → log + wait 60s before retry
                   catch browser crash → relaunch browser, log [ERROR] with traceback
  Console output : [WhatsAppWatcher] Starting... | [WhatsAppWatcher] Found N urgent
                   [ERROR] Browser crashed: <traceback>

WATCHER-003 FilesystemWatcher
  File           : src/watchers/filesystem_watcher.py
  Class          : DropFolderHandler(FileSystemEventHandler) — OOP, watchdog library
  Monitors       : AI_Employee_Vault/Inbox/
  File types     : .pdf, .docx, .csv, .txt, .md only (others silently ignored)
  On new file    : copy to Needs_Action/ + create sidecar .md with Schema A frontmatter
  DRY_RUN        : logs "[DRY RUN] Would copy <file> to Needs_Action/" — no copy
  Error handling : catch PermissionError → log [ERROR] cannot read file
                   catch shutil.Error → log + alert human via ALERT_*.md
  Console output : [FilesystemWatcher] Watching Inbox/ | [FilesystemWatcher] New file: x

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPEC-004: MCP SERVER CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Document the MCP config file location and all 3 servers:

Config file: .claude/mcp.json

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
      "env": { "GMAIL_CREDENTIALS": "/absolute/path/to/credentials.json" },
      "note": "Handles send, draft, search for Gmail"
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@anthropic/browser-mcp"],
      "env": { "HEADLESS": "true" },
      "note": "Playwright browser for LinkedIn, payment portals"
    }
  ]
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPEC-005: RALPH WIGGUM LOOP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Document the stop-hook pattern:

File     : .claude/hooks/stop.py
Trigger  : Fires every time Claude Code attempts to exit
Algorithm:
  1. Read TASK_FILE env var (absolute path of current task .md)
  2. Read RALPH_COUNTER env var (default "0")
  3. done_path = vault/Done/basename(TASK_FILE)
  4. If done_path.exists() → print "[Ralph] Task complete ✅" → sys.exit(0)
  5. If counter >= 10 → print "[Ralph] Max iterations reached ⚠️" →
       write ALERT_ralph_max_<task>.md to /Needs_Action/ → sys.exit(0)
  6. Else → counter += 1 → print "[Ralph] Attempt <n>/10 — retrying..." →
       sys.exit(1) [blocks Claude exit, triggers re-run]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPEC-006: SECURITY REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Document .env template:

# .env — NEVER commit. Add to .gitignore immediately.
GMAIL_CLIENT_ID=
GMAIL_CLIENT_SECRET=
GMAIL_CREDENTIALS=/absolute/path/to/credentials.json
BANK_API_TOKEN=
WHATSAPP_SESSION_PATH=/absolute/path/to/whatsapp_session
DRY_RUN=true
VAULT_PATH=/absolute/path/to/AI_Employee_Vault
DEV_MODE=true

Rate limits to enforce in code:
  MAX_EMAILS_PER_HOUR    = 10
  MAX_PAYMENTS_PER_HOUR  = 3
  MAX_SOCIAL_POSTS_PER_DAY = 5

Permission table: (copy from SPEC-002 permission boundaries above)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPEC-007: ERROR HANDLING STANDARD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Document these error categories and their exact handling:

| Category       | Examples                        | Handler                                      |
|----------------|---------------------------------|----------------------------------------------|
| Transient      | Network timeout, API rate limit | Exponential backoff: 1s, 2s, 4s (max 60s)   |
| Authentication | Expired token, 401/403          | Log [ERROR], write ALERT_*.md, pause ops     |
| Logic          | Claude misinterprets task       | Move to /Rejected/, write human review note  |
| Data           | Corrupted .md, missing field    | Quarantine file in /Rejected/, log + alert   |
| System         | Orchestrator crash, disk full   | watchdog.py restarts + writes ALERT_*.md     |

Console logging standard for ALL Python files:
  import logging
  logging.basicConfig(
      level=logging.DEBUG,
      format='%(asctime)s [%(name)s] %(levelname)s — %(message)s',
      handlers=[
          logging.StreamHandler(),                    # Always print to console
          logging.FileHandler('vault/Logs/app.log')  # Always write to file
      ]
  )
  # Usage: self.logger.info("...") | self.logger.error("...", exc_info=True)
  # exc_info=True prints full traceback to BOTH console AND log file

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPEC-008: CEO BRIEFING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trigger  : Every Sunday 11:00 PM (cron on Mac/Linux, Task Scheduler on Windows)
Inputs   : Business_Goals.md + /Done/ files this week + Accounting/Current_Month.md
Output   : /Briefings/YYYY-MM-DD_Monday_Briefing.md
Required sections in output:
  1. Executive Summary (2-3 sentences)
  2. Revenue: This Week | MTD | vs Target | Trend
  3. Completed Tasks (from /Done/ — filter by this week's dates)
  4. Bottlenecks (tasks where actual time > expected time)
  5. Proactive Suggestions (unused subscriptions, upcoming deadlines)
  6. Footer: "Generated by AI Employee v0.1 — Review at your convenience"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT INSTRUCTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Write SPEC.md to project root with all 8 sections (SPEC-001 to SPEC-008).
After writing: print "✅ SPEC.md written — [8] sections, [X] lines"
Print each spec section ID and its line count.
"""