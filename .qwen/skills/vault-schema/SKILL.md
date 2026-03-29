---
name: vault-schema
description: This skill should be used when creating, reading, or modifying vault files in AI_Employee_Vault/. Use when working with Needs_Action, Plans, Pending_Approval, Approved, Rejected, Done folders, or any markdown file with YAML frontmatter.
---

# Vault Schema Skill

## Purpose

Provide standardized templates and validation for all vault file types. All files in `AI_Employee_Vault/` use YAML frontmatter for metadata and markdown for content.

## When to Use This Skill

✅ Creating new action files (watchers writing to Needs_Action/)
✅ Creating plan files (Qwen writing plans for tasks)
✅ Creating approval requests (before HITL actions)
✅ Reading/processing vault files (orchestrator, actions)
✅ Validating file format (ensuring schema compliance)
✅ Moving files between folders (status transitions)

---

## Vault Folder Structure

```
AI_Employee_Vault/
├── Inbox/                    ← User manually drops files here
├── Needs_Action/             ← Watchers WRITE here; Orchestrator READS here
├── In_Progress/qwen/         ← Claim-by-move rule (no double-work)
├── Plans/                    ← Qwen writes PLAN_<task>.md
├── Pending_Approval/         ← Qwen writes approval requests
├── Approved/                 ← User moves here = approved → triggers MCP
├── Rejected/                 ← User moves here = rejected
├── Done/                     ← Completed tasks; Ralph Wiggum checks this
├── Logs/
│   ├── pm2/                  ← PM2 sub-logs
│   └── YYYY-MM-DD.json       ← Audit logs (90-day retention)
├── Briefings/                ← Monday CEO briefings
├── Accounting/               ← Finance watcher writes Current_Month.md
├── Dashboard.md              ← Live status; Qwen updates after every task
├── Company_Handbook.md       ← 10 rules of engagement
└── Business_Goals.md         ← Q1 targets, KPIs, subscription rules
```

---

## Schema A: Needs_Action File

**Written by:** Watchers (GmailWatcher, WhatsAppWatcher, FilesystemWatcher)
**Read by:** Orchestrator → Qwen for processing

### Template

```markdown
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

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | enum | Yes | Source type: `email`, `whatsapp`, `file_drop` |
| `from` | string | Yes | Sender name, phone number, or file dropper |
| `subject` | string | Yes | Subject line or message preview (max 100 chars) |
| `received` | ISO 8601 | Yes | Timestamp in UTC: `2026-01-07T10:30:00Z` |
| `priority` | enum | Yes | `high`, `medium`, `low` |
| `status` | enum | Yes | `pending`, `in_progress`, `complete`, `failed` |
| `watcher` | string | Yes | Which watcher created this file |

### Example

```markdown
---
type: whatsapp
from: +1-555-0123
subject: Hey, can you send me the invoice for January?
received: 2026-01-07T10:30:00Z
priority: high
status: pending
watcher: WhatsAppWatcher
---

## Content
Hey, can you send me the invoice for January? We need it for accounting.

## Suggested Actions
- [ ] Identify client from phone number
- [ ] Generate January invoice PDF
- [ ] Send via email
```

### File Naming Convention

```
Needs_Action/
├── EMAIL_<message_id>_<timestamp>.md
├── WHATSAPP_<contact>_<timestamp>.md
└── FILE_<filename>_<timestamp>.md
```

**Example:**
- `EMAIL_msg123_2026-01-07.md`
- `WHATSAPP_client_a_2026-01-07.md`
- `FILE_invoice.pdf_2026-01-07.md`

---

## Schema B: Plan File

**Written by:** Qwen (after processing Needs_Action/)
**Read by:** Orchestrator, User, Ralph Wiggum

### Template

```markdown
---
created: <ISO 8601>
task_ref: <filename from Needs_Action that triggered this>
status: pending_approval | in_progress | complete | failed
iterations: <Ralph Wiggum counter, starts at 0>
---

## Objective
<objective in one sentence>

## Steps
- [x] Step 1 (completed)
- [ ] Step 2
- [ ] Step 3

## Approval Required
yes | no — <reason if yes>

## Completion Condition
<what must be true for task to move to /Done/>
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `created` | ISO 8601 | Yes | Plan creation timestamp |
| `task_ref` | string | Yes | Reference to triggering Needs_Action file |
| `status` | enum | Yes | `pending_approval`, `in_progress`, `complete`, `failed` |
| `iterations` | int | Yes | Ralph Wiggum counter (0-10 max) |

### Example

```markdown
---
created: 2026-01-07T10:35:00Z
task_ref: WHATSAPP_client_a_2026-01-07.md
status: pending_approval
iterations: 0
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
yes — Email send requires human approval per Company_Handbook.md rule #6

## Completion Condition
Invoice PDF generated, email sent to client_a@email.com, transaction logged to audit log
```

