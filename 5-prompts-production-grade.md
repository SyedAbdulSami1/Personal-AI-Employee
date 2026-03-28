# Personal AI Employee — 5 Production-Grade Prompts
# Har prompt SELF-CONTAINED hai — koi extra file dene ki zaroorat nahi
# Har prompt mein: Debugging + Console Errors + DRY Principle + OOP
# Claude Code terminal mein paste karo — ek ek karke

================================================================================
# PROMPT 1 — /sp.constitution
# Seedha Claude Code terminal mein paste karo
# Kya karega: CONSTITUTION.md file likhega project root mein
================================================================================

```
You are a principal architect. Your ONLY job right now is to write
CONSTITUTION.md to the project root directory. Do not ask questions.
Do not write code. Write exactly the document described below.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROJECT CONTEXT (read carefully before writing)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Project     : Personal AI Employee — Digital FTE (Full-Time Equivalent)
Tagline     : Your life and business on autopilot.
              Local-first, agent-driven, human-in-the-loop.
What it is  : NOT a chatbot. A proactive autonomous agent that manages
              Gmail, WhatsApp, Bank, Social Media, and Project Tasks 24/7.
Brain       : Claude Code (sole reasoning engine — no other LLMs)
Memory/GUI  : Obsidian vault (local Markdown — NEVER cloud sync of secrets)
Senses      : Python Watcher scripts (Gmail, WhatsApp, filesystem)
Hands       : MCP servers (email-mcp, browser-mcp, filesystem-mcp)
Glue        : orchestrator.py (master) + watchdog.py (health monitor)
Persistence : Ralph Wiggum stop-hook — Claude keeps iterating until
              task file moves to /Done/ or max 10 iterations reached

Business value:
  Human FTE  : ~2,000 hrs/year @ ~$5.00/task
  Digital FTE: ~8,760 hrs/year @ ~$0.50/task → 85-90% cost saving

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WRITE CONSTITUTION.md WITH EXACTLY THESE 7 SECTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Section 1 — MISSION STATEMENT
Write 4 sentences covering:
- What this Digital FTE is and what it replaces
- Who it serves (solo founder / small business owner)
- What 24/7 autonomous operation means in practice
- What "success" looks like (tasks completed in /Done/, CEO briefed Monday)

## Section 2 — 10 NON-NEGOTIABLE RULES
Write exactly these 10 rules as a numbered list. Each rule must have
a one-line title and a two-line explanation:

Rule 1  : LOCAL-FIRST ALWAYS
          All sensitive data stays on user's machine. Secrets (.env,
          WhatsApp session, bank tokens) never enter the Obsidian vault.

Rule 2  : CLAUDE CODE IS THE ONLY BRAIN
          No other LLM makes decisions. All reasoning goes through
          Claude Code pointed at the Obsidian vault.

Rule 3  : HUMAN-IN-THE-LOOP FOR SENSITIVE ACTIONS
          Any payment (any amount to new recipient, >$50 to known),
          bulk email, social DM, or irreversible action needs human approval.
          Claude writes to /Pending_Approval/ and WAITS.

Rule 4  : AUDIT EVERY ACTION
          Every external action (email send, payment, post, file move)
          is logged to /Vault/Logs/YYYY-MM-DD.json before AND after execution.
          Silent actions are forbidden.

Rule 5  : DRY_RUN=true IN DEVELOPMENT
          All action scripts check DRY_RUN env var before executing.
          No real API calls during testing. Log "[DRY RUN] would do X" instead.

Rule 6  : FAIL LOUD — NEVER FAIL SILENT
          All exceptions must be caught, logged with full traceback to
          /Vault/Logs/, AND printed to console with [ERROR] prefix.
          No bare except: pass blocks anywhere.

Rule 7  : CREDENTIALS NEVER IN VAULT
          .env, credentials.json, WhatsApp session, bank tokens —
          all stored outside vault. Added to .gitignore immediately.
          Rotate monthly.

Rule 8  : GRACEFUL DEGRADATION
          Gmail API down → queue locally. Banking timeout → NEVER auto-retry.
          Claude unavailable → watchers keep collecting. System never crashes
          silently — watchdog.py alerts human via /Needs_Action/ALERT_*.md

Rule 9  : ALL AI FUNCTIONALITY AS AGENT SKILLS
          Every capability Claude uses must be implemented as a
          reusable Agent Skill (SKILL.md pattern). No one-off prompts.

Rule 10 : RALPH WIGGUM LOOP — FINISH WHAT YOU START
          Claude iterates max 10 times per task. Exits only when task
          file is in /Done/. Counter tracked in temp state file.
          At iteration 10: force exit + write ALERT to /Needs_Action/.

## Section 3 — DECISION AUTHORITY TABLE
Write this exact table:

| Action Category   | Auto-Approve                    | Always Require Human Approval         |
|-------------------|---------------------------------|---------------------------------------|
| Email replies     | Known contacts, within 24hrs    | New contacts, bulk sends, CC lists    |
| Payments          | None (all flagged)              | Every payment without exception       |
| Social media      | Pre-approved scheduled posts    | Replies, DMs, new content, hashtags   |
| File operations   | Create, read, copy              | Delete, move outside vault            |
| WhatsApp          | Keyword-flagged draft only      | Actual send — always manual           |
| Banking           | Read/report transactions        | Any transaction execution             |
| Calendar          | View, suggest time              | Create/delete events with externals   |

## Section 4 — ETHICAL BOUNDARIES
Write: "Claude must NEVER act autonomously in these situations:"
Then list with one-line explanation each:
- Emotional contexts (condolences, conflict messages, apologies)
- Legal matters (contracts, NDAs, regulatory filings, legal advice)
- Medical decisions (health-related actions for self or others)
- Financial edge cases (unusual amounts, new payees, foreign transfers)
- Irreversible deletions (files, accounts, subscriptions cancellation)
- Any situation where Company_Handbook.md has NO explicit rule

## Section 5 — APPROVED TECHNOLOGY STACK
Write as a table:

| Layer        | Technology                          | Purpose                              |
|--------------|-------------------------------------|--------------------------------------|
| Brain        | Claude Code (claude-sonnet-4-5)     | Sole reasoning and decision engine   |
| Memory       | Obsidian vault (local Markdown)     | Dashboard, task queue, audit trail   |
| Senses       | Python 3.13 Watcher scripts         | Gmail, WhatsApp, filesystem monitor  |
| Hands        | MCP servers (email, browser, fs)    | Execute approved external actions    |
| Glue         | orchestrator.py + watchdog.py       | Process management and health        |
| Persistence  | Ralph Wiggum stop-hook              | Autonomous multi-step completion     |
| Process Mgr  | PM2                                 | Keep watchers alive across reboots   |
| Security     | .env + OS keychain                  | Credential storage outside vault     |
| Debugging    | Python logging module               | Console + file logs for every action |

## Section 6 — MANDATORY OVERSIGHT SCHEDULE
Write as a table:

| Frequency | Duration  | What to Check                                    |
|-----------|-----------|--------------------------------------------------|
| Daily     | 2 minutes | Dashboard.md — pending actions, system status    |
| Weekly    | 15 minutes| /Vault/Logs/ — all action log entries this week  |
| Monthly   | 1 hour    | Full audit, credential rotation, cost review     |
| Quarterly | 2 hours   | Security review, API access audit, skill update  |

## Section 7 — DEFINITION OF DONE
Write: "A task is considered COMPLETE only when ALL of these are true:"
1. Task .md file exists in /Done/ folder
2. Corresponding JSON entry exists in /Vault/Logs/YYYY-MM-DD.json
3. Dashboard.md "Recent Activity" section shows the completed task
4. If external action was taken: approval file is in /Done/
5. No [ERROR] entries in today's log related to this task

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT INSTRUCTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Write CONSTITUTION.md to the project root
2. Print: "✅ CONSTITUTION.md written — [X] lines, [7] sections"
3. Print each section heading and its line count
Do NOT use placeholders. Every field must have real content.
```

================================================================================
# PROMPT 2 — /sp.specify
# Seedha Claude Code terminal mein paste karo
# Kya karega: SPEC.md file likhega — poori system specification
================================================================================

