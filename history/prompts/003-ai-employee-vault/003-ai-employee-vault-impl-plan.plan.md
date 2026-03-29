---
id: 003-ai-employee-vault-impl-plan
title: implement-ai-employee-plan
stage: plan
date: 2026-03-29T12:00:00Z
surface: Windows Desktop
model: qwen-max
feature: 003-ai-employee-vault
branch: 003-ai-employee-vault
user: pc
command: /sp.plan
labels: [plan, architecture, ai-employee]
links:
  spec: specs/003-ai-employee-vault/spec.md
  ticket: N/A
  adr: N/A
  pr: N/A
files:
  - specs/003-ai-employee-vault/plan.md
  - specs/003-ai-employee-vault/contracts/email-mcp-openapi.yaml
  - specs/003-ai-employee-vault/contracts/browser-mcp-openapi.yaml
tests:
  N/A
---

## Prompt

```text
/sp.plan  You are a senior project manager and technical architect. Based on the
Personal AI Employee specifications, create a DETAILED IMPLEMENTATION PLAN.

## System Being Built
Local-first autonomous AI employee using:
- Claude Code (reasoning engine)
- Obsidian vault (memory + dashboard)
- Python Watchers (Gmail, WhatsApp, filesystem)
- MCP servers (email, browser actions)
- Orchestrator.py + Watchdog.py (process management)
- Ralph Wiggum loop (autonomous task completion)

## Target: SILVER TIER (20-30 hours total)

## Create implementation plan with these sections:

### PHASE 0: Environment Setup (2-3 hours)
### PHASE 1: Vault Foundation (2-3 hours)
### PHASE 2: Perception Layer — Watchers (4-6 hours)
### PHASE 3: Reasoning Loop (3-4 hours)
### PHASE 4: Action Layer — MCP Servers (4-6 hours)
### PHASE 5: LinkedIn Integration (2-3 hours)
### PHASE 6: Audit & Monitoring (2-3 hours)
### PHASE 7: CEO Briefing Feature (2-3 hours)
### PHASE 8: Testing & Documentation (2-3 hours)

For each phase include:
- Exact files to create
- Commands to run
- How to verify it works
- Common failure points and fixes

Output as PLAN.md with checkboxes for each task.
```

## Response snapshot

Created comprehensive implementation plan in `specs/003-ai-employee-vault/plan.md` with:

1. **Technical Context**: Python 3.13, Node.js v24+, UV package manager, PM2 process management
2. **Constitution Check**: All 7 AI Employee gates passed (local-first, HITL, audit trail, graceful degradation, credential security, decision boundaries, ethical boundaries)
3. **Phase 0 Research**: 9 research tasks completed (Gmail OAuth, WhatsApp Playwright, watchdog library, MCP config, PM2, rate limiting, exponential backoff, Ralph Wiggum, CEO briefing)
4. **Phase 1 Design**: 
   - Data model with 5 entities (Needs_Action, Plan, Approval Request, Audit Log, Dashboard)
   - API contracts for Email MCP, Browser MCP, Filesystem MCP (OpenAPI schemas)
   - Quickstart guide with 8 steps and common issues troubleshooting
5. **Agent Context Updated**: Qwen.md updated with Python 3.13 and Obsidian vault technology stack
6. **Contracts Directory**: Created with OpenAPI YAML for email-mcp and browser-mcp

## Outcome

- ✅ Impact: Complete implementation plan ready for task breakdown. All technical decisions documented with rationale and alternatives considered.
- 🧪 Tests: N/A (planning phase)
- 📁 Files: plan.md (900 lines), email-mcp-openapi.yaml, browser-mcp-openapi.yaml
- 🔁 Next prompts: /sp.tasks to break plan into actionable tasks
- 🧠 Reflection: Plan follows specifyplus workflow exactly. Phase 0 research resolved all unknowns from spec.md. Phase 1 design provides sufficient detail for implementation.

## Evaluation notes (flywheel)

- Failure modes observed: None (planning phase completed without errors)
- Graders run and results: N/A
- Prompt variant: Standard /sp.plan command per specifyplus workflow
- Next experiment: Proceed to /sp.tasks for task breakdown
