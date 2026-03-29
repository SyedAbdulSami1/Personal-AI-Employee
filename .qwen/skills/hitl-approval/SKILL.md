---
name: hitl-approval
description: This skill should be used when implementing, managing, or debugging Human-in-the-Loop (HITL) approval workflows. Use when creating approval requests, processing approved actions, or managing the Pending_Approval → Approved → Done flow.
---

# HITL Approval Skill

## Purpose

Manage Human-in-the-Loop (HITL) approval workflows that ensure user review before critical actions. All payments, new contact communications, bulk sends, and file deletions require explicit human approval via file movement in the vault.

## When to Use This Skill

✅ User says: "Add approval for..." or "This needs my approval..."
✅ Creating new action types that require human review
✅ Processing files from Approved/ folder
✅ Managing Pending_Approval/ folder workflow
✅ Implementing auto-approval thresholds
✅ Debugging approval flow issues

---

## HITL Architecture

### Folder Flow

```
Needs_Action/          ← Watchers write here
    ↓
Orchestrator reads → Qwen creates Plan
    ↓
Plans/               ← Qwen writes PLAN_*.md
    ↓
Pending_Approval/    ← Qwen writes approval requests
    ↓
User reviews & moves to → Approved/    ← User approval (triggers action)
                     or → Rejected/    ← User rejection (logs + stops)
    ↓
Done/                ← Completed tasks (Ralph Wiggum checks this)
```

### Approval Categories

| Category | Auto-Approve | Require Approval |
|----------|--------------|------------------|
| **Email replies** | Known contacts | New contacts, bulk sends |
| **Payments** | < $50 recurring | All new payees, > $100 |
| **Social media** | Scheduled posts | Replies, DMs, new posts |
| **File operations** | Create, read | Delete, move outside vault |
| **WhatsApp sends** | Known contacts | New contacts, group messages |

---

## Schema C: Approval Request

**File:** `Pending_Approval/<TYPE>_<task>_<timestamp>.md`

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

### Field Requirements

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | enum | Yes | Always `approval_request` |
| `action` | enum | Yes | Action type being requested |
| `amount` | float | Conditional | Dollar amount (payments only) |
| `recipient` | string | Yes | Target of action |
| `reason` | string | Yes | One sentence justification |
| `created` | ISO 8601 | Yes | Creation timestamp |
| `expires` | ISO 8601 | Yes | Expiration (+24 hours) |
| `status` | enum | Yes | `pending`, `approved`, `rejected`, `expired` |
| `plan_ref` | string | Yes | Reference to Plan file |

---

## Creating Approval Requests

### Action Builder Pattern

```python
"""Base pattern for all actions requiring approval."""

from pathlib import Path
from datetime import datetime, timedelta
import yaml
import logging
logger = logging.getLogger(__name__)


class BaseAction(ABC):
    requires_approval = True  # Override in subclass
    
    def __init__(self, config, audit_logger):
        self.config = config
        self.audit_logger = audit_logger
        self.vault_path = Path(config.vault_path)
    
    def create_approval_request(self, action_file: Dict[str, Any]) -> str:
        """
        Create Pending_Approval/<TYPE>_<task>.md using Schema C.
        
        Returns path to created file.
        """
        timestamp = datetime.utcnow()
        expires = timestamp + timedelta(hours=24)
        
        # Generate filename
        action_type = action_file.get('action', 'UNKNOWN').upper()
        task_id = action_file.get('id', hashlib.md5(str(timestamp).encode()).hexdigest()[:8])
        filename = f"{action_type}_{task_id}_{timestamp.strftime('%Y-%m-%d')}.md"
        
        filepath = self.vault_path / "Pending_Approval" / filename
        
        # Build content
        content = f"""---
type: approval_request
action: {action_file.get('action')}
recipient: {action_file.get('recipient')}
reason: {action_file.get('reason', 'Action required per Company_Handbook.md')}
created: {timestamp.isoformat()}Z
expires: {expires.isoformat()}Z
status: pending
plan_ref: {action_file.get('plan_ref', 'unknown')}
---

## Action Details
{action_file.get('content', 'No details provided')}

## To APPROVE: Move this file to /Approved/
## To REJECT:  Move this file to /Rejected/
"""
        
        # DRY_RUN check
        if self.config.dry_run:
            logger.info("[DRY RUN] Would create approval request: %s", filename)
            return str(filepath)
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        filepath.write_text(content, encoding='utf-8')
        logger.info("Created approval request: %s", filename)
        
        return str(filepath)
```