```
You are a senior solutions architect. Write SPEC.md to the project root.
This is the complete baseline specification. Do not write code yet.
Fill every section with real, specific, non-placeholder content.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SYSTEM BEING SPECIFIED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name   : Personal AI Employee — Silver Tier (20-30 hrs scope)
Stack  : Claude Code + Obsidian vault + Python Watchers + MCP servers
Pattern: Perception → Obsidian Vault → Reasoning → HITL → Action

Silver Tier must deliver:
  ✓ Obsidian vault (all folders + Dashboard + Handbook + Goals)
  ✓ GmailWatcher + WhatsAppWatcher running via PM2
  ✓ LinkedIn auto-post with HITL approval
  ✓ Claude reasoning loop creating Plan.md files
  ✓ email-mcp for approved email sends
  ✓ Human-in-the-loop file-move approval workflow
  ✓ Daily 8AM briefing via cron/Task Scheduler
  ✓ All features as Agent Skills
  ✓ Full audit logging + watchdog process

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SPEC-001: VAULT FOLDER STRUCTURE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Document this exact folder structure with purpose of each folder:

AI_Employee_Vault/
├── Inbox/              ← User manually drops files here for processing
├── Needs_Action/       ← Watchers write here; Orchestrator reads here
├── In_Progress/        ← Claim-by-move: agent moves file here to own task
│   └── claude/         ← Sub-folder per agent (prevents double-work)
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
```

================================================================================
# PROMPT 3 — /sp.plan
# Seedha Claude Code terminal mein paste karo
# Kya karega: PLAN.md file likhega — phased implementation plan with checkboxes
================================================================================

