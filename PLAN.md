# Personal AI Employee - Implementation Plan
## Silver Tier Target (20-30 hours)

---

### PHASE 0: Environment Setup (2-3 hours)
- [ ] Install Claude Code (latest version)
- [ ] Install Obsidian v1.10.6+
- [ ] Install Python 3.13
- [ ] Install Node.js v24+
- [ ] Install PM2 globally (`npm install -g pm2`)
- [ ] Create Obsidian vault: `AI_Employee_Vault`
- [ ] Setup UV Python project: `uv init --pyproject`
- [ ] Create `.env` file with required secrets (add to .gitignore)
- [ ] Initialize specifyplus project structure
- [ ] Create initial `.gitignore` file
- [ ] Verify all installations work correctly

**Verification**: All tools installed and accessible from command line
**Common Failures**:
- Python version mismatch - use pyenv or official installer
- Node.js permission issues - use nvm or run as admin
- Obsidian plugin conflicts - start with clean vault

---

### PHASE 1: Vault Foundation (2-3 hours)
- [ ] Create folder structure in AI_Employee_Vault:
  - Inbox/
  - Needs_Action/
  - In_Progress/claude/
  - Plans/
  - Pending_Approval/
  - Approved/
  - Rejected/
  - Done/
  - Logs/pm2/
  - Briefings/
  - Accounting/
- [ ] Create Dashboard.md template with status sections
- [ ] Create Company_Handbook.md with 10 rules of engagement
- [ ] Create Business_Goals.md with Q1 targets and KPIs
- [ ] Test Claude Code read/write access to vault
- [ ] Create initial audit log structure in Logs/

**Verification**: Claude can create, read, and move files between vault folders
**Common Failures**:
- Permission errors on Windows - run as administrator
- Path spacing issues - use quotes around paths
- Obsidian indexing delays - wait for vault to load completely

---

### PHASE 2: Perception Layer — Watchers (4-6 hours)
- [ ] Create `src/config.py` with Config dataclass
- [ ] Create `src/actions/audit_logger.py` with AuditLogger class
- [ ] Create `src/actions/retry_handler.py` with @with_retry decorator
- [ ] Create `src/actions/rate_limiter.py` with RateLimiter class
- [ ] Create `src/watchers/base_watcher.py` with BaseWatcher ABC
- [ ] Create `src/watchers/gmail_watcher.py` with GmailWatcher
- [ ] Create `src/watchers/whatsapp_watcher.py` with WhatsAppWatcher
- [ ] Create `src/watchers/filesystem_watcher.py` with DropFolderHandler
- [ ] Test each watcher independently in dry-run mode
- [ ] Configure PM2 ecosystem.config.js for 4 watcher processes
- [ ] Start watchers with PM2 and verify they're running

**Verification**: Each watcher logs activity and creates appropriate files in Needs_Action/
**Common Failures**:
- Gmail OAuth scopes incomplete - add required Google API scopes
- WhatsApp session persistence - ensure Chrome user data dir is set
- Watchdog permission errors - run as admin or adjust folder permissions
- Import path issues - ensure PYTHONPATH includes src/

---

### PHASE 3: Reasoning Loop (3-4 hours)
- [ ] Create `.claude/mcp.json` with email, filesystem, and browser MCP configs
- [ ] Create `.claude/hooks/stop.py` for Ralph Wiggum loop mechanism
- [ ] Create `src/orchestrator.py` with Orchestrator class
- [ ] Create `src/watchdog_monitor.py` with ProcessMonitor class
- [ ] Test end-to-end flow: create test .md in Needs_Action → Claude processes → moves to Done
- [ ] Verify Ralph Wiggum counter increments and exits appropriately
- [ ] Test approval workflow: Needs_Action → Pending_Approval → (manual move to Approved) → action execution

**Verification**: Files move through the complete workflow pipeline correctly
**Common Failures**:
- MCP server connection failures - verify Node.js paths and permissions
- Ralph Wiggum counter not persisting - check environment variable handling
- Orchestrator missing file events - adjust watchdog patterns and debounce timing
- Approval workflow stalling - verify file move operations are atomic

---

### PHASE 4: Action Layer — MCP Servers (4-6 hours)
- [ ] Setup email-mcp server for Gmail integration
- [ ] Setup browser-mcp server for Playwright automation
- [ ] Create email action service in `src/actions/email_action.py`
- [ ] Create browser action service in `src/actions/browser_action.py`
- [ ] Implement Human-in-the-Loop approval workflow in orchestrator
- [ ] Test: create approval file in Pending_Approval → move to Approved → MCP executes → result logged
- [ ] Verify audit logging captures all actions with proper metadata
- [ ] Test error handling and retry mechanisms

