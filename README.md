# Personal AI Employee — Digital FTE

> **Silver Tier Hackathon Project** — Autonomous AI agent that works as your digital employee, reading tasks from WhatsApp/Gmail/File drops, planning actions, requesting human approval, and executing via MCP servers.

**Target**: 20-30 hours implementation | **Status**: In Development | **Brain**: Qwen Code

---

## 🎯 What This Does

Your AI Employee:
1. **Watches** Gmail, WhatsApp, and filesystem for incoming tasks
2. **Plans** actions using Qwen reasoning (creates PLAN_*.md files)
3. **Requests Approval** for payments, emails, social posts (HITL workflow)
4. **Executes** approved actions via MCP servers (email, browser, filesystem)
5. **Logs Everything** in JSON audit trails (90-day retention)
6. **Generates CEO Briefings** every Monday morning

All coordination happens through **Obsidian markdown files** in a local vault — no database needed.

---

## 🏗️ Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Gmail API     │     │  WhatsApp Web    │     │  Filesystem     │
│   (120s poll)   │     │  (30s poll)      │     │  (watchdog)     │
└────────┬────────┘     └────────┬─────────┘     └────────┬────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI_Employee_Vault/                           │
│  Needs_Action/ ← Watchers write here                            │
│  Plans/        ← Qwen writes PLAN_*.md here                     │
│  Pending_Approval/ ← Qwen writes approval requests              │
│  Approved/     ← User moves here = GO                           │
│  Done/         ← Completed tasks (Ralph Wiggum checks)          │
└─────────────────────────────────────────────────────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Orchestrator   │     │  Qwen Reasoning  │     │  MCP Servers    │
│  (master loop)  │────▶│  (plan & decide) │────▶│  email/browser  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

---

## 📁 Project Structure

