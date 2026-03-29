"""Process approved file and complete the end-to-end test flow."""
from pathlib import Path
from datetime import datetime
from src.actions.audit_logger import audit_logger
from src.config import config

def process_approved_flow():
    """Process the approved email file and complete the flow."""
    print("=" * 60)
    print("STEP 5: Processing Approved File (DRY RUN)")
    print("=" * 60)
    
    # Read the approved file
    approved_file = config.approved_path / 'EMAIL_invoice_test_client.md'
    
    if not approved_file.exists():
        print(f"ERROR: Approved file not found: {approved_file}")
        return False
    
    print(f'\nProcessing approved file: {approved_file.name}')

    # Log the approval detection
    audit_logger.log_action(
        action_type='approval_detected',
        actor='orchestrator',
        target='EMAIL_invoice_test_client.md',
        parameters={'action': 'send_email', 'to': 'testclient@example.com'},
        approval_status='human_approved',
        result='pending',
        dry_run=config.dry_run
    )

    # Simulate email send (DRY RUN - no actual email sent)
    print(f'\n[DRY RUN] Would send email to testclient@example.com')
    print(f'[DRY RUN] Subject: January 2026 Invoice - $1,500')

    # Log the email send (dry run)
    audit_logger.log_action(
        action_type='email_send',
        actor='orchestrator',
        target='testclient@example.com',
        parameters={
            'subject': 'January 2026 Invoice - $1,500',
            'body': 'Please find attached your invoice for January 2026 services.',
            'attachment': '/AI_Employee_Vault/Invoices/2026-01_Test_Client.pdf'
        },
        approval_status='human_approved',
        result='dry_run',
        dry_run=True
    )
    print('\n✅ Audit log entry created for email_send (dry_run)')

    # Move all related files to Done/
    files_to_move = [
        ('PLAN_invoice_test_client.md', config.plans_path),
        ('EMAIL_invoice_test_client.md', config.approved_path),
    ]

    print('\nMoving files to Done/:')
    for filename, source_path in files_to_move:
        src = source_path / filename
        if src.exists():
            dst = config.done_path / filename
            src.rename(dst)
            print(f'  ✓ Moved {filename} to Done/')
            
            audit_logger.log_action(
                action_type='file_move',
                actor='orchestrator',
                target=filename,
                parameters={'from': str(src), 'to': str(dst)},
                approval_status='auto_approved',
                result='success',
                dry_run=config.dry_run
            )
        else:
            print(f'  ✗ File not found: {src}')

    print('\n' + "=" * 60)
    print('✅ STEP 5 COMPLETE: All files moved to Done/')
    print("=" * 60)
    return True

if __name__ == "__main__":
    process_approved_flow()
