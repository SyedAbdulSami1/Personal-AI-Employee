---
name: action-builder
description: This skill should be used when creating new Action scripts that extend BaseAction. Use when user needs to execute tasks (send emails, post to social media, make payments, call APIs) based on action files in Needs_Action/ or Approved/ folders.
---

# Action Builder Skill

## Purpose

Create new Action scripts that follow the established BaseAction pattern. Actions are responsible for:
- Reading action files from `AI_Employee_Vault/Approved/` or `Needs_Action/`
- Executing external operations (API calls, file operations, messages)
- Respecting DRY_RUN and HITL (Human-in-the-Loop) rules
- Logging all actions to audit logs
- Running as PM2-managed processes or triggered by orchestrator

## When to Use This Skill

✅ User says: "Add an action to..."
✅ User needs to: Send emails, post to social media, make payments, call APIs
✅ User wants to: Automate responses, trigger workflows, update external systems
✅ Existing actions (LinkedInPoster, EmailAction) don't cover the use case

❌ Don't use for: Creating Watchers (use watcher-creator skill)
❌ Don't use for: Modifying BaseAction unless refactoring

---

## Action Architecture

```
src/actions/
├── base_action.py           ← BaseAction(ABC) - DO NOT MODIFY
├── audit_logger.py          ← AuditLogger (singleton)
├── retry_handler.py         ← @with_retry decorator
├── rate_limiter.py          ← RateLimiter (singleton)
├── linkedin_poster.py       ← LinkedInPoster(BaseAction)
└── <new_action>.py          ← Create new actions here
```

### BaseAction Interface

Every action MUST extend `BaseAction` and implement:

```python
from abc import ABC, abstractmethod
import logging
logger = logging.getLogger(__name__)

class NewAction(BaseAction):
    """
    Docstring: What this action does and when it's triggered.
    """
    
    # Required class attributes
    action_type: str  # Matches approval_request type in frontmatter
    requires_approval: bool  # True = needs HITL before execution
    
    @abstractmethod
    async def execute(self, action_file: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the action based on action_file contents.
        Returns result dict with success status and metadata.
        
        MUST check self.dry_run before any external operation.
        MUST call self.audit.log_action() after execution.
        """
        pass
```

---

## Implementation Process

### Step 1: Understand the Action

Ask the user:
1. **What operation?** (send email, post to social, make payment, update CRM)
2. **What triggers it?** (Approved file, specific action_type, scheduled)
3. **What external API?** (Gmail, LinkedIn, Stripe, custom REST)
4. **Does it need approval?** (payments, new contacts, bulk sends = always yes)
5. **What are the rate limits?** (max per hour/day)

### Step 2: Check for Existing Libraries

Search for Python packages:
```bash
# Example searches
pip search linkedin-api
pip search stripe
pip search sendgrid
```

**Preferred libraries:**
- Official SDKs first
- Well-maintained (last commit <6 months)
- High download count
- Good documentation

### Step 3: Create the Action File

**File location:** `src/actions/<action_name>.py`

