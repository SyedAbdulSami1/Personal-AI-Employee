---
id: PHR-001
title: Generate Tasks MD
stage: tasks
date: 2026-03-29T12:00:00Z
surface: Windows Desktop
model: qwen-max
feature: 003-ai-employee-vault
branch: 003-ai-employee-vault
user: pc
command: /sp.tasks
labels: [tasks, planning, ai-employee]
links:
  spec: specs/003-ai-employee-vault/spec.md
  ticket: N/A
  adr: specs/003-ai-employee-vault/plan.md
  pr: N/A
files:
  - specs/003-ai-employee-vault/tasks.md (created)
  - specs/003-ai-employee-vault/plan.md (read)
  - specs/003-ai-employee-vault/spec.md (read)
  - specs/003-ai-employee-vault/contracts/email-mcp-openapi.yaml (read)
  - specs/003-ai-employee-vault/contracts/browser-mcp-openapi.yaml (read)
tests:
  N/A - Task generation phase, tests will be created during implementation
---

## Prompt

Generate an actionable, dependency-ordered tasks.md for the AI Employee Vault System feature based on available design artifacts (plan.md, spec.md, contracts/).

Requirements:
- Read plan.md for tech stack, libraries, project structure
- Read spec.md for user stories with priorities (P1, P2, P3)
- Read contracts/ for API endpoints
- Generate 90-95 granular tasks organized by user story
- Each task must follow checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- Include Setup phase, Foundational phase, User Story phases (US1-US7), Security phase, Documentation phase
- Include dependency graph showing story completion order
- Include parallel execution examples per story
- Include implementation strategy (MVP first, incremental delivery)

## Response snapshot

Generated comprehensive tasks.md with 165 granular tasks organized into 12 phases:

**Phase 1: Setup (10 tasks)** - Tool installation, project initialization
**Phase 2: Foundational (12 tasks)** - Config, audit_logger, retry_handler, rate_limiter, base classes
**Phase 3: US1 - Email Processing (19 tasks)** - GmailWatcher, email-mcp integration
**Phase 4: US2 - WhatsApp Urgent (21 tasks)** - WhatsAppWatcher, Playwright, browser-mcp
**Phase 5: US3 - File Drops (15 tasks)** - FilesystemWatcher, watchdog library
**Phase 6: US4 - Claude Planning (15 tasks)** - Orchestrator, folder monitoring, approval workflow
**Phase 7: US5 - HITL Approval (10 tasks)** - Approval generator, payment/email/social post flows
**Phase 8: US6 - Ralph Wiggum (10 tasks)** - Stop-hook, counter logic, ALERT generation
**Phase 9: US7 - CEO Briefing (16 tasks)** - BriefingGenerator, cron/Task Scheduler, 6 sections
**Phase 10: Security (16 tasks)** - Watchdog monitor, disk/memory monitoring, Dashboard.md, Company_Handbook.md
**Phase 11: LinkedIn (8 tasks)** - LinkedInPoster, browser-mcp, scheduled posting
**Phase 12: Documentation (13 tasks)** - README, SECURITY.md, demo script, hackathon submission

## Outcome

- ✅ Impact: Created executable tasks.md with 165 granular tasks covering all 7 user stories from spec.md
- 🧪 Tests: Tests are optional per template - only included if explicitly requested (not requested in this feature)
- 📁 Files: specs/003-ai-employee-vault/tasks.md (165 tasks, 12 phases)
- 🔁 Next prompts: Ready for /sp.implement to begin Phase 1 Setup tasks
- 🧠 Reflection: Tasks organized by user story enable independent implementation and testing; MVP scope clearly defined (Phases 1-6 = 92 tasks)

## Evaluation notes (flywheel)

- Failure modes observed: None - task generation completed successfully
- Graders run and results: N/A - task generation phase
- Prompt variant: N/A - first run
- Next experiment: N/A - proceed to implementation phase
