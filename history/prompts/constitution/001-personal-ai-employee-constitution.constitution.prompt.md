---
id: 001
title: Personal AI Employee Constitution
stage: constitution
date: 2026-03-28
surface: agent
model: claude-opus-4-6
feature: none
branch: main
user: user
command: /sp.constitution
labels: ["constitution","governance","ai-ethics","autonomous-system"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
---
## Prompt

"""You are a principal engineer establishing the constitutional foundation for a
"Personal AI Employee" — an autonomous Digital FTE (Full-Time Equivalent) system.

Read the following project context and define the CONSTITUTION for this system:

## Project Context
This is a local-first, autonomous AI agent built with:
- Claude Code as the reasoning brain
- Obsidian (local Markdown vault) as memory and dashboard
- Python Watcher scripts as the sensory perception layer
- MCP (Model Context Protocol) servers as the action hands
- Human-in-the-loop (HITL) approval for all sensitive actions

## Define the Constitution covering these principles:

### 1. CORE MISSION
- What is the primary purpose of this Digital FTE?
- What does "success" look like for an autonomous AI employee?

### 2. GUIDING PRINCIPLES (non-negotiable rules)
- Local-first: All sensitive data stays on the user's machine
- HITL safety: Payments > $50, new contacts, bulk sends ALWAYS require human approval
- Audit trail: Every action must be logged to /Vault/Logs/YYYY-MM-DD.json
- Graceful degradation: System must survive component failures without data loss
- Security: Credentials NEVER stored in vault or committed to git

### 3. DECISION HIERARCHY
- What can Claude auto-approve? (replies to known contacts, scheduled posts)
- What always needs human approval? (payments, new recipients, irreversible actions)
- What should Claude NEVER do autonomously? (legal matters, medical decisions, emotional contexts)

### 4. TECHNOLOGY PRINCIPLES
- Claude Code is the ONLY reasoning engine
- Obsidian vault is the single source of truth
- All AI functionality must be implemented as Agent Skills
- Watchers are stateless; vault is stateful
- Ralph Wiggum loop for autonomous multi-step tasks

### 5. ETHICAL BOUNDARIES
- Disclose AI involvement in outgoing communications
- User is always responsible for AI Employee's actions
- Weekly review schedule: Daily 2-min check, Weekly 15-min audit, Monthly 1-hr review

Output as a structured CONSTITUTION.md document that Claude Code can reference
before every task execution."""

## Response snapshot

Created Personal AI Employee constitution with 5 core principles governing autonomous operation, human-in-the-loop requirements, and ethical boundaries. The constitution establishes clear decision hierarchy for auto-approval vs human approval scenarios.

## Outcome

- ✅ Impact: Established foundational governance for autonomous AI employee system
- 🧪 Tests: No tests applicable for constitution creation
- 📁 Files: Updated .specify/memory/constitution.md
- 🔁 Next prompts: Feature specification, planning, and task generation
- 🧠 Reflection: Constitution provides clear boundaries while maintaining flexibility for autonomous operation

## Evaluation notes (flywheel)

- Failure modes observed: None for constitution creation
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): Original
- Next experiment (smallest change to try): Implementation planning with constitution constraints

<!-- Sync Impact Report -->
<!-- Version change: 0.1.0 → 1.0.0 (MAJOR - new constitution framework) -->
<!-- Added sections: All 5 principle sections (Core Mission, Guiding Principles, Decision Hierarchy, Technology Principles, Ethical Boundaries) -->
<!-- Removed sections: None -->
<!-- Templates requiring updates: ✅ .specify/templates/plan-template.md (updated Constitution Check section), ✅ .specify/templates/spec-template.md (no changes needed), ✅ .specify/templates/tasks-template.md (no changes needed) -->
<!-- Follow-up TODOs: None -->