**Template:**
```python
"""
<Action Name> Action - Executes <action type> operations.

Trigger: action_type = "<action_type>" in Approved/*.md
Requires Approval: yes|no
Rate Limit: <N> per <time period>
Output: Updates action file status + audit log
"""

import os
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from base_action import BaseAction
from audit_logger import AuditLogger
from retry_handler import with_retry
from rate_limiter import RateLimiter
from config import Config

import logging
logger = logging.getLogger(__name__)


class <ActionName>Action(BaseAction):
    """
    Executes <action type> operations.
    
    Triggered when:
    - action_type = "<action_type>" in Approved/*.md
    - All required fields present in frontmatter
    
    Requires approval: <yes|no>
    Rate limit: <N> per <time period>
    """
    
    action_type = "<action_type>"
    requires_approval = <True|False>
    
    def __init__(self, config: Config, audit_logger: AuditLogger):
        super().__init__(config, audit_logger)
        self.client = self._init_client()
        
        # Rate limiter (if applicable)
        self.rate_limiter = RateLimiter(
            max_calls=<N>,
            period=<seconds>
        )
    
    def _init_client(self):
        """Initialize the <service> API client."""
        # Load credentials from config (NOT os.getenv directly)
        api_key = self.config.<SERVICE>_API_KEY
        # Initialize and return client
        pass
    
    @with_retry(max_attempts=3, base_delay=1, max_delay=60)
    async def execute(self, action_file: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the <action type> action.
        
        Args:
            action_file: Parsed markdown with frontmatter
            
        Returns:
            Dict with keys: success, message, metadata, error
        """
        logger.info("[%s] Executing action for: %s", self.action_type, action_file.get('filename'))
        
        # Extract required fields from frontmatter
        recipient = action_file.get('recipient')
        subject = action_file.get('subject')
        content = action_file.get('content')
        
        # Validate required fields
        if not recipient:
            return {
                'success': False,
                'message': 'Missing required field: recipient',
                'error': 'ValidationError'
            }
        
        # DRY_RUN check - MUST be at top
        if self.config.dry_run:
            logger.info("[DRY RUN] %s would send to: %s", self.action_type, recipient)
            return {
                'success': True,
                'message': f'[DRY RUN] Would send to {recipient}',
                'dry_run': True
            }
        
        # Rate limit check
        if not self.rate_limiter.check_and_increment():
            logger.warning("[%s] Rate limit exceeded", self.action_type)
            return {
                'success': False,
                'message': 'Rate limit exceeded',
                'error': 'RateLimitError'
            }
        
        try:
            # Execute the action
            result = await self._send_action(
                recipient=recipient,
                subject=subject,
                content=content
            )
            
            # Log to audit
            self.audit_logger.log_action(
                action_type=self.action_type,
                actor='qwen_agent',
                target=recipient,
                parameters={'subject': subject},
                approval_status='human_approved',
                approved_by='human',
                result='success',
                dry_run=False
            )
            
            logger.info("[%s] Successfully sent to: %s", self.action_type, recipient)
            
            return {
                'success': True,
                'message': f'Sent to {recipient}',
                'metadata': result
            }
            
        except Exception as e:
            logger.error("[%s] Error executing: %s", self.action_type, e, exc_info=True)
            
            # Log error to audit
            self.audit_logger.log_action(
                action_type=self.action_type,
                actor='qwen_agent',
                target=recipient,
                parameters={'subject': subject},
                approval_status='human_approved',
                approved_by='human',
                result='failure',
                error=str(e),
                dry_run=False
            )
            
            return {
                'success': False,
                'message': str(e),
                'error': type(e).__name__
            }
    
    async def _send_action(self, recipient: str, subject: str, content: str) -> Dict[str, Any]:
        """
        Internal method to execute the actual API call.
        Implement API-specific logic here.
        
        Returns:
            API response dict
        """
        pass


if __name__ == "__main__":
    from config import Config
    from audit_logger import AuditLogger
    
    config = Config()
    audit = AuditLogger(config)
    action = <ActionName>Action(config, audit)
    
    # Test with sample action file
    test_file = {
        'filename': 'TEST_ACTION.md',
        'recipient': 'test@example.com',
        'subject': 'Test Subject',
        'content': 'Test content'
    }
    
    result = asyncio.run(action.execute(test_file))
    print(f"Result: {result}")
```

---

## Action Categories & Approval Rules

### Category 1: Always Requires Approval
```python
requires_approval = True
```

**Examples:**
- Payments (any amount to new payee, >$100 to existing)
- Emails to new contacts
- Social media posts (non-scheduled)
- File deletions
- Bulk sends (>10 recipients)

### Category 2: Auto-Approve Under Threshold
```python
requires_approval = True  # But system auto-approves under threshold

# Threshold check in orchestrator:
if action.amount < 50 and action.recurring:
    auto_approve = True
```

**Examples:**
- Recurring payments <$50
- Email replies to known contacts
- Scheduled social media posts

### Category 3: No Approval Needed
```python
requires_approval = False
```

**Examples:**
- Logging actions
- Moving files within vault
- Updating Dashboard.md
- Internal notifications

---

## HITL (Human-in-the-Loop) Flow

### Step 1: Create Approval Request

```python
def create_approval_request(self, action_file: Dict[str, Any]) -> str:
    """
    Create Pending_Approval/<TYPE>_<task>.md using Schema C.
    
    Schema C frontmatter:
    ---
    type: approval_request
    action: <action_type>
    amount: <dollar amount>
    recipient: <email/phone/handle>
    reason: <one sentence>
    created: <ISO 8601>
    expires: <ISO 8601, +24 hours>
    status: pending
    plan_ref: <plan filename>
    ---
    """
    timestamp = datetime.utcnow()
    expires = timestamp.replace(hour=timestamp.hour + 24)
    
    filename = f"{self.action_type.upper()}_{action_file.get('id', 'unknown')}.md"
    filepath = self.vault_path / "Pending_Approval" / filename
    
    content = f"""---
type: approval_request
action: {self.action_type}
recipient: {action_file.get('recipient')}
reason: {action_file.get('reason', 'Action required')}
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
    
    if self.config.dry_run:
        logger.info("[DRY RUN] Would create approval request: %s", filename)
        return str(filepath)
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding='utf-8')
    
    return str(filepath)
```

### Step 2: Wait for User Action