### File Naming Convention

```
Plans/
└── PLAN_<taskname>_<timestamp>.md
```

**Example:**
- `PLAN_invoice_client_a_2026-01-07.md`
- `PLAN_whatsapp_response_2026-01-07.md`

---

## Schema C: Approval Request

**Written by:** Qwen (before HITL actions)
**Read by:** User (for approval/rejection)

### Template

```markdown
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

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | enum | Yes | Always `approval_request` |
| `action` | enum | Yes | `send_email`, `payment`, `social_post`, `file_delete`, `whatsapp_send` |
| `amount` | float | Conditional | Dollar amount (only for payments) |
| `recipient` | string | Yes | Email, phone, or platform handle |
| `reason` | string | Yes | One sentence justification |
| `created` | ISO 8601 | Yes | Request creation timestamp |
| `expires` | ISO 8601 | Yes | Expiration (exactly 24 hours after created) |
| `status` | enum | Yes | `pending`, `approved`, `rejected`, `expired` |
| `plan_ref` | string | Yes | Reference to Plan file |

### Example

```markdown
---
type: approval_request
action: send_email
to: client_a@email.com
subject: January 2026 Invoice - $1,500
attachment: /Vault/Invoices/2026-01_Client_A.pdf
reason: Client requested invoice via WhatsApp
created: 2026-01-07T10:40:00Z
expires: 2026-01-08T10:40:00Z
status: pending
plan_ref: PLAN_invoice_client_a_2026-01-07.md
---

## Action Details
Ready to send invoice to Client A.

**To:** client_a@email.com
**Subject:** January 2026 Invoice - $1,500
**Attachment:** /Vault/Invoices/2026-01_Client_A.pdf
**Body:** Please find attached your invoice for January 2026.

## To APPROVE: Move this file to /Approved/
## To REJECT:  Move this file to /Rejected/
```

### File Naming Convention

```
Pending_Approval/
├── EMAIL_<task>_<timestamp>.md
├── PAYMENT_<task>_<timestamp>.md
└── SOCIAL_POST_<task>_<timestamp>.md
```

**Example:**
- `EMAIL_invoice_client_a_2026-01-07.md`
- `PAYMENT_vendor_x_2026-01-07.md`

---

## Schema D: Audit Log Entry

**Written by:** AuditLogger (after every action)
**Read by:** User, Orchestrator (for debugging)

### Format

**File:** `Logs/YYYY-MM-DD.json` (one JSON line per action)

```json
{"timestamp":"ISO 8601","action_type":"email_send|payment|social_post|file_move|watcher_start|error","actor":"qwen_agent | gmail_watcher | whatsapp_watcher | human","target":"<recipient, file path, or platform>","parameters":{},"approval_status":"human_approved","approved_by":"human | system | none","result":"success | failure | dry_run | skipped","error":"<full error message + traceback if result=failure, else null>","dry_run":false}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `timestamp` | ISO 8601 | Yes | Action timestamp |
| `action_type` | enum | Yes | Type of action performed |
| `actor` | enum | Yes | Who/what performed the action |
| `target` | string | Yes | Recipient, file path, or platform |
| `parameters` | object | Yes | Action-specific parameters |
| `approval_status` | enum | Yes | `human_approved`, `system`, `none` |
| `approved_by` | enum | Yes | `human`, `system`, `none` |
| `result` | enum | Yes | `success`, `failure`, `dry_run`, `skipped` |
| `error` | string | Conditional | Full error message if result=failure |
| `dry_run` | boolean | Yes | Whether action was dry run |

### Example Entries

```json
{"timestamp":"2026-01-07T10:45:00Z","action_type":"email_send","actor":"qwen_agent","target":"client_a@email.com","parameters":{"subject":"January 2026 Invoice"},"approval_status":"human_approved","approved_by":"human","result":"success","error":null,"dry_run":false}
{"timestamp":"2026-01-07T10:30:00Z","action_type":"watcher_start","actor":"gmail_watcher","target":"Gmail API","parameters":{"query":"is:unread is:important"},"approval_status":"system","approved_by":"system","result":"success","error":null,"dry_run":true}
{"timestamp":"2026-01-07T09:15:00Z","action_type":"payment","actor":"qwen_agent","target":"vendor@example.com","parameters":{"amount":150.00},"approval_status":"human_approved","approved_by":"human","result":"failure","error":"StripeError: Card declined","dry_run":false}
```

### Retention Policy

- **90 days** retention
- AuditLogger.__init__ automatically deletes files older than 90 days
- Files named by date: `2026-01-07.json`

---

## Schema E: Dashboard.md

**Written by:** Qwen (after every task)
**Read by:** User, CEO Briefing Generator

### Template

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

### Update Frequency

- **After every task completion**
- **On status changes** (watcher start/stop)
- **Daily summary** (end of day)

