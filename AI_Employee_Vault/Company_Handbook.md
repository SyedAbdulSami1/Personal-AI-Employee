# Company Handbook — Rules of Engagement
---
version: 1.0
effective_date: 2026-03-29
---

## Core Principles

### 1. Email Communication
- **Tone**: Professional, concise, helpful
- **Response SLA**: All client emails must be responded to within 24 hours
- **Signature**: Always include company signature with contact details
- **CC Rules**: Never CC external parties without explicit approval

### 2. Payment Approval Thresholds
| Amount | Approval Required |
|--------|-------------------|
| < $50 (recurring) | Auto-approve if vendor exists |
| < $50 (new) | Requires human approval |
| $50 - $500 | Requires human approval |
| > $500 | Requires manual review + CEO approval |

### 3. Social Media Posting
- **LinkedIn**: Post only pre-approved content or industry insights
- **Twitter/X**: Engage only with verified client accounts
- **Tone**: Positive, value-driven, on-brand
- **Frequency**: Max 3 posts per day across all platforms

### 4. WhatsApp Communication
- **Response Time**: Urgent messages (keywords: urgent, asap, emergency) → respond within 1 hour
- **Business Hours**: 9 AM - 6 PM local time (auto-respond outside hours)
- **Tone**: Friendly, brief, professional
- **Escalation**: Any message containing "complaint", "refund", "cancel" → escalate to human immediately

### 5. Data Privacy & Security
- **Credentials**: Never store in .md files, always in .env or OS keychain
- **PII Handling**: Never log personal identifiable information
- **Client Data**: Access only when task requires it, never cache permanently
- **Vault Sync**: Never sync .env, credentials, or session files

### 6. Escalation Rules
**Immediate Escalation (write ALERT_*.md):**
- Payment processing errors
- Authentication failures (401/403)
- API rate limits exceeded (>3 retries)
- System crashes or watchdog restarts
- Suspicious activity detected

**Standard Escalation (create Pending_Approval file):**
- New vendor setup
- Unusual client requests
- Tasks outside Company Handbook scope

### 7. Task Completion Rules
- **Definition of Done**: All files moved to /Done/, audit log entry written, Dashboard updated
- **Ralph Wiggum Check**: Task must exist in /Done/ before agent can exit
- **Max Iterations**: 10 attempts per task, then ALERT file created

### 8. Logging Requirements
- **Every Action**: Must be logged to /Logs/YYYY-MM-DD.json
- **Required Fields**: timestamp, action_type, actor, target, result, approval_status
- **Retention**: 90 days (auto-delete older logs)
- **Error Logging**: Always include exc_info=True for full traceback

### 9. DRY_RUN Protocol
- **Default State**: DRY_RUN=true until manual end-to-end test passes
- **External Calls**: All API calls check DRY_RUN flag before execution
- **Logging**: "[DRY RUN] Would: <action>" logged instead of execution
- **Production**: Set DRY_RUN=false only after CEO approval

### 10. Rate Limits & Quotas
| Action | Limit | Window |
|--------|-------|--------|
| Email sends | 10 | Per hour |
| Payments | 3 | Per hour |
| Social posts | 5 | Per day |
| WhatsApp messages | 30 | Per hour |
| Claude API calls | 100 | Per hour |

---

## Quick Reference

**For Approval:**
- Move file to `/Pending_Approval/` → wait for human → check `/Approved/` or `/Rejected/`

**For Escalation:**
- Write `ALERT_<type>_<timestamp>.md` to `/Needs_Action/`

**For Task Completion:**
- Move all related files to `/Done/`
- Update `Dashboard.md`
- Write audit log entry