User must:
- **APPROVE**: Move file to `Approved/`
- **REJECT**: Move file to `Rejected/`

Orchestrator monitors `Approved/` folder and triggers action.

### Step 3: Execute After Approval

```python
# In orchestrator.py
def process_approved_files(self):
    approved_dir = self.vault_path / "Approved"
    
    for filepath in approved_dir.glob("*.md"):
        action_file = self._parse_frontmatter(filepath)
        
        # Find appropriate action handler
        action_type = action_file.get('action')
        handler = self.action_handlers.get(action_type)
        
        if handler:
            result = asyncio.run(handler.execute(action_file))
            
            if result['success']:
                # Move to Done/
                done_dir = self.vault_path / "Done"
                filepath.rename(done_dir / filepath.name)
```

---

## Testing Checklist

### Unit Tests
- [ ] `_init_client()` returns valid client
- [ ] `execute()` respects DRY_RUN
- [ ] `execute()` calls rate_limiter.check_and_increment()
- [ ] `execute()` logs to audit_logger
- [ ] Missing fields return error dict
- [ ] Retry decorator wraps external calls

### Integration Tests
- [ ] Action executes when triggered from Approved/
- [ ] Approval request created in Pending_Approval/
- [ ] Success moves file to Done/
- [ ] Failure logs error + keeps file in Approved/
- [ ] Rate limit blocks after threshold

### Error Handling
- [ ] Network errors trigger retry
- [ ] Auth 401/403 logs ERROR + ALERT
- [ ] Rate limit returns RateLimitError
- [ ] Validation errors return clear message

---

## Common Action Patterns

### Pattern 1: Email Send (SMTP/API)
```python
async def _send_action(self, recipient: str, subject: str, content: str):
    # Using SendGrid API
    message = Mail(
        from_email='noreply@company.com',
        to_emails=recipient,
        subject=subject,
        plain_text_content=content
    )
    
    response = self.client.send(message)
    return {'message_id': response.headers.get('X-Message-Id')}
```

### Pattern 2: Social Media Post
```python
async def _send_action(self, content: str, image_url: Optional[str] = None):
    # Using LinkedIn API
    post_data = {
        'author': f'urn:li:person:{self.config.LINKEDIN_PERSON_URN}',
        'lifecycleState': 'PUBLISHED',
        'specificContent': {
            'com.linkedin.ugc.ShareContent': {
                'shareCommentary': {'text': content},
                'media': []
            }
        },
        'visibility': 'PUBLIC'
    }
    
    if image_url:
        # Upload media first
        media = await self._upload_media(image_url)
        post_data['specificContent']['com.linkedin.ugc.ShareContent']['media'].append(media)
    
    response = self.client.post('/ugcPosts', json=post_data)
    return {'post_id': response.json()['id']}
```

### Pattern 3: Payment (Stripe)
```python
async def _send_action(self, recipient: str, amount: float, description: str):
    # Create payout
    payout = self.client.payouts.create(
        amount=int(amount * 100),  # cents
        currency='usd',
        method='instant',
        destination_data={
            'email': recipient
        },
        description=description
    )
    
    return {'payout_id': payout.id, 'status': payout.status}
```

### Pattern 4: REST API Call (Generic)
```python
async def _send_action(self, endpoint: str, method: str, payload: Dict):
    response = self.session.request(
        method=method,
        url=f'{self.config.<SERVICE>_BASE_URL}/{endpoint}',
        json=payload
    )
    response.raise_for_status()
    return response.json()
```

---

## Rate Limiting

All actions MUST implement rate limiting:

```python
from rate_limiter import RateLimiter

# In __init__
self.rate_limiter = RateLimiter(
    max_calls=10,      # Max calls
    period=3600        # Per seconds (1 hour)
)

# In execute()
if not self.rate_limiter.check_and_increment():
    logger.warning("[%s] Rate limit exceeded", self.action_type)
    return {'success': False, 'message': 'Rate limit exceeded'}
```

**Default limits from Company_Handbook.md:**
```python
MAX_EMAILS_PER_HOUR = 10
MAX_PAYMENTS_PER_HOUR = 3
MAX_SOCIAL_POSTS_PER_DAY = 5
```

---

## Error Recovery

All actions MUST use `@with_retry` decorator:

```python
from retry_handler import with_retry

@with_retry(max_attempts=3, base_delay=1, max_delay=60)
async def execute(self, action_file: Dict[str, Any]):
    # External API calls here
    pass
```

**Error categories:**

| Error Type | Handler |
|------------|---------|
| Network timeout | Retry with backoff (1s→2s→4s) |
| Rate limit (429) | Retry after `Retry-After` header |
| Auth 401/403 | Log ERROR + ALERT + NEVER retry |
| Validation error | Return error dict, don't retry |
| API down | Log ERROR + keep in Approved/ for retry |