```
You are a senior project manager. Write PLAN.md to the project root.
Silver Tier scope (20-30 hours total). Every task must have a checkbox.
Every command must be exact and runnable. No placeholders.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CODING STANDARDS TO EMBED IN EVERY PHASE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
These standards apply to ALL code written in every phase:

DRY PRINCIPLE:
  - Never write the same logic twice
  - BaseWatcher handles all shared watcher logic (polling, logging, error catching)
  - AuditLogger is the single place for all logging — imported everywhere
  - RetryHandler decorator applied to ALL external API calls
  - Config loaded once from .env via a single Config class, passed by reference

OOP STRUCTURE:
  - BaseWatcher(ABC) → GmailWatcher, WhatsAppWatcher, FilesystemWatcher
  - BaseAction(ABC) → EmailAction, PaymentAction, SocialPostAction
  - AuditLogger (singleton pattern) — one instance shared across all modules
  - RateLimiter (singleton) — one instance, tracks all action types
  - Config (dataclass) — loaded once at startup, passed to all constructors

DEBUGGING STANDARD (apply to every single file):
  import logging
  logging.basicConfig(
      level=logging.DEBUG,
      format='%(asctime)s [%(name)s] %(levelname)s — %(message)s',
      handlers=[
          logging.StreamHandler(),            # Errors ALWAYS visible in console
          logging.FileHandler(log_file_path)  # AND written to /Logs/app.log
      ]
  )
  # Rule: EVERY except block must call:
  #   self.logger.error("What failed: %s", e, exc_info=True)
  # exc_info=True prints full traceback to console AND file
  # NEVER write: except Exception: pass  ← this is forbidden

DRY_RUN PATTERN (every action function, without exception):
  DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'
  def execute(self, ...):
      if self.dry_run:
          self.logger.info("[DRY RUN] Would execute: %s with args %s",
                           self.__class__.__name__, locals())
          return {"status": "dry_run", "would_do": "..."}
      # real execution below

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 0 — Environment Setup (2-3 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [ ] Install Claude Code globally
      Command: npm install -g @anthropic/claude-code
      Verify : claude --version  (expect: 1.x.x or higher)
      If fail: check Node.js version first — needs v24+

- [ ] Install Node.js v24 LTS
      Download: https://nodejs.org
      Verify  : node --version   (expect: v24.x.x)
               npm --version    (expect: 10.x.x)

- [ ] Install Python 3.13+
      Download: https://python.org/downloads
      Verify  : python --version  (expect: Python 3.13.x)
      Windows : check "Add to PATH" during install

- [ ] Install PM2 globally
      Command: npm install -g pm2
      Verify : pm2 --version   (expect: 5.x.x or higher)

- [ ] Install UV (Python package manager)
      Command: pip install uv
      Verify : uv --version

- [ ] Initialize UV project
      Command: uv init personal-ai-employee
               cd personal-ai-employee

- [ ] Create .gitignore immediately (before any other file)
      Create file: .gitignore
      Contents must include:
        .env
        .claude/
        whatsapp_session/
        __pycache__/
        *.pyc
        *.pyo
        credentials.json
        *.log
      Verify: git add .gitignore && git commit -m "Add gitignore first"

- [ ] Create .env from template
      Create file: .env  (this file is in .gitignore — safe)
      Contents:
        GMAIL_CLIENT_ID=
        GMAIL_CLIENT_SECRET=
        GMAIL_CREDENTIALS=
        BANK_API_TOKEN=
        WHATSAPP_SESSION_PATH=
        DRY_RUN=true
        DEV_MODE=true
        VAULT_PATH=./AI_Employee_Vault
      Verify: cat .env (should show keys with empty values)
      CRITICAL: confirm .env is in .gitignore before filling values

- [ ] Verify specifyplus structure exists
      Command: ls -la  (should show CONSTITUTION.md, SPEC.md)
      If missing: run /sp.constitution and /sp.specify first

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 1 — Vault Foundation (2-3 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [ ] Create all vault folders in one command
      Mac/Linux: mkdir -p AI_Employee_Vault/{Inbox,Needs_Action,In_Progress/claude,Plans,Pending_Approval,Approved,Rejected,Done,Logs/pm2,Briefings,Accounting}
      Windows  : Create each folder manually in Explorer or via multiple mkdir commands
      Verify   : ls AI_Employee_Vault  (should show 11 folders)

- [ ] Write Dashboard.md
      Must contain:
        YAML frontmatter: last_updated, status: active
        ## System Status table (Component | Status | Last Check)
          Rows: Gmail Watcher 🔴 Not Started, WhatsApp Watcher 🔴 Not Started,
                Filesystem Watcher 🔴 Not Started, Orchestrator 🔴 Not Started,
                Watchdog 🔴 Not Started
        ## Pending Actions section (default: "_None_")
        ## This Week's Revenue table (MTD | Target | Status)
        ## Recent Activity section (default: "_No activity yet_")

- [ ] Write Company_Handbook.md
      Must contain exactly 10 numbered rules. Each rule:
        - Title in bold
        - 2-3 sentence explanation
        - Exact threshold if applicable (e.g., "> $50 requires approval")
      Rules must cover: email tone, payment thresholds, new contacts,
      social media, logging, uncertainty handling, WhatsApp keywords,
      file deletion policy, banking read-only rule, CEO briefing rule

- [ ] Write Business_Goals.md
      Must contain:
        YAML frontmatter: last_updated, review_frequency: weekly
        ## Q1 2026 Revenue Target (monthly goal, current MTD)
        ## KPI Table (Metric | Target | Alert Threshold) — min 3 rows
        ## Active Projects list
        ## Subscription Audit Rules (3 conditions that trigger flag)

- [ ] Test Claude reads vault
      Command: claude "Read Dashboard.md and print its full contents"
      Verify : Claude prints Dashboard.md content without errors
      If fail: check vault path, check claude is pointing to correct dir

- [ ] Test Claude writes vault
      Command: claude "Append '- TEST: write works' to Dashboard.md Recent Activity section, then remove it"
      Verify : File is temporarily modified then restored
      If fail: check file permissions on AI_Employee_Vault/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 2 — Python Project Structure (1-2 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [ ] Install all Python dependencies
      Command: uv add google-auth google-auth-oauthlib google-api-python-client \
                      playwright watchdog python-dotenv

- [ ] Install Playwright browser
      Command: playwright install chromium
      Verify : playwright --version

- [ ] Create project source structure
      Create these empty __init__.py files:
        src/__init__.py
        src/watchers/__init__.py
        src/actions/__init__.py
      Create src/config.py (Config dataclass — DRY: loaded once, passed everywhere):
        from dataclasses import dataclass
        from pathlib import Path
        import os
        from dotenv import load_dotenv
        load_dotenv()

        @dataclass
        class Config:
            vault_path: Path = Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
            dry_run: bool = os.getenv('DRY_RUN', 'true').lower() == 'true'
            dev_mode: bool = os.getenv('DEV_MODE', 'true').lower() == 'true'
            gmail_credentials: str = os.getenv('GMAIL_CREDENTIALS', '')
            whatsapp_session: str = os.getenv('WHATSAPP_SESSION_PATH', '')
            max_emails_per_hour: int = 10
            max_payments_per_hour: int = 3
            max_posts_per_day: int = 5
            ralph_max_iterations: int = 10

            def validate(self) -> None:
                """Validates config on startup. Raises ValueError with clear message."""
                if not self.vault_path.exists():
                    raise ValueError(f"[Config] VAULT_PATH does not exist: {self.vault_path}")
                if not self.dry_run and not self.gmail_credentials:
                    raise ValueError("[Config] GMAIL_CREDENTIALS required when DRY_RUN=false")

      Verify: python -c "from src.config import Config; c = Config(); c.validate(); print('Config OK')"

- [ ] Write src/actions/audit_logger.py (DRY: single logging class for entire system)
      Class: AuditLogger (use as singleton via module-level instance)
      Methods:
        __init__(self, config: Config)
          - Sets up Python logging: StreamHandler (console) + FileHandler (/Logs/app.log)
          - format: '%(asctime)s [%(name)s] %(levelname)s — %(message)s'
          - level: DEBUG in DEV_MODE, INFO in production
          - On init: delete log files older than 90 days in /Logs/

        log_action(self, action_type, actor, target, parameters={},
                   approval_status="pending", result="success", error=None) -> None
          - Builds JSON dict with all required fields + dry_run flag
          - Appends one JSON line to /Logs/YYYY-MM-DD.json
          - Also calls self.logger.info() so it appears in console
          - If result == "failure": self.logger.error(error, exc_info=False)

      Verify: python -c "
        from src.config import Config
        from src.actions.audit_logger import AuditLogger
        logger = AuditLogger(Config())
        logger.log_action('test', 'pytest', 'test_target', result='success')
        print('AuditLogger OK')
      "

- [ ] Write src/actions/retry_handler.py (DRY: decorator used by all external calls)
      Function: with_retry(max_attempts=3, base_delay=1, max_delay=60)
        - Returns decorator that wraps any function
        - On exception: logger.warning("Attempt N failed: <error>")
        - Delay: min(base_delay * 2^attempt, max_delay) seconds
        - On final failure: logger.error("All N attempts failed", exc_info=True)
        - Re-raises exception after final attempt
      Verify: write a test function that fails twice then succeeds,
              confirm retry_handler recovers it and logs correctly

- [ ] Write src/actions/rate_limiter.py (DRY: single rate limiter for all actions)
      Class: RateLimiter
        __init__(self, config: Config)
          - Loads/creates /Logs/rate_limits.json on startup
        check_and_increment(self, action_type: str) -> bool
          - Returns True if under limit, False if over limit
          - action_type maps to: email→max_emails_per_hour,
                                 payment→max_payments_per_hour,
                                 social_post→max_posts_per_day
          - Logs "[RateLimiter] Action BLOCKED — limit reached for <type>"
          - Logs "[RateLimiter] Action ALLOWED — <N>/<max> used"
      Verify: call check_and_increment 11 times for 'email', confirm 11th returns False

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 3 — Watcher Layer (4-6 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [ ] Write src/watchers/base_watcher.py
      Class: BaseWatcher(ABC)
        __init__(self, config: Config, check_interval: int)
          Sets: vault_path, needs_action path, dry_run, dev_mode, check_interval
          Creates: self.logger = logging.getLogger(self.__class__.__name__)
          Creates: self.audit = AuditLogger(config)  — DRY: shared logger
          Verifies: needs_action folder exists, creates if not
          Logs    : "[BaseWatcher] Initialized. DRY_RUN=%s, vault=%s"

        @abstractmethod
        check_for_updates(self) -> list:  """Return list of new items"""

        @abstractmethod
        create_action_file(self, item) -> Path:  """Write .md to /Needs_Action/"""

        run(self) -> None:
          self.logger.info("[%s] Starting poll loop (interval=%ds)",
                           self.__class__.__name__, self.check_interval)
          while True:
              try:
                  items = self.check_for_updates()
                  self.logger.debug("[%s] Found %d new items",
                                    self.__class__.__name__, len(items))
                  for item in items:
                      path = self.create_action_file(item)
                      self.logger.info("[%s] Created action file: %s",
                                       self.__class__.__name__, path)
              except KeyboardInterrupt:
                  self.logger.info("[%s] Stopped by user", self.__class__.__name__)
                  break
              except Exception as e:
                  self.logger.error("[%s] Unhandled error in poll loop: %s",
                                    self.__class__.__name__, e, exc_info=True)
              time.sleep(self.check_interval)

      Verify: confirm BaseWatcher cannot be instantiated (should raise TypeError)

- [ ] Setup Gmail API credentials (do this before writing GmailWatcher)
      Steps:
        1. Go to console.cloud.google.com
        2. Create project "personal-ai-employee"
        3. Enable Gmail API
        4. Create OAuth 2.0 credentials (Desktop app)
        5. Download credentials.json
        6. Save to a path OUTSIDE the vault (e.g., ~/.credentials/gmail.json)
        7. Update .env: GMAIL_CREDENTIALS=/absolute/path/to/gmail.json
      Verify: file exists at path, not inside AI_Employee_Vault/

- [ ] Write src/watchers/gmail_watcher.py
      Class: GmailWatcher(BaseWatcher)
        __init__(self, config: Config)
          - calls super().__init__(config, check_interval=120)
          - loads credentials from config.gmail_credentials
          - builds Gmail API service
          - initializes self.processed_ids = set()
          - if credentials file missing: raises FileNotFoundError with clear message
          - logs "[GmailWatcher] Connected to Gmail API"

        check_for_updates(self) -> list:
          - calls Gmail API: users().messages().list(userId='me', q='is:unread is:important')
          - filters out already-processed IDs
          - on HttpError 429 (rate limit): logger.warning + sleep 60s
          - on HttpError 401 (auth): logger.error + raise AuthenticationError
          - logs "[GmailWatcher] API returned %d messages, %d new"

        create_action_file(self, message) -> Path:
          - fetches full message details
          - extracts From, Subject from headers
          - builds YAML frontmatter (Schema A from SPEC.md)
          - if dry_run: logger.info("[DRY RUN] Would create EMAIL_%s.md", id)
                        return None
          - writes file to Needs_Action/EMAIL_<id>.md
          - adds id to processed_ids
          - calls audit.log_action('file_create', 'GmailWatcher', filepath)
          - returns filepath

        if __name__ == '__main__':
          config = Config()
          config.validate()
          watcher = GmailWatcher(config)
          watcher.run()

      Verify dry run:
        DRY_RUN=true python src/watchers/gmail_watcher.py
        Should print: "[GmailWatcher] Starting..." then poll messages
        Should NOT create any files in Needs_Action/

- [ ] Write src/watchers/whatsapp_watcher.py
      Class: WhatsAppWatcher(BaseWatcher)
        __init__(self, config: Config)
          - calls super().__init__(config, check_interval=30)
          - sets self.session_path = Path(config.whatsapp_session)
          - sets self.keywords = ['urgent','asap','invoice','payment','help','pricing']
          - logs "[WhatsAppWatcher] Session path: %s", session_path

        check_for_updates(self) -> list:
          - uses sync_playwright, launches persistent context
          - headless=False if session file doesn't exist (first run for QR scan)
          - headless=True after session exists
          - navigates to web.whatsapp.com
          - waits for chat list selector with 30s timeout
          - on TimeoutError: logger.error("[WhatsApp] Page load timeout", exc_info=True)
                             return []  (don't crash — degrade gracefully)
          - finds unread chats, filters by keywords
          - closes browser, returns filtered list
          - logs "[WhatsAppWatcher] Found %d keyword matches"

        create_action_file(self, message_data) -> Path:
          - builds YAML frontmatter (Schema A, type: whatsapp)
          - if dry_run: logger.info("[DRY RUN] Would create WHATSAPP_*.md") → return None
          - writes to Needs_Action/WHATSAPP_<contact>_<timestamp>.md
          - calls audit.log_action(...)
          - returns filepath

        if __name__ == '__main__':
          config = Config()
          config.validate()
          watcher = WhatsAppWatcher(config)
          watcher.run()

- [ ] Write src/watchers/filesystem_watcher.py
      Class: DropFolderHandler(FileSystemEventHandler) — uses watchdog library
        __init__(self, config: Config)
          - sets self.needs_action = config.vault_path / 'Needs_Action'
          - sets self.allowed_extensions = {'.pdf','.docx','.csv','.txt','.md'}
          - creates self.logger and self.audit
          - logs "[FilesystemWatcher] Monitoring: %s", inbox_path

        on_created(self, event):
          - if event.is_directory: return  (ignore folders)
          - source = Path(event.src_path)
          - if source.suffix not in allowed_extensions:
              logger.debug("[FilesystemWatcher] Ignoring file type: %s", source.suffix)
              return
          - if dry_run: logger.info("[DRY RUN] Would copy %s to Needs_Action/", source.name)
                        return
          - shutil.copy2(source, needs_action / f"FILE_{source.name}")
          - write sidecar .md with Schema A frontmatter (type: file_drop)
          - on PermissionError: logger.error("Cannot read %s", source, exc_info=True)
          - on shutil.Error: logger.error("Copy failed", exc_info=True)
                             write ALERT_filesystem_error.md to Needs_Action/
          - calls audit.log_action(...)

      if __name__ == '__main__':
        config = Config()
        config.validate()
        inbox = config.vault_path / 'Inbox'
        handler = DropFolderHandler(config)
        observer = Observer()
        observer.schedule(handler, str(inbox), recursive=False)
        observer.start()
        logger.info("[FilesystemWatcher] Observer started")
        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            logger.info("[FilesystemWatcher] Stopped")
        observer.join()

      Verify:
        DRY_RUN=true python src/watchers/filesystem_watcher.py &
        cp test.txt AI_Employee_Vault/Inbox/
        (should print "[DRY RUN] Would copy test.txt to Needs_Action/")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 4 — PM2 Process Management (1-2 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [ ] Write ecosystem.config.js
      module.exports = {
        apps: [
          {
            name: "gmail_watcher",
            script: "src/watchers/gmail_watcher.py",
            interpreter: "python3",
            autorestart: true,
            watch: false,
            env: { DRY_RUN: "true", VAULT_PATH: "./AI_Employee_Vault" },
            out_file: "AI_Employee_Vault/Logs/pm2/gmail-out.log",
            error_file: "AI_Employee_Vault/Logs/pm2/gmail-err.log"
          },
          {
            name: "whatsapp_watcher",
            script: "src/watchers/whatsapp_watcher.py",
            interpreter: "python3",
            autorestart: true, watch: false,
            env: { DRY_RUN: "true", VAULT_PATH: "./AI_Employee_Vault" },
            out_file: "AI_Employee_Vault/Logs/pm2/whatsapp-out.log",
            error_file: "AI_Employee_Vault/Logs/pm2/whatsapp-err.log"
          },
          {
            name: "filesystem_watcher",
            script: "src/watchers/filesystem_watcher.py",
            interpreter: "python3",
            autorestart: true, watch: false,
            env: { DRY_RUN: "true", VAULT_PATH: "./AI_Employee_Vault" },
            out_file: "AI_Employee_Vault/Logs/pm2/fs-out.log",
            error_file: "AI_Employee_Vault/Logs/pm2/fs-err.log"
          }
        ]
      }

- [ ] Start all watchers via PM2
      Command: pm2 start ecosystem.config.js
      Verify : pm2 list  (all 3 should show status: online)
      Check  : pm2 logs gmail_watcher --lines 20  (should show startup messages)

- [ ] Save PM2 state
      Command: pm2 save
               pm2 startup  (copy-paste the output command and run it)
      Verify : restart machine, run pm2 list — should auto-start

- [ ] Test resilience
      Command: pm2 stop gmail_watcher
               (wait 5 seconds)
               pm2 list  (should show gmail_watcher as online again — auto-restarted)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 5 — Orchestrator + Ralph Wiggum (3-4 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [ ] Write .claude/hooks/stop.py (Ralph Wiggum)
      (full implementation described in SPEC-005)
      After writing: verify hook is registered in Claude Code settings

- [ ] Configure MCP servers
      Create/update .claude/mcp.json
      (use exact JSON from SPEC-004)
      Replace /absolute/path/ with real paths on your machine
      Verify: claude mcp list  (should show filesystem, email, browser)

- [ ] Write src/orchestrator.py
      Class: Orchestrator
        __init__(self, config: Config)
          - sets vault paths, creates logger, audit, rate_limiter
          - logs "[Orchestrator] Starting. Vault: %s", config.vault_path

        build_task_prompt(self, task_file: Path) -> str:
          - reads task file contents
          - returns formatted prompt:
            "You are the AI Employee. Process this task:
             File: {task_file}
             Contents: {contents}
             Instructions:
             1. Read Company_Handbook.md for applicable rules
             2. Create /Plans/PLAN_{taskname}.md with objective and steps
             3. If external action needed: create /Pending_Approval/{TYPE}_{task}.md
             4. Move task file to /Done/ ONLY when fully resolved
             5. Append one line to Dashboard.md under Recent Activity
             6. Output <promise>TASK_COMPLETE</promise> when done
             DRY_RUN={dry_run} — no real API calls if True"

        process_task(self, task_file: Path) -> None:
          - moves file to In_Progress/claude/ (claim-by-move — prevents double work)
          - sets env: TASK_FILE=task_file, RALPH_COUNTER=0
          - calls: subprocess.run(["claude", "--print", prompt])
          - logs result: "[Orchestrator] Task %s complete" or "[ERROR] Task failed"
          - on subprocess error: logger.error(..., exc_info=True)

        watch_needs_action(self) -> None:
          - uses watchdog Observer on /Needs_Action/
          - on new .md file: calls self.process_task(filepath)
          - logs "[Orchestrator] New task detected: %s"

        watch_approved(self) -> None:
          - uses watchdog Observer on /Approved/
          - on new .md file: reads action type from YAML frontmatter
          - calls appropriate MCP action via Claude
          - logs "[Orchestrator] Approved action triggered: %s"

        start(self) -> None:
          - starts both watchdog observers
          - logs "[Orchestrator] Watching Needs_Action/ and Approved/"
          - runs forever (KeyboardInterrupt → graceful shutdown)

      if __name__ == '__main__':
        config = Config()
        config.validate()
        orch = Orchestrator(config)
        orch.start()

- [ ] End-to-end dry run test
      Step 1: Start orchestrator: DRY_RUN=true python src/orchestrator.py
      Step 2: Create test task:
              echo "---
              type: email
              from: test@example.com
              subject: Test task
              received: 2026-01-07T10:00:00Z
              priority: high
              status: pending
              ---
              ## Content
              Test email for dry run" > AI_Employee_Vault/Needs_Action/TEST_001.md
      Step 3: Watch console — should show:
              "[Orchestrator] New task detected: TEST_001.md"
              "[Orchestrator] Moving to In_Progress/claude/"
              Claude processing output...
              "[Ralph] Attempt 1/10 — retrying..." OR "[Ralph] Task complete ✅"
      Step 4: Verify Plans/ has PLAN_TEST_001.md
      Step 5: Verify Pending_Approval/ has approval request
      Step 6: Move approval to Approved/ — verify Orchestrator detects it
      Step 7: Verify Done/ has TEST_001.md
      Step 8: Verify Logs/ has today's JSON with all entries

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 6 — Watchdog Process (1-2 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [ ] Write src/watchdog_monitor.py
      (separate from Python's built-in watchdog library)
      Class: ProcessMonitor
        PROCESSES = {
            'gmail_watcher': 'python src/watchers/gmail_watcher.py',
            'filesystem_watcher': 'python src/watchers/filesystem_watcher.py',
            'orchestrator': 'python src/orchestrator.py'
        }
        __init__(self, config: Config)
          - creates logger, audit
          - logs "[ProcessMonitor] Monitoring %d processes", len(PROCESSES)

        is_running(self, name: str) -> bool:
          - checks /tmp/{name}.pid file
          - reads PID, checks if process exists (os.kill(pid, 0))
          - on ProcessLookupError: return False (process is dead)
          - on FileNotFoundError: return False (PID file missing)

        restart_process(self, name: str, cmd: str) -> None:
          - logs "[ProcessMonitor] %s not running — restarting...", name
          - subprocess.Popen(cmd.split(), ...)
          - writes new PID to /tmp/{name}.pid
          - creates alert: Needs_Action/ALERT_{name}_restarted.md
          - calls audit.log_action('process_restart', 'ProcessMonitor', name)

        run(self) -> None:
          - loops every 60 seconds
          - for each process: if not is_running → restart_process
          - logs "[ProcessMonitor] Health check OK" when all running
          - KeyboardInterrupt → logs "Stopping ProcessMonitor"

- [ ] Add ProcessMonitor to ecosystem.config.js
      Add as 4th app entry: watchdog_monitor, script: src/watchdog_monitor.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 7 — CEO Briefing + LinkedIn (3-4 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [ ] Write src/briefing_generator.py
      Class: BriefingGenerator
        __init__(self, config: Config)
          - sets paths, logger, audit

        get_done_tasks_this_week(self) -> list[dict]:
          - scans /Done/ folder
          - filters files modified in last 7 days
          - parses YAML frontmatter from each
          - returns list of task dicts
          - logs "[BriefingGenerator] Found %d completed tasks this week"

        get_revenue(self) -> dict:
          - reads Accounting/Current_Month.md
          - extracts revenue figures (simple text parsing)
          - returns: {mtd, target, trend}

        check_subscriptions(self, transactions: list) -> list[dict]:
          PATTERNS = {
              'netflix.com': 'Netflix', 'spotify.com': 'Spotify',
              'adobe.com': 'Adobe CC', 'notion.so': 'Notion',
              'slack.com': 'Slack'
          }
          - matches transaction descriptions against PATTERNS
          - returns list of flagged subscriptions

        generate(self) -> Path:
          - calls get_done_tasks_this_week(), get_revenue()
          - builds briefing markdown content (all 6 required sections)
          - writes to /Briefings/YYYY-MM-DD_Monday_Briefing.md
          - calls audit.log_action('briefing_generated', ...)
          - logs "[BriefingGenerator] Briefing written to %s"
          - if dry_run: logs "[DRY RUN] Would generate briefing" → return None

      if __name__ == '__main__':
        config = Config()
        config.validate()
        gen = BriefingGenerator(config)
        gen.generate()

- [ ] Setup Sunday 11PM trigger
      Mac/Linux: crontab -e → add: 0 23 * * 0 cd /path/to/project && python src/briefing_generator.py
      Windows  : Task Scheduler → New Task → Weekly → Sunday → 23:00 → Action: python src/briefing_generator.py

- [ ] Test briefing manually
      Command: python src/briefing_generator.py
      Verify : /Briefings/ contains YYYY-MM-DD_Monday_Briefing.md with all 6 sections

- [ ] Write src/actions/linkedin_poster.py
      Class: LinkedInPoster(BaseAction)  ← OOP: extends BaseAction
        post_draft(self, content: str, title: str) -> Path:
          - creates /Pending_Approval/LINKEDIN_<timestamp>.md (Schema C)
          - logs "[LinkedInPoster] Draft created — awaiting approval"
          - returns approval file path

        execute_post(self, approved_file: Path) -> None:
          - reads approved file content
          - if dry_run: logger.info("[DRY RUN] Would post to LinkedIn: %s", title)
                        return
          - uses browser-mcp to navigate LinkedIn and post
          - on failure: logger.error("[LinkedInPoster] Post failed", exc_info=True)
          - on success: move approved_file to /Done/, log action

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 8 — Documentation & Submission (2-3 hours)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- [ ] Write README.md with: architecture overview, setup steps (exact commands),
      env vars table, ASCII architecture diagram, tier declaration: SILVER,
      demo video link

- [ ] Write SECURITY.md with: .gitignore list, DRY_RUN explanation,
      credential storage approach, HITL boundaries

- [ ] Record 5-10 min demo video: show full invoice request flow end-to-end

- [ ] Submit: https://forms.gle/JR9T1SJq5rmQyGkGA

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT INSTRUCTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Write PLAN.md to project root with all 8 phases.
Use [ ] checkboxes for every task.
After writing: print "✅ PLAN.md written — [8] phases, [X] total tasks"
```