---

## Schema F: CEO Briefing

**Written by:** BriefingGenerator (Sunday 11 PM)
**Read by:** User (Monday morning)

### Template

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

### Trigger

- **Every Sunday 11:00 PM** (cron on Mac/Linux, Task Scheduler on Windows)
- Runs as separate process: `src/briefing_generator.py`

---

## File Operations

### Creating a New File

```python
from pathlib import Path
from datetime import datetime

def create_needs_action_file(item: Dict[str, Any]) -> str:
    """Create Needs_Action file using Schema A."""
    vault_path = Path(config.vault_path)
    needs_action_dir = vault_path / "Needs_Action"
    
    timestamp = datetime.fromisoformat(item['received']).strftime('%Y-%m-%d')
    filename = f"{item['type']}_{item['id']}_{timestamp}.md"
    filepath = needs_action_dir / filename
    
    content = f"""---
type: {item['type']}
from: {item['from']}
subject: {item['subject'][:100]}
received: {item['received']}
priority: {item.get('priority', 'medium')}
status: pending
watcher: {item['watcher']}
---

## Content
{item['content']}

## Suggested Actions
- [ ] Review and respond
"""
    
    if config.dry_run:
        logger.info("[DRY RUN] Would create: %s", filename)
        return str(filepath)
    
    filepath.write_text(content, encoding='utf-8')
    return str(filepath)
```

### Moving Files (Status Transitions)

```python
def move_to_approved(filepath: Path):
    """Move file from Pending_Approval/ to Approved/."""
    approved_dir = vault_path / "Approved"
    approved_dir.mkdir(parents=True, exist_ok=True)
    
    new_path = approved_dir / filepath.name
    filepath.rename(new_path)
    
    logger.info("Moved to Approved/: %s", filepath.name)

def move_to_done(filepath: Path):
    """Move file to Done/ after successful completion."""
    done_dir = vault_path / "Done"
    done_dir.mkdir(parents=True, exist_ok=True)
    
    new_path = done_dir / filepath.name
    filepath.rename(new_path)
    
    # Update Dashboard.md
    update_dashboard(filepath.name)
```

### Reading Frontmatter

```python
import yaml
from pathlib import Path

def parse_frontmatter(filepath: Path) -> Dict[str, Any]:
    """Parse YAML frontmatter from markdown file."""
    content = filepath.read_text(encoding='utf-8')
    
    # Split frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 2:
            frontmatter = yaml.safe_load(parts[1])
            body = parts[2] if len(parts) > 2 else ''
            return {**frontmatter, 'body': body, 'filename': filepath.name}
    
    return {'body': content, 'filename': filepath.name}
```

### Validating Schema

```python
def validate_schema_a(filepath: Path) -> bool:
    """Validate Needs_Action file against Schema A."""
    data = parse_frontmatter(filepath)
    
    required_fields = ['type', 'from', 'subject', 'received', 'priority', 'status', 'watcher']
    
    for field in required_fields:
        if field not in data:
            logger.error("Missing required field: %s", field)
            return False
    
    # Validate enum values
    if data['type'] not in ['email', 'whatsapp', 'file_drop']:
        logger.error("Invalid type: %s", data['type'])
        return False
    
    if data['priority'] not in ['high', 'medium', 'low']:
        logger.error("Invalid priority: %s", data['priority'])
        return False
    
    return True
```

---

## Reference Files

- [Business_Goals.md Template](../../AI_Employee_Vault/Business_Goals.md.template)
- [Company_Handbook.md](../../AI_Employee_Vault/Company_Handbook.md)
- [Dashboard.md](../../AI_Employee_Vault/Dashboard.md)
- [Audit Logger](../../src/actions/audit_logger.py)

---

## Anti-Patterns (Avoid These)

❌ **Missing frontmatter** - All vault files MUST have YAML frontmatter
❌ **Invalid timestamps** - Always use ISO 8601: `2026-01-07T10:30:00Z`
❌ **Wrong folder** - Files must be in correct folder (Needs_Action/, Plans/, etc.)
❌ **No status field** - Always track status: `pending`, `in_progress`, `complete`
❌ **Hardcoded paths** - Use `config.vault_path`, not absolute paths
❌ **Overwriting files** - Use unique filenames with timestamps
❌ **Skipping audit log** - All actions logged to `Logs/YYYY-MM-DD.json`
❌ **Expired approvals** - Check expires field before processing

---

## Success Metrics

✅ All vault files use correct schema
✅ Frontmatter validates against schema
✅ Files in correct folders
✅ Status transitions tracked
✅ Audit logs created for all actions
✅ Dashboard.md updated after tasks
✅ CEO briefings generated weekly

---

**Created from:** AI Employee Hackathon - Vault File Schemas
**Reference:** SPEC.md, QWEN.md Section 5 (Vault File Schemas)
