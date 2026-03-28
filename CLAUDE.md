# CLAUDE.md — Project Rules
# D:\D Data\Personal AI Employee Hackathon\CLAUDE.md
# This file OVERRIDES C:\Users\pc\.claude\CLAUDE.md
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
Brain   : Claude Code (sole reasoning engine — no other LLMs)
Memory  : AI_Employee_Vault/ (local Obsidian markdown — single source of truth)
Senses  : Python Watcher scripts (Gmail, WhatsApp, filesystem)
Hands   : MCP servers (email-mcp, browser-mcp, filesystem-mcp built-in)
Loop    : Ralph Wiggum stop-hook → .claude/hooks/stop.py (max 10 iterations)
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
│   ├── In_Progress/claude/       ← claim-by-move rule (no double-work)
│   ├── Plans/                    ← Claude writes PLAN_<task>.md
│   ├── Pending_Approval/         ← Claude writes approval requests; user reviews
│   ├── Approved/                 ← user moves here = approved → triggers MCP
│   ├── Rejected/                 ← user moves here = rejected; Claude logs+stops
│   ├── Done/                     ← completed tasks; Ralph Wiggum checks this
│   ├── Logs/pm2/                 ← JSON audit logs + PM2 sub-logs
│   ├── Briefings/                ← Monday CEO briefings land here
│   ├── Accounting/               ← Finance watcher writes Current_Month.md
│   ├── Dashboard.md              ← live status; Claude updates after every task
│   ├── Company_Handbook.md       ← 10 rules of engagement; Claude reads before acting
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
├── .claude/
│   ├── hooks/stop.py             ← Ralph Wiggum. Blocks exit until Done/ has task.
│   ├── mcp.json                  ← MCP server config
│   └── skills/                   ← Agent Skills (SKILL.md files)
│
├── .env                          ← secrets only. In .gitignore. Never committed.
├── .gitignore                    ← FIRST file created. Always.
├── ecosystem.config.js           ← PM2 config: 4 apps
├── pyproject.toml                ← UV project
└── CLAUDE.md                     ← this file
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

### Ralph Wiggum stop-hook (.claude/hooks/stop.py):
```
Exit allowed : task file exists in Done/
Exit blocked : counter < 10 → increment, re-inject prompt, sys.exit(1)
Max reached  : counter == 10 → write ALERT_ralph_max_<task>.md → sys.exit(0)
Counter var  : RALPH_COUNTER env var (reset to "0" between tasks)
```

---

## 5. VAULT FILE SCHEMAS — always use YAML frontmatter

```yaml
# Needs_Action file (Watchers write this):
---
type: email | whatsapp | file_drop
from: <sender>
subject: <preview, max 100 chars>
received: <ISO 8601>
priority: high | medium | low
status: pending
watcher: GmailWatcher | WhatsAppWatcher | FilesystemWatcher
---

# Approval request (Claude writes to Pending_Approval/):
---
type: approval_request
action: send_email | payment | social_post | file_delete | whatsapp_send
recipient: <target>
reason: <one sentence why>
created: <ISO 8601>
expires: <ISO 8601, +24hrs>
status: pending
plan_ref: <PLAN_filename.md that triggered this>
---
# To APPROVE: move this file to /Approved/
# To REJECT:  move this file to /Rejected/
```

### Audit log — /Logs/YYYY-MM-DD.json — one JSON line per action:
```json
{"timestamp":"ISO","action_type":"email_send","actor":"claude_code",
 "target":"<recipient>","parameters":{},"approval_status":"human_approved",
 "result":"success","error":null,"dry_run":false}
```
Retention: 90 days. AuditLogger.__init__ deletes older files automatically.

---

## 6. SECURITY

```
.gitignore FIRST — must include:
  .env  credentials.json  whatsapp_session/  __pycache__/  *.pyc  Logs/*.json

.env keys (fill values in .env, not here):
  GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_CREDENTIALS=<abs path>
  BANK_API_TOKEN, WHATSAPP_SESSION_PATH=<abs path>
  DRY_RUN=true, DEV_MODE=true, VAULT_PATH=./AI_Employee_Vault

Credentials path: OUTSIDE vault. Absolute path. Rotated monthly.
Logging: never log token, password, or PII — even at DEBUG level.
Vault sync (Platinum tier): markdown/state only. .env and sessions NEVER sync.
```

---

## 7. MCP CONFIG — .claude/mcp.json

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
  ]
}
```

---

## 8. ERROR RECOVERY

```
Network / rate-limit  → @with_retry: 1s→2s→4s backoff, cap 60s
Auth 401/403          → log ERROR, write ALERT_auth_<svc>.md to Needs_Action/, pause
Bad vault file        → move to Rejected/, log ERROR, continue next task
Watcher crash         → watchdog_monitor.py restarts + writes ALERT_<n>_restarted.md
Gmail API down        → queue in Needs_Action/, process when restored
Banking timeout       → NEVER auto-retry. Fresh human approval every time.
Claude unavailable    → watchers keep collecting; queue grows; process on restart
```

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

## 10. WHERE TO FIND DETAILS — on-demand only

```
Project principles     → CONSTITUTION.md
Full specifications    → SPEC.md  (schemas, watcher specs, MCP config)
Phase-by-phase plan    → PLAN.md  (exact commands + verify steps per phase)
Task checklist         → TASKS.md (100 tasks; mark [x] as completed)
Agent skills           → .claude/skills/*.md  (read only when relevant)
Ralph Wiggum impl      → .claude/hooks/stop.py
Teacher requirements   → teacher-requirement.md (source of truth for hackathon)
```

---
# ~145 lines. Every line prevents a specific mistake or token waste.
# Global baseline: C:\Users\pc\.claude\CLAUDE.md (this file overrides it)