### Example: Email Action

```python
class EmailAction(BaseAction):
    action_type = "send_email"
    requires_approval = True
    
    def should_require_approval(self, action_file: Dict[str, Any]) -> bool:
        """
        Check if this email requires approval.
        
        Rules from Company_Handbook.md:
        - New contacts → always approve
        - Bulk sends (>10 recipients) → always approve
        - Known contacts → auto-approve
        """
        recipient = action_file.get('to', '')
        recipients = action_file.get('recipients', [recipient])
        
        # Bulk send check
        if len(recipients) > 10:
            logger.info("Bulk send (%d recipients) requires approval", len(recipients))
            return True
        
        # New contact check
        known_contacts = self._load_known_contacts()
        for r in recipients:
            if r not in known_contacts:
                logger.info("New contact (%s) requires approval", r)
                return True
        
        # Known contact → auto-approve
        logger.info("Known contact (%s) - auto-approve", recipient)
        return False
    
    async def execute(self, action_file: Dict[str, Any]):
        """Execute email send with approval check."""
        
        # Check if approval needed
        if self.should_require_approval(action_file):
            # Create approval request and STOP
            approval_path = self.create_approval_request(action_file)
            return {
                'success': True,
                'status': 'pending_approval',
                'approval_file': approval_path
            }
        
        # Auto-approved → send email
        if self.config.dry_run:
            logger.info("[DRY RUN] Would send email to: %s", action_file['to'])
            return {'success': True, 'dry_run': True}
        
        # Send email
        result = await self._send_email(action_file)
        
        # Log to audit
        self.audit_logger.log_action(
            action_type='send_email',
            actor='qwen_agent',
            target=action_file['to'],
            parameters={'subject': action_file['subject']},
            approval_status='system',  # Auto-approved
            approved_by='system',
            result='success' if result else 'failure',
            dry_run=False
        )
        
        return result
```

### Example: Payment Action

```python
class PaymentAction(BaseAction):
    action_type = "payment"
    requires_approval = True
    
    def should_require_approval(self, action_file: Dict[str, Any]) -> bool:
        """
        Check if this payment requires approval.
        
        Rules from Company_Handbook.md:
        - All new payees → always approve
        - > $100 → always approve
        - < $50 recurring → auto-approve
        """
        amount = float(action_file.get('amount', 0))
        recipient = action_file.get('recipient', '')
        is_recurring = action_file.get('recurring', False)
        
        # New payee check
        known_payees = self._load_known_payees()
        if recipient not in known_payees:
            logger.info("New payee (%s) requires approval", recipient)
            return True
        
        # Amount check
        if amount > 100:
            logger.info("Payment > $100 ($%.2f) requires approval", amount)
            return True
        
        # Recurring small payment → auto-approve
        if is_recurring and amount < 50:
            logger.info("Recurring payment < $50 ($%.2f) - auto-approve", amount)
            return False
        
        # Default → require approval
        return True
    
    async def execute(self, action_file: Dict[str, Any]):
        """Execute payment with approval check."""
        
        # NEVER auto-retry payments - always require fresh approval for failures
        if self.should_require_approval(action_file):
            approval_path = self.create_approval_request(action_file)
            return {
                'success': True,
                'status': 'pending_approval',
                'approval_file': approval_path
            }
        
        # Auto-approved → process payment
        if self.config.dry_run:
            logger.info("[DRY RUN] Would pay $%s to: %s", 
                       action_file['amount'], action_file['recipient'])
            return {'success': True, 'dry_run': True}
        
        # Process payment (with retry disabled for payments)
        result = await self._process_payment(action_file)
        
        # Log to audit
        self.audit_logger.log_action(
            action_type='payment',
            actor='qwen_agent',
            target=action_file['recipient'],
            parameters={'amount': action_file['amount']},
            approval_status='system',
            approved_by='system',
            result='success' if result else 'failure',
            dry_run=False
        )
        
        return result
```