================================================================================
# PROMPT 4 — /sp.tasks
# Seedha Claude Code terminal mein paste karo
# Kya karega: TASKS.md file likhega — 100 granular executable tasks
================================================================================

```
You are a senior developer. Write TASKS.md to the project root.
Generate exactly 100 tasks (TASK-001 to TASK-100).
Every task must be immediately actionable — no vague descriptions.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MANDATORY TASK FORMAT — use for EVERY single task
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

### TASK-XXX: <verb + what>
- **Priority**: P0 | P1 | P2 | P3
- **Estimate**: X min | X hrs
- **Depends on**: TASK-XXX (or "none")
- **File(s)**: exact paths to create or modify
- **Command**: exact terminal command (or "manual step")
- **Done when**: one specific testable sentence
- **Debug check**: what to look for in console to confirm it works

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CODING RULES TO EMBED IN TASK DESCRIPTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
When generating tasks that involve writing code, include these rules:

DRY:  "Do not repeat: use Config class from src/config.py,
       AuditLogger from src/actions/audit_logger.py,
       RetryHandler from src/actions/retry_handler.py"

OOP:  "Extend BaseWatcher / BaseAction — do not copy logic"

DEBUG:"Every file must have:
       logging.basicConfig with StreamHandler + FileHandler
       Every except block: logger.error('...', exc_info=True)
       No bare except: pass anywhere in codebase"

DRY_RUN: "Every action function must check:
          if self.dry_run: logger.info('[DRY RUN] Would do X'); return"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
GENERATE TASKS FOR THESE GROUPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

GROUP A — SETUP (TASK-001 to TASK-010): 10 tasks
  Install tools, create .gitignore, create .env, init git,
  init UV project, verify all tool versions, run specifyplus init

GROUP B — VAULT (TASK-011 to TASK-020): 10 tasks
  Create all 11 folders, write Dashboard.md, Company_Handbook.md,
  Business_Goals.md, verify Claude reads vault, verify Claude writes vault

GROUP C — CONFIG & SHARED UTILITIES (TASK-021 to TASK-030): 10 tasks
  Create src/config.py Config dataclass,
  Create src/actions/audit_logger.py AuditLogger class,
  Create src/actions/retry_handler.py with_retry decorator,
  Create src/actions/rate_limiter.py RateLimiter class,
  Create src/__init__.py and src/actions/__init__.py and src/watchers/__init__.py,
  Test each utility independently via python -c "..." one-liners

GROUP D — BASE WATCHER (TASK-031 to TASK-036): 6 tasks
  Write src/watchers/base_watcher.py BaseWatcher ABC,
  verify cannot be instantiated, verify run() loop logs to console,
  verify run() catches exceptions without crashing

GROUP E — GMAIL WATCHER (TASK-037 to TASK-046): 10 tasks
  Setup Google Cloud Console project,
  Enable Gmail API,
  Create OAuth credentials,
  Download credentials.json to safe location outside vault,
  Update .env with GMAIL_CREDENTIALS path,
  Write src/watchers/gmail_watcher.py GmailWatcher(BaseWatcher),
  Test dry run (no files created),
  Test live mode (files appear in Needs_Action/),
  Verify error handling when credentials missing,
  Verify deduplication (same email not processed twice)

GROUP F — WHATSAPP WATCHER (TASK-047 to TASK-054): 8 tasks
  Write src/watchers/whatsapp_watcher.py WhatsAppWatcher(BaseWatcher),
  Run first-time headless=False to scan QR code and save session,
  Verify session saved at WHATSAPP_SESSION_PATH,
  Test dry run,
  Test keyword filter (only flagged messages create files),
  Verify TimeoutError handled gracefully (returns [] not crash),
  Verify browser crash handled gracefully (restarts browser)

GROUP G — FILESYSTEM WATCHER (TASK-055 to TASK-060): 6 tasks
  Write src/watchers/filesystem_watcher.py DropFolderHandler,
  Test: drop allowed file (.pdf) in Inbox/ → appears in Needs_Action/,
  Test: drop disallowed file (.exe) → NOT copied (ignored silently),
  Test: dry run → "[DRY RUN]" printed, no files copied,
  Verify PermissionError logged not crashed

GROUP H — PM2 CONFIG (TASK-061 to TASK-067): 7 tasks
  Write ecosystem.config.js with 4 apps,
  Run pm2 start ecosystem.config.js,
  Verify pm2 list shows all 4 online,
  Verify pm2 logs show startup messages,
  Run pm2 save,
  Run pm2 startup (and execute the generated command),
  Test resilience: kill one process, verify PM2 restarts it

GROUP I — RALPH WIGGUM HOOK (TASK-068 to TASK-073): 6 tasks
  Write .claude/hooks/stop.py,
  Register hook in Claude Code settings,
  Test task completes in 1 iteration (file moved to Done/ before hook fires),
  Test hook fires and retries when file NOT in Done/,
  Test max 10 iterations creates ALERT_*.md in Needs_Action/,
  Verify counter resets between separate tasks

GROUP J — ORCHESTRATOR (TASK-074 to TASK-082): 9 tasks
  Write src/orchestrator.py Orchestrator class,
  Configure .claude/mcp.json with 3 servers,
  Test: manual file in Needs_Action/ → Orchestrator detects and triggers Claude,
  Verify: In_Progress/claude/ shows claimed file,
  Verify: Plans/ shows PLAN_*.md,
  Verify: Pending_Approval/ shows approval request,
  Test: move approval to Approved/ → Orchestrator detects,
  Verify: Done/ shows completed task,
  Verify: Logs/ shows full JSON audit trail

GROUP K — PROCESS MONITOR (TASK-083 to TASK-087): 5 tasks
  Write src/watchdog_monitor.py ProcessMonitor class,
  Add to ecosystem.config.js as 4th app,
  Test: kill a watcher → monitor restarts it + creates ALERT_*.md,
  Verify: ALERT_*.md appears in Needs_Action/ within 60s,
  Verify: monitor logs "[ProcessMonitor] Health check OK" every 60s

GROUP L — CEO BRIEFING (TASK-088 to TASK-093): 6 tasks
  Write src/briefing_generator.py BriefingGenerator class,
  Test with sample data: python src/briefing_generator.py,
  Verify: Briefings/ contains correct .md with all 6 sections,
  Setup Sunday 11PM cron/Task Scheduler trigger,
  Verify: dry run prints "[DRY RUN] Would generate briefing",
  Write src/actions/audit_logic.py subscription pattern checker

GROUP M — LINKEDIN (TASK-094 to TASK-097): 4 tasks
  Write src/actions/linkedin_poster.py LinkedInPoster(BaseAction),
  Test: post_draft() creates approval file in Pending_Approval/,
  Test: after approval, execute_post() dry run logs "[DRY RUN]",
  Test: after approval, execute_post() live mode posts to LinkedIn

GROUP N — DOCUMENTATION & SUBMISSION (TASK-098 to TASK-100): 3 tasks
  Write README.md + SECURITY.md,
  Record 5-10 min demo video,
  Submit via https://forms.gle/JR9T1SJq5rmQyGkGA

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OUTPUT INSTRUCTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Write TASKS.md to project root.
Exactly 100 tasks (TASK-001 to TASK-100) using the mandatory format above.
Add a summary table at top: Group | Range | Count | Est Hours
After writing: print "✅ TASKS.md written — 100 tasks across 14 groups"
```