---

## Console Output Standards

Every action MUST log:

```
[<ActionName>] Executing action for: <filename>
[<ActionName>] Successfully sent to: <recipient>
[ERROR] <full message with traceback>
```

**Logging configuration:**
```python
# Entry point only (in __main__)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("AI_Employee_Vault/Logs/app.log"),
    ],
)

# In action file (top only)
import logging
logger = logging.getLogger(__name__)
```

---

## Reference Files

- [BaseAction Implementation](../../src/actions/base_action.py)
- [LinkedInPoster Example](../../src/actions/linkedin_poster.py)
- [Audit Logger](../../src/actions/audit_logger.py)
- [Retry Handler](../../src/actions/retry_handler.py)
- [Rate Limiter](../../src/actions/rate_limiter.py)
- [Schema C Template](../vault-schema/reference/schema-c.md)
- [Config Class](../../src/config.py)

---

## Examples

### Example 1: EmailAction

**User request:** "Send email replies to approved requests"

**Implementation:**
```python
class EmailAction(BaseAction):
    action_type = "send_email"
    requires_approval = True
    
    def _init_client(self):
        from sendgrid import SendGridAPIClient
        return SendGridAPIClient(self.config.SENDGRID_API_KEY)
    
    @with_retry(max_attempts=3, base_delay=1, max_delay=60)
    async def execute(self, action_file: Dict[str, Any]):
        if self.config.dry_run:
            logger.info("[DRY RUN] Would send email to: %s", action_file['to'])
            return {'success': True, 'dry_run': True}
        
        message = Mail(
            from_email='noreply@company.com',
            to_emails=action_file['to'],
            subject=action_file['subject'],
            plain_text_content=action_file['content']
        )
        
        if action_file.get('attachment'):
            # Handle attachment
            pass
        
        response = await asyncio.to_thread(self.client.send, message)
        
        self.audit_logger.log_action(
            action_type='send_email',
            actor='qwen_agent',
            target=action_file['to'],
            parameters={'subject': action_file['subject']},
            approval_status='human_approved',
            approved_by='human',
            result='success'
        )
        
        return {'success': True, 'message_id': response.headers.get('X-Message-Id')}
```

### Example 2: PaymentAction

**User request:** "Process payments to approved vendors"

**Implementation:**
```python
class PaymentAction(BaseAction):
    action_type = "payment"
    requires_approval = True
    
    def _init_client(self):
        import stripe
        stripe.api_key = self.config.STRIPE_SECRET_KEY
        return stripe
    
    @with_retry(max_attempts=3, base_delay=1, max_delay=60)
    async def execute(self, action_file: Dict[str, Any]):
        amount = float(action_file['amount'])
        recipient = action_file['recipient']
        
        # NEVER auto-retry payments - always require fresh approval
        if self.config.dry_run:
            logger.info("[DRY RUN] Would pay $%s to: %s", amount, recipient)
            return {'success': True, 'dry_run': True}
        
        try:
            payout = self.client.payouts.create(
                amount=int(amount * 100),
                currency='usd',
                method='instant',
                destination_data={'email': recipient},
                description=action_file.get('reason', 'Payment')
            )
            
            self.audit_logger.log_action(
                action_type='payment',
                actor='qwen_agent',
                target=recipient,
                parameters={'amount': amount},
                approval_status='human_approved',
                approved_by='human',
                result='success'
            )
            
            return {'success': True, 'payout_id': payout.id}
            
        except stripe.error.StripeError as e:
            logger.error("[Payment] Stripe error: %s", e, exc_info=True)
            return {'success': False, 'error': str(e)}
```

---

## Anti-Patterns (Avoid These)

❌ **Hardcoding credentials** - Always use `config.<FIELD>`
❌ **Scattered `os.getenv()` calls** - Config reads .env once
❌ **No DRY_RUN check** - Always guard external actions
❌ **Silent failures** - Always log with `exc_info=True`
❌ **No rate limiting** - Always check before external calls
❌ **Auto-retrying payments** - NEVER retry without fresh approval
❌ **Skipping audit log** - Always log_action() after execution
❌ **Copying BaseAction code** - Extend, don't copy

---

## Success Metrics

✅ New action follows BaseAction pattern exactly
✅ DRY_RUN mode works (no external calls when true)
✅ Rate limiting enforced
✅ Audit log entries created
✅ Approval requests use Schema C format
✅ Error handling covers all categories
✅ No credentials in code
✅ Retry decorator on all external calls

---

**Created from:** AI Employee Hackathon - Action Architecture
**Pattern proven:** LinkedInPoster, EmailAction, PaymentAction