---

## Processing Approved Files

### Orchestrator Pattern

```python
"""Orchestrator monitors Approved/ and triggers actions."""

from pathlib import Path
import asyncio
import logging
logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self, config, action_handlers):
        self.config = config
        self.action_handlers = action_handlers  # Dict: action_type → handler
        self.vault_path = Path(config.vault_path)
        self.approved_dir = self.vault_path / "Approved"
        self.done_dir = self.vault_path / "Done"
    
    async def process_approved_files(self):
        """
        Monitor Approved/ folder and execute approved actions.
        Runs every 30 seconds.
        """
        logger.info("[Orchestrator] Checking Approved/ folder...")
        
        # Ensure directories exist
        self.approved_dir.mkdir(parents=True, exist_ok=True)
        self.done_dir.mkdir(parents=True, exist_ok=True)
        
        # Process all approved files
        for filepath in self.approved_dir.glob("*.md"):
            try:
                await self._process_single_file(filepath)
            except Exception as e:
                logger.error("Error processing %s: %s", filepath, e, exc_info=True)
    
    async def _process_single_file(self, filepath: Path):
        """Process a single approved file."""
        logger.info("[Orchestrator] Processing: %s", filepath.name)
        
        # Parse frontmatter
        content = filepath.read_text(encoding='utf-8')
        parts = content.split('---', 2)
        
        if len(parts) < 2:
            logger.error("Invalid file format: %s", filepath)
            return
        
        frontmatter = yaml.safe_load(parts[1])
        body = parts[2] if len(parts) > 2 else ''
        
        # Check expiration
        expires = frontmatter.get('expires')
        if expires and datetime.fromisoformat(expires.rstrip('Z')) < datetime.utcnow():
            logger.warning("Approval expired: %s", filepath)
            self._mark_expired(filepath)
            return
        
        # Get action type
        action_type = frontmatter.get('action')
        if not action_type:
            logger.error("Missing action field: %s", filepath)
            return
        
        # Find handler
        handler = self.action_handlers.get(action_type)
        if not handler:
            logger.error("No handler for action type: %s", action_type)
            return
        
        # Execute action
        action_file = {**frontmatter, 'body': body, 'filename': filepath.name}
        result = await handler.execute(action_file)
        
        # Handle result
        if result.get('success'):
            logger.info("Action successful: %s", filepath.name)
            
            # Move to Done/
            done_path = self.done_dir / filepath.name
            filepath.rename(done_path)
            logger.info("Moved to Done/: %s", filepath.name)
            
            # Update Dashboard.md
            self._update_dashboard(filepath.name, result)
            
        elif result.get('status') == 'pending_approval':
            # Already in approval flow
            pass
            
        else:
            logger.error("Action failed: %s - %s", filepath.name, result.get('error'))
            # Keep in Approved/ for retry
    
    def _mark_expired(self, filepath: Path):
        """Mark approval as expired."""
        rejected_dir = self.vault_path / "Rejected"
        rejected_dir.mkdir(parents=True, exist_ok=True)
        
        new_path = rejected_dir / f"EXPIRED_{filepath.name}"
        filepath.rename(new_path)
        
        logger.info("Moved expired file to Rejected/: %s", new_path)
    
    def _update_dashboard(self, filename: str, result: Dict):
        """Update Dashboard.md with completed action."""
        dashboard_path = self.vault_path / "Dashboard.md"
        
        if dashboard_path.exists():
            content = dashboard_path.read_text()
            
            # Add to recent activity
            timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M')
            activity_line = f"- [{timestamp}] {filename} completed\n"
            
            # Insert after "## Recent Activity" header
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line == "## Recent Activity":
                    lines.insert(i + 1, activity_line)
                    break
            
            dashboard_path.write_text('\n'.join(lines))
```

---

## Auto-Approval Thresholds

### Configuration

**File:** `src/config.py`