================================================================================
# PROMPT 5 — /sp.implement
# Seedha Claude Code terminal mein paste karo
# Kya karega: Poora system implement karega — code likhega, test karega
# IMPORTANT: project root folder se run karo
================================================================================

```
You are Claude Code — an autonomous implementer. Your job is to write,
test, and verify every file of the Personal AI Employee system.

WORKING DIRECTORY: current directory (project root where you are running)
READ FIRST: CONSTITUTION.md, SPEC.md, PLAN.md, TASKS.md
If any of these are missing, tell me which ones before proceeding.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ABSOLUTE CODING RULES — violating these = implementation failure
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RULE 1 — DRY (Don't Repeat Yourself):
  ✗ WRONG: Copy-paste logging setup in every file
  ✓ RIGHT: logging configured once in AuditLogger, imported everywhere
  ✗ WRONG: Check DRY_RUN in 10 different places with different logic
  ✓ RIGHT: self.dry_run set once in BaseWatcher.__init__, used everywhere
  ✗ WRONG: Config values read from os.getenv() scattered across files
  ✓ RIGHT: Config dataclass in src/config.py, passed to every class

RULE 2 — OOP (Object-Oriented Programming):
  ✗ WRONG: Three separate watcher files with duplicated while True loop
  ✓ RIGHT: BaseWatcher(ABC) has run() loop; subclasses override check_for_updates()
  ✗ WRONG: Logging code repeated in GmailWatcher, WhatsAppWatcher, FilesystemWatcher
  ✓ RIGHT: self.logger = logging.getLogger(self.__class__.__name__) in BaseWatcher
  ✗ WRONG: AuditLogger instantiated multiple times across files
  ✓ RIGHT: AuditLogger created once, passed as dependency to every class

RULE 3 — DEBUGGING (errors must be visible in console AND in log file):
  ✗ WRONG: except Exception as e: pass
  ✗ WRONG: except Exception as e: print(e)
  ✓ RIGHT: except Exception as e: self.logger.error("What failed: %s", e, exc_info=True)
  exc_info=True prints full traceback to console AND /Logs/app.log
  Every file must configure both StreamHandler AND FileHandler:
    handlers=[logging.StreamHandler(), logging.FileHandler(log_path)]

RULE 4 — DRY_RUN safety (no real API calls during dev/testing):
  ✗ WRONG: if os.getenv('DRY_RUN') == 'true': (checked differently each time)
  ✓ RIGHT: self.dry_run = config.dry_run (set once via Config, used everywhere)
  Every action function:
    if self.dry_run:
        self.logger.info("[DRY RUN] %s would: %s", self.__class__.__name__, description)
        return None  # or return {"status": "dry_run"}
    # real code below

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPLEMENT IN THIS EXACT ORDER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

══ STEP 1: Verify tools ══
Run and show output of:
  claude --version
  python --version
  node --version
  pm2 --version
  uv --version
If any missing: stop and list what needs to be installed.

══ STEP 2: Create vault + gitignore ══
Create .gitignore with: .env, .claude/, whatsapp_session/,
  __pycache__/, *.pyc, *.pyo, credentials.json, *.log
Create vault structure:
  mkdir -p AI_Employee_Vault/{Inbox,Needs_Action,In_Progress/claude,Plans,Pending_Approval,Approved,Rejected,Done,Logs/pm2,Briefings,Accounting}
Verify: show ls output of AI_Employee_Vault/

══ STEP 3: Write vault markdown files ══

Write AI_Employee_Vault/Dashboard.md:
---
last_updated: <current timestamp>
status: active
---
# AI Employee Dashboard

## System Status
| Component           | Status              | Last Check |
|---------------------|---------------------|------------|
| Gmail Watcher       | 🔴 Not Started      | -          |
| WhatsApp Watcher    | 🔴 Not Started      | -          |
| Filesystem Watcher  | 🔴 Not Started      | -          |
| Orchestrator        | 🔴 Not Started      | -          |
| Process Monitor     | 🔴 Not Started      | -          |

## Pending Actions
_None_

## This Week's Revenue
| Metric   | Value | Target  | Status       |
|----------|-------|---------|--------------|
| MTD      | $0    | $10,000 | 🔴 0%        |

## Recent Activity
_No activity yet_

Write AI_Employee_Vault/Company_Handbook.md with EXACTLY these 10 rules:
# Company Handbook — Rules of Engagement for AI Employee

**Rule 1 — Email Tone and Response Time**
Reply to all known client emails within 24 hours. Always use polite,
professional language. Never use informal slang in client communication.

**Rule 2 — Payment Approval (no exceptions)**
Flag ALL payments for human approval before executing. There is no
auto-approve threshold for payments. Write to /Pending_Approval/ and wait.

**Rule 3 — New Contact Protocol**
Never send any communication to a new (unknown) contact without explicit
human approval. Unknown = not in previous email/WhatsApp history.

**Rule 4 — Social Media Approval Gate**
All social media posts (LinkedIn, Twitter/X, Facebook, Instagram) must be
drafted, placed in /Pending_Approval/, approved, then posted. Never post directly.

**Rule 5 — Log Every Action**
Every external action (email, payment, post, file move to Done/) must produce
a JSON entry in /Vault/Logs/YYYY-MM-DD.json. Silent actions are forbidden.

**Rule 6 — When Uncertain: Escalate Don't Guess**
If a task has no applicable rule in this handbook, write an approval request
to /Pending_Approval/ explaining the uncertainty. Never guess on sensitive tasks.

**Rule 7 — WhatsApp Keyword Escalation**
Immediately flag any WhatsApp message containing: urgent, asap, invoice,
payment, help, pricing. Create Needs_Action file within 30 seconds.

**Rule 8 — File Deletion Forbidden**
Never delete any file. Move to /Rejected/ (if declined) or /Done/ (if complete).
The only files Claude may delete are temporary state files in /tmp/.

**Rule 9 — Banking is Read-Only**
AI Employee may read and report bank transactions. It may never initiate,
authorize, or execute any financial transaction autonomously.

**Rule 10 — CEO Briefing is Non-Negotiable**
Generate the Monday CEO Briefing every Sunday at 11 PM without exception.
If data is incomplete, generate with available data and note what is missing.

Write AI_Employee_Vault/Business_Goals.md:
---
last_updated: <today's date>
review_frequency: weekly
---
# Business Goals — Q1 2026

## Revenue Target
- Monthly goal: $10,000
- Current MTD: $0

## Key Performance Indicators
| Metric                  | Target      | Alert Threshold |
|-------------------------|-------------|-----------------|
| Client response time    | < 24 hours  | > 48 hours      |
| Invoice payment rate    | > 90%       | < 80%           |
| Monthly software costs  | < $500      | > $600          |

## Active Projects
_(Add your projects here)_

## Subscription Audit Rules
Flag any subscription for review if:
1. No login or usage in the past 30 days
2. Cost increased more than 20% since last month
3. Duplicate functionality with another tool already in use

══ STEP 4: Create Python project structure ══

Create these files (empty __init__.py files):
  src/__init__.py
  src/watchers/__init__.py
  src/actions/__init__.py

Create .env file:
  # .env — NEVER commit this file
  GMAIL_CLIENT_ID=
  GMAIL_CLIENT_SECRET=
  GMAIL_CREDENTIALS=
  BANK_API_TOKEN=
  WHATSAPP_SESSION_PATH=
  DRY_RUN=true
  DEV_MODE=true
  VAULT_PATH=./AI_Employee_Vault

Install dependencies:
  uv add google-auth google-auth-oauthlib google-api-python-client playwright watchdog python-dotenv
  playwright install chromium

══ STEP 5: Write src/config.py ══
Write this complete file — DRY: single Config object used everywhere:

"""Configuration for Personal AI Employee. Loaded once, passed everywhere."""
import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

@dataclass
class Config:
    vault_path: Path = field(
        default_factory=lambda: Path(os.getenv('VAULT_PATH', './AI_Employee_Vault'))
    )
    dry_run: bool = field(
        default_factory=lambda: os.getenv('DRY_RUN', 'true').lower() == 'true'
    )
    dev_mode: bool = field(
        default_factory=lambda: os.getenv('DEV_MODE', 'true').lower() == 'true'
    )
    gmail_credentials: str = field(
        default_factory=lambda: os.getenv('GMAIL_CREDENTIALS', '')
    )
    whatsapp_session: str = field(
        default_factory=lambda: os.getenv('WHATSAPP_SESSION_PATH', '')
    )
    max_emails_per_hour: int = 10
    max_payments_per_hour: int = 3
    max_posts_per_day: int = 5
    ralph_max_iterations: int = 10

    def validate(self) -> None:
        """Validate config on startup. Raises ValueError with a clear message."""
        errors = []
        if not self.vault_path.exists():
            errors.append(f"VAULT_PATH does not exist: {self.vault_path}")
        if not self.dry_run and not self.gmail_credentials:
            errors.append("GMAIL_CREDENTIALS required when DRY_RUN=false")
        if not self.dry_run and not self.whatsapp_session:
            errors.append("WHATSAPP_SESSION_PATH required when DRY_RUN=false")
        if errors:
            for e in errors:
                logger.error("[Config] Validation failed: %s", e)
            raise ValueError(f"Config errors: {'; '.join(errors)}")
        logger.info("[Config] Validation OK. DRY_RUN=%s, VAULT=%s",
                    self.dry_run, self.vault_path)

After writing, verify:
  python -c "from src.config import Config; c = Config(); c.validate(); print('Config OK')"
  Console must show: "[Config] Validation OK. DRY_RUN=True, VAULT=..."

══ STEP 6: Write src/actions/audit_logger.py ══
Write this complete file — DRY: single logging authority for entire system:

"""
AuditLogger: Single source of truth for all logging.
Writes to console AND /Vault/Logs/YYYY-MM-DD.json simultaneously.
Import and use this everywhere — never configure logging separately.
"""
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from src.config import Config


class AuditLogger:
    """Handles all audit logging. Use one instance per process."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.logs_dir = config.vault_path / 'Logs'
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()
        self._cleanup_old_logs()
        self.logger = logging.getLogger('AuditLogger')
        self.logger.info("[AuditLogger] Initialized. Logs dir: %s", self.logs_dir)

    def _setup_logging(self) -> None:
        """Configure root logger: console + file. Called once on init."""
        log_level = logging.DEBUG if self.config.dev_mode else logging.INFO
        log_file = self.logs_dir / 'app.log'

        logging.basicConfig(
            level=log_level,
            format='%(asctime)s [%(name)s] %(levelname)s — %(message)s',
            handlers=[
                logging.StreamHandler(),          # Always visible in console
                logging.FileHandler(log_file),    # Always written to file
            ]
        )

    def _cleanup_old_logs(self) -> None:
        """Delete JSON log files older than 90 days."""
        cutoff = datetime.now(timezone.utc).timestamp() - (90 * 24 * 3600)
        for log_file in self.logs_dir.glob('*.json'):
            if log_file.stat().st_mtime < cutoff:
                log_file.unlink()
                logging.getLogger('AuditLogger').info(
                    "[AuditLogger] Deleted old log: %s", log_file.name
                )

    def log_action(
        self,
        action_type: str,
        actor: str,
        target: str,
        parameters: dict[str, Any] | None = None,
        approval_status: str = 'pending',
        result: str = 'success',
        error: str | None = None,
    ) -> None:
        """Log one action. Writes to console + /Logs/YYYY-MM-DD.json."""
        logger = logging.getLogger('AuditLogger')
        entry = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'action_type': action_type,
            'actor': actor,
            'target': target,
            'parameters': parameters or {},
            'approval_status': approval_status,
            'approved_by': 'human' if approval_status == 'human_approved' else 'system',
            'result': result,
            'error': error,
            'dry_run': self.config.dry_run,
        }
        # Write to daily JSON log
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_dir / f'{today}.json'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')

        # Also log to console/app.log
        if result == 'failure':
            logger.error("[Audit] %s by %s on %s — FAILED: %s",
                         action_type, actor, target, error)
        else:
            logger.info("[Audit] %s by %s on %s — %s", action_type, actor, target, result)

After writing, verify:
  python -c "
from src.config import Config
from src.actions.audit_logger import AuditLogger
al = AuditLogger(Config())
al.log_action('test_action', 'pytest', 'test_target', result='success')
print('AuditLogger OK — check Logs/ for JSON entry')
"
  Console must show: "[AuditLogger] Initialized..." and "[Audit] test_action..."

══ STEP 7: Write src/actions/retry_handler.py ══
Write this complete file:

"""
RetryHandler: Exponential backoff decorator for all external API calls.
DRY: Apply @with_retry to any function that calls an external service.
"""
import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


def with_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,),
) -> Callable:
    """
    Decorator: retry function with exponential backoff on failure.
    Usage: @with_retry(max_attempts=3, base_delay=1, max_delay=60)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error = None
            for attempt in range(max_attempts):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info("[Retry] %s succeeded on attempt %d",
                                    func.__name__, attempt + 1)
                    return result
                except exceptions as e:
                    last_error = e
                    if attempt == max_attempts - 1:
                        logger.error(
                            "[Retry] %s failed after %d attempts: %s",
                            func.__name__, max_attempts, e,
                            exc_info=True  # full traceback in console
                        )
                        raise
                    delay = min(base_delay * (2 ** attempt), max_delay)
                    logger.warning(
                        "[Retry] %s attempt %d/%d failed: %s. Retrying in %.1fs...",
                        func.__name__, attempt + 1, max_attempts, e, delay
                    )
                    time.sleep(delay)
        return wrapper
    return decorator

══ STEP 8: Write src/actions/rate_limiter.py ══
Write complete RateLimiter class:
  - loads/saves counters from /Logs/rate_limits.json
  - check_and_increment(action_type) → bool
  - resets hourly counters every 3600s, daily counters every 86400s
  - logs "[RateLimiter] ALLOWED email 3/10" or "[RateLimiter] BLOCKED email — limit reached"
  - no bare except blocks — all exceptions logged with exc_info=True

══ STEP 9: Write src/watchers/base_watcher.py ══
Write complete BaseWatcher(ABC) class:
  - __init__ receives Config and check_interval
  - creates self.audit = AuditLogger(config) — DRY: shared
  - creates self.rate_limiter = RateLimiter(config) — DRY: shared
  - logs startup with dry_run status
  - run() loop: catches all exceptions with exc_info=True, never crashes
  - abstract: check_for_updates() and create_action_file()
  After writing, verify: python -c "from src.watchers.base_watcher import BaseWatcher; print('OK')"

══ STEP 10: Write src/watchers/gmail_watcher.py ══
Write complete GmailWatcher(BaseWatcher):
  - __init__: loads Gmail API, logs connection status
  - check_for_updates: applies @with_retry decorator
  - create_action_file: writes YAML Schema A frontmatter
  - DRY_RUN: "[DRY RUN] Would create EMAIL_<id>.md" — no file written
  - All exceptions: logger.error(..., exc_info=True)
  - if __name__ == '__main__': Config().validate() then watcher.run()

══ STEP 11: Write src/watchers/whatsapp_watcher.py ══
Write complete WhatsAppWatcher(BaseWatcher):
  - headless=False first run (QR scan), True after session exists
  - TimeoutError → return [] gracefully (log warning, not error)
  - Browser crash → relaunch browser, log error with traceback
  - Keyword filter applied before creating any file
  - DRY_RUN guard in create_action_file

══ STEP 12: Write src/watchers/filesystem_watcher.py ══
Write complete DropFolderHandler(FileSystemEventHandler):
  - Only allowed extensions: {'.pdf', '.docx', '.csv', '.txt', '.md'}
  - PermissionError → log error, continue (don't crash)
  - shutil.Error → log error + create ALERT_*.md in Needs_Action/
  - DRY_RUN: log "[DRY RUN] Would copy <file>" — no actual copy
  - if __name__ == '__main__': Observer pattern, KeyboardInterrupt handled

══ STEP 13: Write src/orchestrator.py ══
Write complete Orchestrator class:
  - claim-by-move: move task to In_Progress/claude/ before processing
  - build_task_prompt(): includes DRY_RUN status in prompt
  - process_task(): subprocess.run with error capture + logging
  - watch_needs_action() and watch_approved(): separate watchdog Observers
  - All exceptions: logger.error(..., exc_info=True) — never silent
  - if __name__ == '__main__': Config().validate() then orch.start()

══ STEP 14: Write .claude/hooks/stop.py ══
Write complete Ralph Wiggum hook:
  - reads TASK_FILE and RALPH_COUNTER from environment
  - checks if task file exists in /Done/
  - at iteration 10: creates ALERT_ralph_max_<task>.md in /Needs_Action/
  - logs every iteration to console: "[Ralph] Attempt N/10"
  - all file operations in try/except with logging

══ STEP 15: Write ecosystem.config.js ══
Write complete PM2 config with 4 apps:
  gmail_watcher, whatsapp_watcher, filesystem_watcher, watchdog_monitor
  All with: autorestart:true, error_file and out_file pointing to /Logs/pm2/

══ STEP 16: Write src/watchdog_monitor.py ══
Write complete ProcessMonitor class:
  - monitors 3 processes via PID files
  - restart_process() creates ALERT_*.md in Needs_Action/
  - logs "[ProcessMonitor] Health check OK" when all running
  - runs every 60 seconds with graceful KeyboardInterrupt

══ STEP 17: Write src/briefing_generator.py ══
Write complete BriefingGenerator class:
  - get_done_tasks_this_week(): filter /Done/ by modification date
  - get_revenue(): parse Accounting/Current_Month.md
  - check_subscriptions(): SUBSCRIPTION_PATTERNS dict matching
  - generate(): produces all 6 briefing sections
  - DRY_RUN: logs "[DRY RUN] Would generate briefing" → return None
  - if __name__ == '__main__': Config().validate() then gen.generate()

══ STEP 18: Run all verification tests ══

TEST A — Vault read/write:
  claude "Read Dashboard.md and print its full contents"
  Expected console: full Dashboard.md content

TEST B — Filesystem watcher dry run:
  DRY_RUN=true python src/watchers/filesystem_watcher.py &
  cp /tmp/test.txt AI_Employee_Vault/Inbox/
  Expected console: "[DRY RUN] Would copy test.txt to Needs_Action/"

TEST C — Gmail watcher dry run:
  DRY_RUN=true python src/watchers/gmail_watcher.py
  Expected console: "[GmailWatcher] Starting poll loop..."
  Expected: NO files in Needs_Action/

TEST D — Config validation:
  python -c "from src.config import Config; Config().validate(); print('PASS')"
  Expected console: "[Config] Validation OK..."

TEST E — AuditLogger:
  python -c "
from src.config import Config
from src.actions.audit_logger import AuditLogger
al = AuditLogger(Config())
al.log_action('test', 'test_actor', 'test_target', result='success')
import json, datetime
log = open(f'AI_Employee_Vault/Logs/{datetime.date.today()}.json').readlines()
print('Log entries:', len(log))
assert len(log) > 0, 'FAIL: no log entries'
print('PASS')
"

TEST F — End-to-end orchestrator dry run:
  Step 1: DRY_RUN=true python src/orchestrator.py &
  Step 2: Write test task to Needs_Action/ (YAML frontmatter, type: email)
  Step 3: Watch console — expect:
    "[Orchestrator] New task detected"
    Claude processing output
    "[Ralph] Attempt 1/10" or "[Ralph] Task complete"
  Step 4: ls Plans/     → expect PLAN_*.md
  Step 5: ls Done/      → expect task moved there
  Step 6: cat AI_Employee_Vault/Logs/YYYY-MM-DD.json → expect JSON entries

TEST G — Rate limiter:
  python -c "
from src.config import Config
from src.actions.rate_limiter import RateLimiter
rl = RateLimiter(Config())
results = [rl.check_and_increment('email') for _ in range(12)]
assert results[9] == True,  'FAIL: 10th should be allowed'
assert results[10] == False, 'FAIL: 11th should be blocked'
print('RateLimiter PASS')
"

══ STEP 19: Start with PM2 ══
  pm2 start ecosystem.config.js
  pm2 list   (verify all 4 show "online")
  pm2 logs   (verify startup messages appear for each)
  pm2 save
  pm2 startup  (run the generated command)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AFTER EACH STEP PRINT THIS REPORT FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ STEP N — <step name>
   Files created   : [list of file paths]
   Commands run    : [list of commands]
   Console output  : [key lines from console showing it worked]
   Test result     : PASS ✅ / FAIL ❌
   ⚠️  Issues found : [if any — what failed and how fixed]
   DRY_RUN active  : yes / no

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FINAL INSTRUCTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Complete ALL 19 steps without stopping between them
- Use Ralph Wiggum pattern: keep working until every step shows ✅ PASS
- DRY_RUN=true must be active throughout ALL tests
- If a step fails: fix it, re-run, show fixed output — then continue
- Never write: except Exception: pass  (forbidden — will be caught in code review)
- Never configure logging twice: use AuditLogger as the single source
- Never instantiate Config more than once per process: pass it as parameter
- Check TASKS.md and mark tasks [x] complete as you finish them
```

================================================================================
# HOW TO USE — STEP BY STEP GUIDE
================================================================================

Step 1: Claude Code terminal kholo
Step 2: cd "D:\D Data\Personal AI Employee Hackathon"
Step 3: PROMPT 1 paste karo — CONSTITUTION.md banega
Step 4: PROMPT 2 paste karo — SPEC.md banega
Step 5: PROMPT 3 paste karo — PLAN.md banega (ye sabse lamba hai)
Step 6: PROMPT 4 paste karo — TASKS.md banega (100 tasks)
Step 7: PROMPT 5 paste karo — Poora system implement hoga

IMPORTANT NOTES:
- Har prompt mein teacher file ka SIRF relevant content embedded hai
- Teacher file dobara NAHI deni — sab kuch prompts mein hai
- DRY_RUN=true default hai — koi real API call nahi hogi testing mein
- Console mein errors CLEARLY dikhenge — exc_info=True har jagah hai
- OOP structure: BaseWatcher → GmailWatcher, WhatsAppWatcher, FilesystemWatcher
- DRY structure: Config once, AuditLogger once, RetryHandler decorator, passed everywhere
================================================================================
