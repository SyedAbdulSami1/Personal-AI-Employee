# Tasks: AI Employee Vault System

**Input**: Design documents from `/specs/003-ai-employee-vault/`
**Prerequisites**: plan.md, spec.md, contracts/email-mcp-openapi.yaml, contracts/browser-mcp-openapi.yaml

**Tests**: Tests are OPTIONAL - only include them if explicitly requested in the feature specification or if user requests TDD approach.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Install tools, initialize project, create .gitignore and .env template

- [ ] T001 [P] Install Python 3.13 and verify: `python --version`
- [ ] T002 [P] Install Node.js v24+ and verify: `node --version`
- [ ] T003 [P] Install UV package manager: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- [ ] T004 [P] Install PM2 globally: `npm install -g pm2`
- [ ] T005 [P] Install Obsidian v1.10.6+ (optional, for vault viewing)
- [ ] T006 [P] Install Claude Code from claude.ai/download
- [ ] T007 Initialize UV Python project: `uv init` (if not already done)
- [ ] T008 [P] Create .gitignore with: .env, .claude/, *.pyc, __pycache__/, node_modules/, Logs/*.json, whatsapp_session/
- [ ] T009 [P] Create .env.example template with all required variables (GMAIL_CLIENT_ID, GMAIL_CREDENTIALS, WHATSAPP_SESSION_PATH, DRY_RUN=true, VAULT_PATH, DEV_MODE=true)
- [ ] T010 Copy .env.example to .env and instruct user to fill in actual values

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T011 [P] Create src/config.py with Config dataclass (dry_run, dev_mode, vault_path, gmail_credentials, whatsapp_session_path, rate limits)
- [ ] T012 [P] Create src/actions/audit_logger.py with AuditLogger class (JSON logging to Logs/YYYY-MM-DD.json, 90-day retention)
- [ ] T013 [P] Create src/actions/retry_handler.py with @with_retry decorator (exponential backoff: 1s→2s→4s, cap 60s)
- [ ] T014 [P] Create src/actions/rate_limiter.py with RateLimiter class (token bucket: 10 emails/hr, 3 payments/hr, 5 posts/day)
- [ ] T015 [P] Create src/actions/base_action.py with BaseAction abstract class (DRY_RUN guard, execute() ABC)
- [ ] T016 [P] Create src/watchers/base_watcher.py with BaseWatcher abstract class (run() loop, DRY_RUN guard, logger setup)
- [ ] T017 [P] Create logging.basicConfig() pattern for all Python files (StreamHandler + FileHandler to vault/Logs/app.log)
- [ ] T018 [P] Create AI_Employee_Vault/ folder structure: Inbox/, Needs_Action/, In_Progress/claude/, Plans/, Pending_Approval/, Approved/, Rejected/, Done/, Logs/, Logs/pm2/, Briefings/, Accounting/
- [ ] T019 [P] Create .qwen/hooks/stop.py (Ralph Wiggum stop-hook with RALPH_COUNTER, TASK_FILE, max 10 iterations)
- [ ] T020 [P] Create .qwen/mcp.json with filesystem (builtin), email-mcp, browser-mcp configuration
- [ ] T021 [P] Create ecosystem.config.js with PM2 config for 4 apps (orchestrator, gmail_watcher, whatsapp_watcher, watchdog)
- [ ] T022 [P] Create .qwen/model_config.yaml with Qwen model settings (qwen-max, temperature=0.2, max_tokens=4096)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Email Processing Workflow (Priority: P1) 🎯 MVP

**Goal**: GmailWatcher polls Gmail API every 120s and creates Needs_Action/EMAIL_<id>.md files for unread important emails

**Independent Test**: Send an email to monitored Gmail account → verify EMAIL_<message_id>.md appears in Needs_Action/ within 120 seconds with correct Schema A frontmatter

### Implementation for User Story 1

- [ ] T023 [P] [US1] Create src/watchers/gmail_watcher.py with GmailWatcher class extending BaseWatcher
- [ ] T024 [P] [US1] Add google-api-python-client, google-auth-httplib2, google-auth-oauthlib dependencies to pyproject.toml
- [ ] T025 [US1] Implement Gmail OAuth2 setup in gmail_watcher.py (credentials.json loading, refresh token handling)
- [ ] T026 [US1] Implement Gmail API query "is:unread is:important" in gmail_watcher.py check_for_updates()
- [ ] T027 [US1] Implement in-memory processed_ids set for deduplication (cleared on restart)
- [ ] T028 [US1] Implement create_action_file() to write Needs_Action/EMAIL_<message_id>.md with Schema A frontmatter
- [ ] T029 [US1] Add DRY_RUN guard: log "[DRY RUN] Would create EMAIL_<id>.md" without writing file
- [ ] T030 [US1] Add error handling: google.auth.exceptions.TransportError → retry with backoff
- [ ] T031 [US1] Add error handling: googleapiclient.errors.HttpError → log [ERROR] + create ALERT_gmail_api.md
- [ ] T032 [US1] Add console output: [GmailWatcher] Starting... | [GmailWatcher] Found N new emails | [GmailWatcher] Created EMAIL_<id>.md
- [ ] T033 [US1] Create Gmail API credentials setup guide (Google Cloud Console steps: enable API, OAuth consent, credentials.json download)
- [ ] T034 [US1] Create src/actions/email_action.py with EmailAction class (send, draft, search operations via email-mcp)
- [ ] T035 [US1] Implement email-mcp integration in email_action.py (call send_email, draft_email, search_emails endpoints)
- [ ] T036 [US1] Add rate limiting to email_action.py: check MAX_EMAILS_PER_HOUR before send
- [ ] T037 [US1] Create email-mcp server setup: clone email-mcp repo, install dependencies, configure GMAIL_CREDENTIALS
- [ ] T038 [US1] Test GmailWatcher in dry-run mode: send test email → verify log shows "[DRY RUN]" message
- [ ] T039 [US1] Test GmailWatcher in live mode: set DRY_RUN=false → send test email → verify Needs_Action/EMAIL_*.md created
- [ ] T040 [US1] Configure PM2 for gmail_watcher: `pm2 start ecosystem.config.js --only gmail_watcher`
- [ ] T041 [US1] Verify GmailWatcher runs continuously: `pm2 logs gmail_watcher` shows polling every 120s

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - WhatsApp Urgent Message Detection (Priority: P1)

**Goal**: WhatsAppWatcher polls WhatsApp Web every 30s and captures messages containing urgent keywords

**Independent Test**: Send WhatsApp message with keyword "urgent" → verify WHATSAPP_<contact>_<timestamp>.md appears in Needs_Action/ within 30 seconds

### Implementation for User Story 2

- [ ] T042 [P] [US2] Add playwright dependency to pyproject.toml: `uv add playwright`
- [ ] T043 [P] [US2] Install Playwright browsers: `playwright install chromium`
- [ ] T044 [P] [US2] Create src/watchers/whatsapp_watcher.py with WhatsAppWatcher class extending BaseWatcher
- [ ] T045 [US2] Implement Playwright persistent browser context with session persistence to WHATSAPP_SESSION_PATH
- [ ] T046 [US2] Implement first-run flow: headless=False → user scans QR → session saved → subsequent runs headless=True
- [ ] T047 [US2] Implement keyword filtering: ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing']
- [ ] T048 [US2] Implement check_for_updates() to poll WhatsApp Web every 30 seconds
- [ ] T049 [US2] Implement create_action_file() to write Needs_Action/WHATSAPP_<contact>_<timestamp>.md with Schema A frontmatter
- [ ] T050 [US2] Add DRY_RUN guard: log "[DRY RUN] Would create WHATSAPP_*.md" without writing file
- [ ] T051 [US2] Add error handling: playwright.TimeoutError → log + wait 60s before retry
- [ ] T052 [US2] Add error handling: browser crash → relaunch browser, log [ERROR] with traceback
- [ ] T053 [US2] Add console output: [WhatsAppWatcher] Starting... | [WhatsAppWatcher] Found N urgent | [ERROR] Browser crashed: <traceback>
- [ ] T054 [US2] Create src/actions/whatsapp_action.py with WhatsAppAction class (send message via browser-mcp)
- [ ] T055 [US2] Implement browser-mcp integration in whatsapp_action.py (navigate, click, fill for WhatsApp Web)
- [ ] T056 [US2] Add rate limiting to whatsapp_action.py: check MAX_WHATSAPPS_PER_HOUR before send
- [ ] T057 [US2] Test WhatsAppWatcher first run: headless=False → manual QR scan → verify session saved
- [ ] T058 [US2] Test WhatsAppWatcher subsequent runs: headless=True → session loaded → polling works
- [ ] T059 [US2] Test keyword detection: send message with "urgent" → verify WHATSAPP_*.md created
- [ ] T060 [US2] Test non-keyword message: send message without keywords → verify no file created
- [ ] T061 [US2] Configure PM2 for whatsapp_watcher: `pm2 start ecosystem.config.js --only whatsapp_watcher`
- [ ] T062 [US2] Verify WhatsAppWatcher runs continuously: `pm2 logs whatsapp_watcher` shows polling every 30s

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - File Drop Processing (Priority: P2)

**Goal**: FilesystemWatcher monitors Inbox/ for new files and copies them to Needs_Action/ with sidecar .md

**Independent Test**: Copy a .pdf file to Inbox/ → verify file is copied to Needs_Action/ with sidecar .md file within 5 seconds

### Implementation for User Story 3

- [ ] T063 [P] [US3] Add watchdog dependency to pyproject.toml: `uv add watchdog`
- [ ] T064 [P] [US3] Create src/watchers/filesystem_watcher.py with DropFolderHandler class extending FileSystemEventHandler
- [ ] T065 [US3] Implement on_created() event handler to detect new files in Inbox/
- [ ] T066 [US3] Implement file type filtering: only .pdf, .docx, .csv, .txt, .md (others silently ignored)
- [ ] T067 [US3] Implement file copy logic: copy from Inbox/ to Needs_Action/
- [ ] T068 [US3] Implement sidecar .md creation with Schema A frontmatter (type=file_drop, from=user, subject=filename)
- [ ] T069 [US3] Add DRY_RUN guard: log "[DRY RUN] Would copy <file> to Needs_Action/" without copying
- [ ] T070 [US3] Add error handling: PermissionError → log [ERROR] cannot read file
- [ ] T071 [US3] Add error handling: shutil.Error → log + create ALERT_filesystem.md
- [ ] T072 [US3] Add console output: [FilesystemWatcher] Watching Inbox/ | [FilesystemWatcher] New file: <filename>
- [ ] T073 [US3] Test FilesystemWatcher in dry-run mode: drop .pdf → verify log shows "[DRY RUN]" message
- [ ] T074 [US3] Test FilesystemWatcher in live mode: drop .pdf → verify file copied + sidecar .md created
- [ ] T075 [US3] Test unsupported file type: drop .exe → verify file silently ignored
- [ ] T076 [US3] Configure PM2 for filesystem_watcher: `pm2 start ecosystem.config.js --only filesystem_watcher`
- [ ] T077 [US3] Verify FilesystemWatcher runs continuously: `pm2 logs filesystem_watcher` shows instant detection

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Claude Task Planning (Priority: P1)

**Goal**: Orchestrator monitors Needs_Action/ and triggers Claude to create Plan.md files for each task

**Independent Test**: Place a Needs_Action file → verify PLAN_<taskname>.md is created in Plans/ with Schema B frontmatter

### Implementation for User Story 4

- [ ] T078 [P] [US4] Create src/orchestrator.py with Orchestrator class (folder monitoring, Claude trigger)
- [ ] T079 [US4] Implement Needs_Action/ folder monitoring in orchestrator.py (poll every 10s for new .md files)
- [ ] T080 [US4] Implement claim-by-move pattern: move file from Needs_Action/ to In_Progress/claude/ before processing
- [ ] T081 [US4] Implement Claude Code trigger command to process Needs_Action file
- [ ] T082 [US4] Implement Plan file generator: create Plans/PLAN_<taskname>.md with Schema B frontmatter
- [ ] T083 [US4] Implement approval detection: if Plan requires approval → create Pending_Approval/<TYPE>_<task>.md
- [ ] T084 [US4] Implement /Approved/ folder watcher: detect moved files → trigger MCP action
- [ ] T085 [US4] Implement file move logic: Approved/ → execute action → move to Done/
- [ ] T086 [US4] Implement file move logic: Rejected/ → log rejection → stop processing
- [ ] T087 [US4] Add DRY_RUN guard to orchestrator: log intended actions without executing
- [ ] T088 [US4] Test orchestrator: place EMAIL_*.md in Needs_Action/ → verify PLAN_*.md created in Plans/
- [ ] T089 [US4] Test approval workflow: create approval request → move to Approved/ → verify action triggered
- [ ] T090 [US4] Test rejection workflow: create approval request → move to Rejected/ → verify logged + stopped
- [ ] T091 [US4] Configure PM2 for orchestrator: `pm2 start ecosystem.config.js --only orchestrator`
- [ ] T092 [US4] Verify orchestrator runs continuously: `pm2 logs orchestrator` shows folder monitoring

**Checkpoint**: At this point, User Stories 1-4 should all work with full planning + approval workflow

---

## Phase 7: User Story 5 - Human-in-the-Loop Approval Workflow (Priority: P1)

**Goal**: System enforces approval for sensitive actions (emails, payments, posts) via file-move workflow

**Independent Test**: Move approval request file to Approved/ → verify action executes; move to Rejected/ → verify logged + stopped

### Implementation for User Story 5

- [ ] T093 [P] [US5] Create src/actions/approval_generator.py with ApprovalGenerator class (creates Schema C frontmatter)
- [ ] T094 [US5] Implement approval expiry logic: 24 hours from creation → auto-reject + move to Rejected/
- [ ] T095 [US5] Implement payment approval flow: amount, recipient, reason fields in Schema C
- [ ] T096 [US5] Implement email approval flow: to, subject, body, attachment fields in Schema C
- [ ] T097 [US5] Implement social post approval flow: platform, content, scheduled_time fields in Schema C
- [ ] T098 [US5] Implement file delete approval flow: file_path, reason fields in Schema C
- [ ] T099 [US5] Test $0 test payment: create approval → move to Approved/ → verify payment logged (no real charge)
- [ ] T100 [US5] Test email approval: create approval → move to Approved/ → verify test email sent
- [ ] T101 [US5] Test approval expiry: create approval → wait 24 hours → verify auto-rejected
- [ ] T102 [US5] Test rejection: create approval → move to Rejected/ → verify logged + stopped

**Checkpoint**: At this point, User Story 5 approval workflow should be fully functional

---

## Phase 8: User Story 6 - Ralph Wiggum Iteration Control (Priority: P2)

**Goal**: Ralph Wiggum stop-hook limits Claude retries to 10 attempts to prevent infinite loops

**Independent Test**: Trigger a task that cannot complete → verify Ralph counter increments and ALERT created after 10 attempts

### Implementation for User Story 6

- [ ] T103 [P] [US6] Verify .qwen/hooks/stop.py is properly configured in Claude Code hook system
- [ ] T104 [US6] Implement TASK_FILE env var reading in stop.py (absolute path of current task .md)
- [ ] T105 [US6] Implement RALPH_COUNTER env var reading in stop.py (default "0")
- [ ] T106 [US6] Implement Done/ check: if task file exists in Done/ → print "[Ralph] Task complete ✅" → sys.exit(0)
- [ ] T107 [US6] Implement counter increment: if counter < 10 → counter += 1 → sys.exit(1) (triggers re-run)
- [ ] T108 [US6] Implement max reached logic: if counter >= 10 → write ALERT_ralph_max_<task>.md → sys.exit(0)
- [ ] T109 [US6] Implement console output: "[Ralph] Attempt <n>/10 — retrying..." on retry
- [ ] T110 [US6] Test Ralph Wiggum with successful task: move file to Done/ → verify "[Ralph] Task complete ✅"
- [ ] T111 [US6] Test Ralph Wiggum with failing task: trigger 10 retries → verify ALERT_ralph_max_*.md created
- [ ] T112 [US6] Verify RALPH_COUNTER resets on task change (new task → counter = 0)

**Checkpoint**: At this point, User Story 6 loop control should prevent infinite retries

---

## Phase 9: User Story 7 - CEO Briefing Generation (Priority: P3)

**Goal**: BriefingGenerator runs Sunday 11PM and creates Monday_Briefing.md with 6 required sections

**Independent Test**: Trigger briefing script → verify file created in Briefings/ with all 6 sections

### Implementation for User Story 7

- [ ] T113 [P] [US7] Create src/briefing_generator.py with BriefingGenerator class
- [ ] T114 [US7] Implement Sunday 11PM trigger via cron (Mac/Linux) or Task Scheduler (Windows)
- [ ] T115 [US7] Implement Business_Goals.md reader: extract Q1 targets, KPIs, subscription rules
- [ ] T116 [US7] Implement /Done/ files reader: filter by date range (current week)
- [ ] T117 [US7] Implement audit logs parser: extract revenue data from Logs/YYYY-MM-DD.json
- [ ] T118 [US7] Implement Executive Summary section generator
- [ ] T119 [US7] Implement Revenue section generator: This Week, MTD, Trend
- [ ] T120 [US7] Implement Completed Tasks section generator: list from /Done/ files
- [ ] T121 [US7] Implement Bottlenecks section generator: compare expected vs actual completion times
- [ ] T122 [US7] Implement Proactive Suggestions section generator: subscription audit, upcoming deadlines
- [ ] T123 [US7] Implement Footer with timestamp and version
- [ ] T124 [US7] Create src/actions/subscription_analyzer.py with SubscriptionAnalyzer class (audit logic for cost optimization)
- [ ] T125 [US7] Test briefing with sample data: create mock /Done/ files → verify briefing generated with all 6 sections
- [ ] T126 [US7] Test briefing with no tasks: verify "No tasks completed this week" message
- [ ] T127 [US7] Test cron trigger (Mac/Linux): `0 23 * * 0 cd /path && python src/briefing_generator.py`
- [ ] T128 [US7] Test Task Scheduler trigger (Windows): create task for Sunday 11PM

**Checkpoint**: At this point, User Story 7 CEO briefing should be fully functional

---

## Phase 10: Security & Cross-Cutting Concerns

**Purpose**: Security hardening, audit logging, watchdog monitoring

- [ ] T129 [P] Create src/watchdog_monitor.py with ProcessMonitor class (health checks, auto-restart dead watchers)
- [ ] T130 [P] Implement disk space monitoring in watchdog_monitor.py (alert if <1GB free)
- [ ] T131 [P] Implement memory monitoring in watchdog_monitor.py (alert if >90% usage)
- [ ] T132 [P] Implement auto-restart logic: if process dead → pm2 restart → write ALERT_<n>_restarted.md
- [ ] T133 [P] Create AI_Employee_Vault/Dashboard.md with live metrics template (System Status, Revenue, Recent Activity, Bottlenecks, Upcoming Deadlines)
- [ ] T134 [P] Create AI_Employee_Vault/Company_Handbook.md with 10 rules of engagement
- [ ] T135 [P] Create AI_Employee_Vault/Business_Goals.md with Q1 targets, KPI table, subscription rules
- [ ] T136 [P] Implement Dashboard.md auto-update after every task completion (file moved to Done/)
- [ ] T137 [P] Verify DRY_RUN=true flag is present in ALL action scripts (gmail_watcher, whatsapp_watcher, filesystem_watcher, email_action, whatsapp_action)
- [ ] T138 [P] Verify rate_limiter.check_and_increment() is called in ALL action scripts before external calls
- [ ] T139 [P] Verify @with_retry decorator is applied to ALL external API calls (Gmail API, WhatsApp Web, email-mcp, browser-mcp)
- [ ] T140 [P] Verify logging.basicConfig() is configured in entry points only (orchestrator, each watcher's __main__)
- [ ] T141 [P] Verify all except blocks use logger.error() with exc_info=True
- [ ] T142 [P] Verify no secrets in code: grep for GMAIL_CLIENT, BANK_API, WHATSAPP_SESSION → should only be in .env
- [ ] T143 [P] Test watchdog: kill gmail_watcher process → verify auto-restart + ALERT written
- [ ] T144 [P] Test disk full scenario: simulate low disk → verify ALERT_disk_full.md written + watchers paused

---

## Phase 11: LinkedIn Auto-Post (Priority: P2)

**Goal**: LinkedIn poster with HITL approval, scheduled via cron/Task Scheduler

- [ ] T145 [P] Create src/actions/linkedin_poster.py with LinkedInPoster class extending BaseAction
- [ ] T146 [P] Implement browser-mcp integration for LinkedIn Web (navigate to linkedin.com, click post button, fill content)
- [ ] T147 [P] Implement social post template in AI_Employee_Vault/Plans/social_posts/
- [ ] T148 [P] Add HITL approval gate: create Pending_Approval/SOCIAL_POST_<timestamp>.md before posting
- [ ] T149 [P] Implement scheduled posting via cron (Mac/Linux) or Task Scheduler (Windows)
- [ ] T150 [P] Add rate limiting: MAX_SOCIAL_POSTS_PER_DAY = 5
- [ ] T151 [P] Test LinkedIn poster in dry-run mode: verify log shows intended post without posting
- [ ] T152 [P] Test LinkedIn poster in live mode: create approval → move to Approved/ → verify post published

---

## Phase 12: Documentation & Polish

**Purpose**: README, security docs, demo script, hackathon submission

- [ ] T153 [P] Write README.md with setup instructions, architecture diagram, quickstart guide
- [ ] T154 [P] Write SECURITY.md with credential handling disclosure, rate limits, permission boundaries
- [ ] T155 [P] Create demo script: end-to-end invoice flow scenario (WhatsApp → Plan → Approval → Email → Done)
- [ ] T156 [P] Record 5-10 min demo video showing full system operation
- [ ] T157 [P] Submit to hackathon form with demo video link
- [ ] T158 [P] Run full end-to-end test: all 3 watchers → orchestrator → approval → action → log → dashboard
- [ ] T159 [P] Verify PM2 starts all 4 processes: `pm2 list` shows orchestrator, gmail_watcher, whatsapp_watcher, watchdog
- [ ] T160 [P] Verify all logs are written: `pm2 logs` shows output from all processes
- [ ] T161 [P] Verify audit logs are created: Logs/YYYY-MM-DD.json has entries for all actions
- [ ] T162 [P] Verify Dashboard.md is updated after task completion
- [ ] T163 [P] Code cleanup: remove unused imports, fix linting errors
- [ ] T164 [P] Run pytest on all test files (if tests were included)
- [ ] T165 [P] Final verification: DRY_RUN=false → run full flow → verify all components work together

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Security (Phase 10)**: Depends on all user stories being implemented
- **LinkedIn (Phase 11)**: Depends on Foundational + browser-mcp setup
- **Documentation (Phase 12)**: Depends on all features being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent of US1/US2
- **User Story 4 (P1)**: Can start after Foundational (Phase 2) - Depends on watchers creating Needs_Action files
- **User Story 5 (P1)**: Can start after US4 (orchestrator creates approval requests)
- **User Story 6 (P2)**: Can start after US4 (Ralph monitors Claude exits)
- **User Story 7 (P3)**: Can start after US4/US5 (needs /Done/ files and audit logs)

### Within Each User Story

- Models/config before services
- Services before endpoints/actions
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Setup Phase**: T001-T006 (tool installs) can all run in parallel
- **Foundational Phase**: T011-T017 (config, audit_logger, retry_handler, rate_limiter, base classes) can run in parallel
- **User Story 1**: T023-T024 (gmail_watcher.py + dependencies) can run in parallel
- **User Story 2**: T042-T044 (playwright install + whatsapp_watcher.py) can run in parallel
- **User Story 3**: T063-T064 (watchdog + filesystem_watcher.py) can run in parallel
- **User Story 4**: T078-T079 (orchestrator.py + folder monitoring) can run in parallel
- **Security Phase**: T129-T132 (watchdog components) can run in parallel
- **Different user stories** can be worked on in parallel by different developers

---

## Parallel Example: User Story 1

```bash
# Launch all setup tasks for User Story 1 together:
Task: "Create src/watchers/gmail_watcher.py with GmailWatcher class"
Task: "Add google-api-python-client dependencies to pyproject.toml"

# These can run in parallel because:
# - gmail_watcher.py creation doesn't depend on dependencies being installed yet
# - Dependencies can be added to pyproject.toml while code is being written
```

---

## Parallel Example: User Story 2

```bash
# Launch all setup tasks for User Story 2 together:
Task: "Add playwright dependency to pyproject.toml"
Task: "Install Playwright browsers: playwright install chromium"
Task: "Create src/watchers/whatsapp_watcher.py with WhatsAppWatcher class"

# T042 (add dependency) and T044 (create watcher) can run in parallel
# T043 (install browsers) must wait for T042 but can run while T044 is in progress
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T010)
2. Complete Phase 2: Foundational (T011-T022) - CRITICAL checkpoint
3. Complete Phase 3: User Story 1 (T023-T041)
4. **STOP and VALIDATE**: Test GmailWatcher independently
   - Send test email → verify Needs_Action/EMAIL_*.md created within 120s
   - Verify Schema A frontmatter is correct
   - Verify DRY_RUN mode works
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (Email Processing) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (WhatsApp Urgent) → Test independently → Deploy/Demo
4. Add User Story 3 (File Drops) → Test independently → Deploy/Demo
5. Add User Story 4 (Claude Planning) → Test independently → Deploy/Demo
6. Add User Story 5 (HITL Approval) → Test independently → Deploy/Demo
7. Add User Story 6 (Ralph Wiggum) → Test independently
8. Add User Story 7 (CEO Briefing) → Test independently
9. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (GmailWatcher)
   - Developer B: User Story 2 (WhatsAppWatcher)
   - Developer C: User Story 3 (FilesystemWatcher)
3. Stories complete and integrate independently
4. Reconvene for User Story 4 (Orchestrator) - needs all watchers working

---

## Task Summary

| Phase | Description | Task Count | Story |
|-------|-------------|------------|-------|
| Phase 1 | Setup | 10 | N/A |
| Phase 2 | Foundational | 12 | N/A |
| Phase 3 | User Story 1 - Email Processing | 19 | US1 |
| Phase 4 | User Story 2 - WhatsApp Urgent | 21 | US2 |
| Phase 5 | User Story 3 - File Drops | 15 | US3 |
| Phase 6 | User Story 4 - Claude Planning | 15 | US4 |
| Phase 7 | User Story 5 - HITL Approval | 10 | US5 |
| Phase 8 | User Story 6 - Ralph Wiggum | 10 | US6 |
| Phase 9 | User Story 7 - CEO Briefing | 16 | US7 |
| Phase 10 | Security & Cross-Cutting | 16 | N/A |
| Phase 11 | LinkedIn Auto-Post | 8 | N/A |
| Phase 12 | Documentation & Polish | 13 | N/A |
| **Total** | | **165** | |

**Note**: This task list includes 165 granular tasks. For a Silver Tier (20-30 hrs) scope, prioritize:
- **MVP (Required)**: Phases 1-6 (T001-T092) = 92 tasks
- **Silver Tier**: MVP + Phases 7-8 (T093-T112) = 112 tasks
- **Gold Tier**: Silver + Phases 9-10 (T113-T144) = 144 tasks
- **Platinum Tier**: All 165 tasks

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- DRY_RUN=true by default - set to false only after manual end-to-end test passes
- All watchers run via PM2: `pm2 start ecosystem.config.js`
- All logs in AI_Employee_Vault/Logs/
- Vault content exclusively in AI_Employee_Vault/