```python
from dataclasses import dataclass, field
import os

@dataclass
class Config:
    # ... other fields ...
    
    # Auto-approval thresholds
    auto_approve_email_known_contacts: bool = True
    auto_approve_payment_recurring_max: float = 50.0
    auto_approve_payment_one_time_max: float = 0.0  # Never auto-approve one-time
    auto_approve_social_scheduled: bool = True
    auto_approve_bulk_max_recipients: int = 10
```

### Implementation

```python
class AutoApprovalChecker:
    def __init__(self, config: Config):
        self.config = config
        self.known_contacts = self._load_known_contacts()
        self.known_payees = self._load_known_payees()
    
    def should_auto_approve(self, action_type: str, action_file: Dict) -> bool:
        """Check if action qualifies for auto-approval."""
        
        if action_type == 'send_email':
            return self._check_email_auto_approve(action_file)
        
        elif action_type == 'payment':
            return self._check_payment_auto_approve(action_file)
        
        elif action_type == 'social_post':
            return self._check_social_auto_approve(action_file)
        
        elif action_type == 'whatsapp_send':
            return self._check_whatsapp_auto_approve(action_file)
        
        return False
    
    def _check_email_auto_approve(self, action_file: Dict) -> bool:
        """Email auto-approval rules."""
        recipients = action_file.get('recipients', [action_file.get('to')])
        
        # Bulk send check
        if len(recipients) > self.config.auto_approve_bulk_max_recipients:
            return False
        
        # Known contact check
        for r in recipients:
            if r not in self.known_contacts:
                return False
        
        return self.config.auto_approve_email_known_contacts
    
    def _check_payment_auto_approve(self, action_file: Dict) -> bool:
        """Payment auto-approval rules."""
        amount = float(action_file.get('amount', 0))
        is_recurring = action_file.get('recurring', False)
        recipient = action_file.get('recipient', '')
        
        # New payee → never auto-approve
        if recipient not in self.known_payees:
            return False
        
        # Recurring payment under threshold
        if is_recurring and amount <= self.config.auto_approve_payment_recurring_max:
            return True
        
        # One-time payment (never auto-approve by default)
        return amount <= self.config.auto_approve_payment_one_time_max
```

---

## Expiration Handling

### Check Expiration

```python
def check_expiration(filepath: Path) -> str:
    """
    Check if approval request has expired.
    
    Returns: 'valid', 'expired', 'expiring_soon'
    """
    content = filepath.read_text()
    parts = content.split('---', 2)
    
    if len(parts) < 2:
        return 'invalid'
    
    frontmatter = yaml.safe_load(parts[1])
    expires = frontmatter.get('expires')
    
    if not expires:
        return 'valid'  # No expiration set
    
    expires_dt = datetime.fromisoformat(expires.rstrip('Z'))
    now = datetime.utcnow()
    
    if expires_dt < now:
        return 'expired'
    
    # Check if expiring in next hour
    if expires_dt < now + timedelta(hours=1):
        return 'expiring_soon'
    
    return 'valid'
```

### Process Expiring Files

```python
def process_expiring_approvals(self):
    """Check all Pending_Approval/ files for expiration."""
    pending_dir = self.vault_path / "Pending_Approval"
    
    for filepath in pending_dir.glob("*.md"):
        status = check_expiration(filepath)
        
        if status == 'expired':
            logger.warning("Approval expired: %s", filepath)
            self._mark_expired(filepath)
            
            # Alert user
            self._write_expiration_alert(filepath)
        
        elif status == 'expiring_soon':
            logger.info("Approval expiring soon: %s", filepath)
            # Optionally send reminder
```

---

## Audit Logging

### Log Approval Events

```python
# When creating approval request
audit_logger.log_action(
    action_type='approval_request_created',
    actor='qwen_agent',
    target=filepath.name,
    parameters={'action': action_type, 'recipient': recipient},
    approval_status='pending',
    approved_by='none',
    result='pending',
    dry_run=False
)

# When user approves
audit_logger.log_action(
    action_type='approval_granted',
    actor='human',
    target=filepath.name,
    parameters={'action': action_type},
    approval_status='human_approved',
    approved_by='human',
    result='success',
    dry_run=False
)

# When user rejects
audit_logger.log_action(
    action_type='approval_rejected',
    actor='human',
    target=filepath.name,
    parameters={'action': action_type, 'reason': 'user_rejected'},
    approval_status='rejected',
    approved_by='human',
    result='skipped',
    dry_run=False
)
```