```
project-root/
├── AI_Employee_Vault/          # Obsidian vault (single source of truth)
│   ├── Inbox/                  # Manual file drops
│   ├── Needs_Action/           # Watchers write here
│   ├── Plans/                  # Qwen writes plans here
│   ├── Pending_Approval/       # Approval requests land here
│   ├── Approved/               # User approves → triggers MCP
│   ├── Done/                   # Completed tasks
│   ├── Logs/                   # JSON audit logs + PM2 logs
│   ├── Briefings/              # Monday CEO briefings
│   ├── Dashboard.md            # Live system status
│   ├── Company_Handbook.md     # 10 rules of engagement
│   └── Business_Goals.md       # Q1 targets, KPIs
│
├── src/
│   ├── config.py               # Config dataclass (ONE instance)
│   ├── watchers/
│   │   ├── base_watcher.py     # BaseWatcher ABC
│   │   ├── gmail_watcher.py    # GmailWatcher (120s)
│   │   ├── whatsapp_watcher.py # WhatsAppWatcher (30s)
│   │   └── filesystem_watcher.py
│   ├── actions/
│   │   ├── audit_logger.py     # AuditLogger (90-day retention)
│   │   ├── retry_handler.py    # @with_retry decorator
│   │   ├── rate_limiter.py     # RateLimiter
│   │   └── linkedin_poster.py  # LinkedInPoster(BaseAction)
│   ├── orchestrator.py         # Master process
│   ├── watchdog_monitor.py     # Restarts dead watchers
│   └── briefing_generator.py   # Sunday 11PM briefing
│
├── .qwen/
│   ├── hooks/stop.py           # Ralph Wiggum stop-hook
│   ├── mcp.json                # MCP server config
│   └── model_config.yaml       # Qwen settings
│
├── .env                        # Secrets (NEVER commit)
├── .gitignore                  # Created FIRST
├── ecosystem.config.js         # PM2 config (4 apps)
├── pyproject.toml              # UV project
└── README.md                   # This file
```

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Install Command |
|------|---------|-----------------|
| Python | 3.13+ | `py --version` |
| Node.js | v24+ | `node --version` |
| PM2 | latest | `npm install -g pm2` |
| Obsidian | v1.10.6+ | [Download](https://obsidian.md) |
| UV | latest | `pip install uv` |

### 1. Clone & Setup

```bash
cd "D:\D Data\Personal AI Employee Hackathon"
uv sync
npm install  # for MCP servers
```

### 2. Configure Environment

```bash
copy .env.template .env
```

Edit `.env` with your values (see **FREE Options** below):

```bash
DRY_RUN=true                    # Keep true until tested
VAULT_PATH=./AI_Employee_Vault
GMAIL_CREDENTIALS=./credentials.json
WHATSAPP_SESSION_PATH=./whatsapp_session
QWEN_API_KEY=ollama             # Use local Qwen (FREE)
QWEN_BASE_URL=http://localhost:11434/v1
```

### 3. Create Vault Structure

```bash
mkdir -p AI_Employee_Vault/{Inbox,Needs_Action,Plans,Pending_Approval,Approved,Rejected,Done,Logs/pm2,Briefings,Accounting}
```

Create these files in `AI_Employee_Vault/`:
- `Dashboard.md` (see template in QWEN.md)
- `Company_Handbook.md` (10 rules)
- `Business_Goals.md` (Q1 targets)

### 4. Start Watchers (PM2)

```bash
pm2 start ecosystem.config.js
pm2 list
pm2 logs
```

### 5. Test End-to-End

1. Create test file: `AI_Employee_Vault/Inbox/test.txt`
2. Watcher moves it to `Needs_Action/`
3. Orchestrator processes → creates `Plans/PLAN_*.md`
4. If approval needed → `Pending_Approval/`
5. You move to `Approved/` → MCP executes
6. File moves to `Done/`

---

## 🔐 FREE Options (No Cost Required)

| Service | FREE Tier | Setup |
|---------|-----------|-------|
| **Gmail API** | Free with Google Cloud | [Guide](https://developers.google.com/gmail/api/quickstart) |
| **WhatsApp** | 100% Free (Web via Playwright) | No API needed |
| **Qwen Model** | Ollama local (100% free) | `ollama run qwen2.5:7b` |
| **Qwen API** | 1M tokens/month | [DashScope](https://dashscope.console.aliyun.com/) |
| **Filesystem** | Built-in (free) | No setup |
| **Browser MCP** | Free (Playwright) | `npx @anthropic/browser-mcp` |

**Recommended**: Use Ollama local Qwen + Gmail API + WhatsApp Web = **100% FREE stack**

---

## 📋 Vault File Schemas

### SCHEMA A: Needs_Action (Watchers write)

```yaml
---
type: email | whatsapp | file_drop
from: <sender>
subject: <max 100 chars>
received: <ISO 8601>
priority: high | medium | low
status: pending
watcher: GmailWatcher | WhatsAppWatcher | FilesystemWatcher
---
## Content
<message body>
## Suggested Actions
- [ ] Action 1
- [ ] Action 2
```

### SCHEMA B: Plan (Qwen writes)

```yaml
---
created: <ISO 8601>
task_ref: <Needs_Action filename>
status: pending_approval | in_progress | complete
iterations: <Ralph counter>
---
## Objective
<one sentence>
## Steps
- [ ] Step 1
## Approval Required
yes | no
## Completion Condition
<what moves this to Done/>
```

### SCHEMA C: Approval Request

```yaml
---
type: approval_request
action: send_email | payment | social_post
recipient: <email/phone>
reason: <why needed>
created: <ISO 8601>
expires: <24 hours later>
plan_ref: <Plan filename>
---
## Action Details
<full details>
## To APPROVE: Move to /Approved/
## To REJECT: Move to /Rejected/
```

---

## 🔄 End-to-End Example

**Scenario**: Client WhatsApp message: "Send me January invoice"

```
1. WhatsAppWatcher detects message (30s interval)
   → Creates: Needs_Action/WHATSAPP_client_2026-03-31.md

2. Orchestrator triggers Qwen
   → Creates: Plans/PLAN_invoice_client.md

3. Qwen determines email requires approval
   → Creates: Pending_Approval/EMAIL_invoice_client.md

4. You review and move file to Approved/

5. Email MCP sends invoice PDF
   → Logs to: Logs/2026-03-31.json

6. Files move to Done/
   → Dashboard.md updated
```

---

## 🛡️ Security

### What's Protected

| Feature | Implementation |
|---------|----------------|
| **Secrets** | `.env` only, never committed |
| **Credentials** | Outside vault, absolute paths |
| **Rate Limits** | 10 emails/hr, 3 payments/hr |
| **Audit Trail** | 90-day JSON logs |
| **HITL** | All payments/emails require approval |

### `.gitignore` Includes

```
.env  credentials.json  whatsapp_session/  __pycache__/  *.pyc  Logs/*.json
```

---

## 🧪 Testing

### Run Individual Watchers

```bash
uv run python src/watchers/gmail_watcher.py --test
uv run python src/watchers/whatsapp_watcher.py --test
uv run python src/watchers/filesystem_watcher.py --test
```

### Run Full Test Suite

```bash
uv run pytest test_all_watchers.py -v
uv run pytest test_e2e_process.py -v
```

### DRY_RUN Mode

Default: `DRY_RUN=true` in `.env`

All actions log what they **would** do without executing. Set to `false` only after manual testing passes.

---

## 📊 Monitoring
### PM2 Commands

```bash
pm2 list                    # Check status
pm2 logs                    # View all logs
pm2 restart <name>          # Restart specific process
pm2 save                    # Persist process list
pm2 startup                 # Auto-start on boot
```

---

## 📊 Interactive Dashboard (New)

The project now includes a professional, interactive Kanban-style dashboard for task management.

### 1. Prerequisites
Ensure you have the required dashboard dependencies:
```bash
pip install fastapi uvicorn pyyaml
```

### 2. Start the Dashboard Server
Run the FastAPI backend server:
```bash
uvicorn src.server:app --reload --port 8000
```

### 3. Access the Dashboard
Open your browser and navigate to:
**`http://localhost:8000`**

### 🎯 Key Features:
- **Kanban Board**: Manage Inbox, Pending Approval, and Done tasks visually.
- **One-Click Actions**: Approve or Reject plans directly from the UI.
- **Real-time Status**: Monitor system health and mode (DRY_RUN/PRODUCTION).
- **Toast Notifications**: Get instant feedback on all operations.
- **Auto-Refresh**: Column data updates every 15 seconds automatically.

---

## Dashboard

Check `AI_Employee_Vault/Dashboard.md` for:
- Watcher status (✅/❌)
- Pending actions count
- Today's completed tasks
- Revenue tracking
- Bottlenecks

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Python not found** | Install 3.13+, add to PATH |
| **Gmail 403** | Enable Gmail API in Google Cloud Console |
| **WhatsApp session lost** | Delete session folder, re-scan QR |
| **MCP won't connect** | Check Node.js paths in `.qwen/mcp.json` |
| **Ralph counter stuck** | Verify `.qwen/hooks/stop.py` config |
| **Vault permission error** | Run as administrator (Windows) |

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| `QWEN.md` | Project rules (overrides global) |
| `SPEC.md` | Technical specifications (8 sections) |
| `PLAN.md` | Implementation plan (phases 0-8) |
| `CONSTITUTION.md` | Core principles |
| `teacher-requirement.md` | Hackathon requirements |

---

## 🎯 Hackathon Judging Weights

| Category | Weight | Focus |
|----------|--------|-------|
| **Functionality** | 30% | End-to-end flow works |
| **Innovation** | 25% | Creative integrations |
| **Practicality** | 20% | Daily usability |
| **Security** | 15% | HITL, audit trail |
| **Documentation** | 10% | README + demo video |

---

## 📝 License

MIT License — Hackathon project for Panaversity

---

## 🤝 Contributing

This is a hackathon project. Key features to add:

- [ ] LinkedIn poster (browser automation)
- [ ] Payment gateway integration
- [ ] Multi-user support
- [ ] Voice briefing (TTS)
- [ ] Mobile app for approvals

---

**Built with**: Qwen Code + Obsidian + Python + MCP + PM2

*"Bismillah, let's build."* 🚀