**Verification**: Approved actions execute successfully and create appropriate audit log entries
**Common Failures**:
- MCP server startup failures - verify Node.js dependencies and scripts
- Gmail API rate limits - implement exponential backoff in retry handler
- Browser automation timing issues - add explicit waits and timeouts
- Credential expiration - implement refresh token handling

---

### PHASE 5: LinkedIn Integration (2-3 hours)
- [ ] Research LinkedIn API options (official API vs browser automation)
- [ ] Implement LinkedInPoster class extending BaseAction
- [ ] Create `/Plans/social_posts/` folder for LinkedIn content
- [ ] Add LinkedIn posting to approval workflow
- [ ] Test: create LinkedIn post file in Plans/social_posts/ → approval → posting → log
- [ ] Verify content formatting and image handling (if applicable)

**Verification**: LinkedIn posts appear on target profile with correct content
**Common Failures**:
- LinkedIn API approval process - may need to use browser automation instead
- Authentication token expiration - implement refresh mechanism
- Content formatting issues - LinkedIn has specific post formatting rules
- Rate limiting - respect LinkedIn's API limits

---

### PHASE 6: Audit & Monitoring (2-3 hours)
- [ ] Implement JSON audit logging in `audit_logger.py` (daily log files)
- [ ] Create `src/watchdog_monitor.py` with health checks and auto-restart
- [ ] Setup 90-day log rotation in AuditLogger.__init__
- [ ] Add rate limiting: max 10 emails/hr, max 3 payments/hr
- [ ] Test log rotation and retention policies
- [ ] Verify watchdog restarts crashed processes
- [ ] Test rate limiter blocks excess requests

**Verification**: Audit logs contain complete action history; watchdog maintains process health
**Common Failures**:
- Log file locking issues - use proper file handling modes
- Watchdog false positives - adjust health check intervals and thresholds
- Rate limiter clock issues - use monotonic time for interval calculations
- Disk space exhaustion - verify log rotation actually deletes old files

---

### PHASE 7: CEO Briefing Feature (2-3 hours)
- [ ] Implement Sunday night trigger (cron on Unix, Task Scheduler on Windows)
- [ ] Create `src/briefing_generator.py` with BriefingGenerator class
- [ ] Claude reads Business_Goals.md + transaction data from logs
- [ ] Generate Monday_Briefing.md in /Briefings/ with:
  - Progress toward Q1 goals
  - Key metrics from audit logs
  - Completed vs pending tasks
  - Upcoming deadlines
- [ ] Test briefing generation with sample data
- [ ] Verify formatting is clear and actionable

**Verification**: Monday briefing appears in Briefings folder with relevant insights
**Common Failures**:
- Timezone issues - ensure cron runs at correct local time
- Data aggregation errors - handle missing or malformed log entries
- Template formatting - keep briefing readable and scannable
- Empty data handling - gracefully handle periods with no activity

---

### PHASE 8: Testing & Documentation (2-3 hours)
- [ ] End-to-end test: WhatsApp invoice request → detection → plan → approval → email send → log
- [ ] Write comprehensive README.md with:
  - Architecture overview
  - Setup instructions
  - Usage guidelines
  - Troubleshooting FAQ
- [ ] Record 5-10 minute demo video showing:
  - System startup
  - File detection and processing
  - Approval workflow
  - Action execution
  - Audit logging
- [ ] Create security disclosure document covering:
  - Credential handling
  - Data retention policies
  - Access controls
  - Encryption at rest (if applicable)
- [ ] Run full system test for 2+ hours to verify stability

**Verification**: Complete workflow functions reliably with proper logging and error handling
**Common Failures**:
- Demo video recording issues - use built-in OS recording tools
- Documentation outdated - update as changes are made
- Test data contamination - use separate test vault for validation
- Performance degradation - monitor memory usage over extended runs

---

## TOTAL ESTIMATED TIME: 22-30 hours

### Dependencies Notes:
- All Python dependencies managed via UV and pyproject.toml
- Node.js dependencies managed via npm and package.json (for MCP servers)
- Environment variables stored in .env (never committed)
- Vault structure is the single source of truth for all data

### Success Criteria:
- System runs autonomously for extended periods
- All watchers detect and process incoming items
- Approval workflow functions correctly for all action types
- Audit logs capture complete action history
- CEO briefing generates meaningful insights weekly
- Recovery mechanisms work for common failure scenarios