---

## Testing HITL Flow

### Test Scenarios

```python
def test_approval_flow():
    """Test complete HITL approval flow."""
    
    # 1. Create action requiring approval
    action_file = {
        'action': 'send_email',
        'to': 'new_contact@example.com',  # New contact → requires approval
        'subject': 'Test',
        'content': 'Test content'
    }
    
    # 2. Execute action (should create approval request)
    action = EmailAction(config, audit_logger)
    result = asyncio.run(action.execute(action_file))
    
    assert result['status'] == 'pending_approval'
    assert 'approval_file' in result
    
    # 3. Simulate user approval (move file to Approved/)
    approval_file = Path(result['approval_file'])
    approved_file = approved_dir / approval_file.name
    approval_file.rename(approved_file)
    
    # 4. Orchestrator processes approved file
    orchestrator = Orchestrator(config, {'send_email': action})
    asyncio.run(orchestrator.process_approved_files())
    
    # 5. Verify file moved to Done/
    done_file = done_dir / approved_file.name
    assert done_file.exists()
```

---

## Reference Files

- [Schema C Template](../vault-schema/reference/schema-c.md)
- [Audit Logger](../../src/actions/audit_logger.py)
- [Config Class](../../src/config.py)
- [Company_Handbook.md](../../AI_Employee_Vault/Company_Handbook.md)
- [Orchestrator](../../src/orchestrator.py)

---

## Examples

### Example 1: New Contact Email

**Scenario:** Client sends WhatsApp asking for invoice → Qwen creates email draft → Requires approval (new contact)

**Flow:**
1. WhatsAppWatcher detects message → Creates `Needs_Action/WHATSAPP_*.md`
2. Qwen processes → Creates `Plans/PLAN_invoice_*.md`
3. Qwen creates approval request → `Pending_Approval/EMAIL_invoice_*.md`
4. User reviews → Moves to `Approved/`
5. Orchestrator detects → EmailAction sends
6. File moved to `Done/`

### Example 2: Recurring Payment

**Scenario:** Monthly software subscription ($15/month, known payee) → Auto-approved

**Flow:**
1. Qwen creates payment action → `action_type=payment, amount=15, recurring=true`
2. PaymentAction.should_require_approval() → Returns False (known payee, < $50, recurring)
3. Payment processed immediately
4. Audit log: `approval_status=system, approved_by=system`

### Example 3: Large One-Time Payment

**Scenario:** Vendor invoice $500 (new payee) → Requires approval

**Flow:**
1. Qwen creates payment action → `amount=500, recipient=new_vendor@company.com`
2. PaymentAction.should_require_approval() → Returns True (new payee, > $100)
3. Approval request created → `Pending_Approval/PAYMENT_*.md`
4. User reviews → Can approve, reject, or request changes
5. If approved → Payment processed
6. If rejected → Moved to `Rejected/`, logged

---

## Anti-Patterns (Avoid These)

❌ **Auto-approving new contacts** - Always require approval for unknown recipients
❌ **Auto-approving large payments** - > $100 always requires approval
❌ **Auto-retrying failed payments** - Always require fresh approval after failure
❌ **No expiration** - All approvals must expire in 24 hours
❌ **Silent rejections** - Log rejected approvals to audit
❌ **Skipping audit log** - Always log approval events
❌ **No DRY_RUN check** - Always guard approval creation
❌ **Hardcoded thresholds** - Use Config class for thresholds

---

## Success Metrics

✅ All required actions create approval requests
✅ Auto-approval follows Company_Handbook.md rules
✅ Approval requests expire in 24 hours
✅ User can approve by moving to Approved/
✅ User can reject by moving to Rejected/
✅ Approved actions execute automatically
✅ All approval events logged to audit
✅ Dashboard.md updated after completion

---

**Created from:** AI Employee Hackathon - HITL Approval Patterns
**Reference:** QWEN.md Section 5 (Vault File Schemas), Company_Handbook.md
