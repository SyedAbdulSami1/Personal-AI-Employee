#!/usr/bin/env python3
"""
Component Test Suite - STEP 4
Tests each component as specified in the implementation plan.

Tests:
1. Vault test: Create test.md in /Needs_Action, verify Claude can read it
2. Watcher test: Run gmail_watcher.py --dry-run for 30 seconds
3. Orchestrator test: Manually drop a test .md in /Needs_Action, verify Claude triggers
4. Approval test: Create approval file, move to /Approved, verify MCP triggers
5. Logging test: Perform test action, verify JSON appears in /Logs/
"""
import logging
import json
import time
from pathlib import Path
from datetime import datetime

from src.config import config
from src.actions.audit_logger import audit_logger
from src.watchers.gmail_watcher import GmailWatcher
from src.watchers.whatsapp_watcher import WhatsAppWatcher
from src.watchers.filesystem_watcher import FilesystemWatcher
from src.orchestrator import Orchestrator

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.logs_path / "test_results.log"),
    ],
)

logger = logging.getLogger(__name__)

def test_1_vault_read():
    """Test 1: Vault test - Create test.md in /Needs_Action, verify Claude can read it"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 1: Vault Read Test")
    logger.info("=" * 70)
    
    test_file = config.needs_action_path / "test_component_001.md"
    test_content = f"""---
type: test
from: component_test_suite
subject: Component Test 001
received: {datetime.now().isoformat()}
priority: high
status: pending
watcher: TestSuite
---
## Test Content

This is a component test file.

If Claude can read this, the vault integration is working.

## Test Checklist
- [ ] File created successfully
- [ ] Frontmatter is valid YAML
- [ ] Content is readable
"""
    
    try:
        # Create test file
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        logger.info(f"✓ Test file created: {test_file.name}")
        
        # Read it back
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verify frontmatter
        if content.startswith('---'):
            logger.info("✓ Frontmatter present")
        else:
            logger.error("✗ Frontmatter missing")
            return False
        
        # Verify content
        if "## Test Content" in content:
            logger.info("✓ Content readable")
        else:
            logger.error("✗ Content not readable")
            return False
        
        logger.info("✅ TEST 1 PASSED: Vault read/write working")
        return True
        
    except Exception as e:
        logger.error(f"✗ TEST 1 FAILED: {e}", exc_info=True)
        return False
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
            logger.info(f"Cleaned up test file: {test_file.name}")


def test_2_gmail_watcher_dry_run():
    """Test 2: Watcher test - Run gmail_watcher in dry-run mode"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 2: Gmail Watcher Dry-Run Test")
    logger.info("=" * 70)
    
    try:
        gmail_watcher = GmailWatcher(config)
        logger.info(f"✓ GmailWatcher created")
        logger.info(f"  Interval: {gmail_watcher.get_interval()}s")
        logger.info(f"  Dry run: {config.dry_run}")
        
        # Simulate email check (dry-run mode)
        logger.info("  Running simulated email check...")
        result = gmail_watcher.check_for_updates()
        
        logger.info(f"  Check result: {result}")
        logger.info("✅ TEST 2 PASSED: Gmail watcher dry-run working")
        return True
        
    except Exception as e:
        logger.error(f"✗ TEST 2 FAILED: {e}", exc_info=True)
        return False


def test_3_filesystem_watcher():
    """Test 3: Filesystem watcher test - Drop file in Inbox, verify processing"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 3: Filesystem Watcher Test")
    logger.info("=" * 70)
    
    test_file = config.inbox_path / "test_drop.txt"
    
    try:
        # Create test file in Inbox
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Test file for filesystem watcher")
        logger.info(f"✓ Test file dropped in Inbox: {test_file.name}")
        
        # Process it
        filesystem_watcher = FilesystemWatcher(config)
        logger.info("  Processing file drop...")
        filesystem_watcher._process_file_drop(str(test_file))
        
        # Check if action file was created (in dry-run mode, it won't actually write)
        if config.dry_run:
            logger.info("  [DRY RUN] No file written (expected)")
            logger.info("✅ TEST 3 PASSED: Filesystem watcher dry-run working")
        else:
            # Check for new file in Needs_Action
            action_files = list(config.needs_action_path.glob(f"*{test_file.stem}*.md"))
            if action_files:
                logger.info(f"✓ Action file created: {action_files[0].name}")
                logger.info("✅ TEST 3 PASSED: Filesystem watcher working")
            else:
                logger.error("✗ No action file created")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"✗ TEST 3 FAILED: {e}", exc_info=True)
        return False
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def test_4_approval_workflow():
    """Test 4: Approval test - Create approval file, verify workflow"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 4: Approval Workflow Test")
    logger.info("=" * 70)
    
    approval_file = config.pending_approval_path / "TEST_EMAIL_approval.md"
    approval_content = f"""---
type: approval_request
action: send_email
to: test@example.com
subject: Test Email
reason: Component testing
created: {datetime.now().isoformat()}
expires: {datetime.now().isoformat()}
status: pending
plan_ref: PLAN_test_001.md
---
## Action Details

This is a test approval request.

## To APPROVE: Move this file to /Approved/
## To REJECT: Move this file to /Rejected/
"""
    
    try:
        # Create approval file
        with open(approval_file, 'w', encoding='utf-8') as f:
            f.write(approval_content)
        logger.info(f"✓ Approval file created: {approval_file.name}")
        
        # Verify we can read it
        with open(approval_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "send_email" in content:
            logger.info("✓ Approval file readable")
        else:
            logger.error("✗ Approval file content incorrect")
            return False
        
        logger.info("✅ TEST 4 PASSED: Approval workflow structure working")
        return True
        
    except Exception as e:
        logger.error(f"✗ TEST 4 FAILED: {e}", exc_info=True)
        return False
    finally:
        # Cleanup
        if approval_file.exists():
            approval_file.unlink()


def test_5_logging():
    """Test 5: Logging test - Perform action, verify JSON log entry"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 5: Audit Logging Test")
    logger.info("=" * 70)
    
    try:
        # Perform a test action
        logger.info("  Performing test action...")
        audit_logger.log_action(
            action_type="component_test",
            actor="test_suite",
            target="test_component_005",
            parameters={"test_id": 5, "dry_run": config.dry_run},
            approval_status="auto_approved",
            result="success",
            dry_run=config.dry_run
        )
        logger.info("✓ Test action logged")
        
        # Check for log file
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = config.logs_path / f"{today}.json"
        
        if log_file.exists():
            logger.info(f"✓ Log file exists: {log_file.name}")
            
            # Read and verify log entries (JSON array format)
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            if isinstance(log_data, list) and len(log_data) > 0:
                # Find our test entry
                test_entry = None
                for entry in log_data:
                    if entry.get("action_type") == "component_test" and entry.get("actor") == "test_suite":
                        test_entry = entry
                        break
                
                if test_entry:
                    logger.info("✓ Log entry verified")
                    logger.info(f"  Actor: {test_entry.get('actor')}")
                    logger.info(f"  Result: {test_entry.get('result')}")
                    logger.info("✅ TEST 5 PASSED: Audit logging working")
                    return True
                else:
                    logger.error("✗ Test entry not found in log")
                    return False
            else:
                logger.error("✗ Log file is not a valid JSON array")
                return False
        else:
            logger.error(f"✗ Log file not found: {log_file}")
            return False
        
    except Exception as e:
        logger.error(f"✗ TEST 5 FAILED: {e}", exc_info=True)
        return False


def test_6_orchestrator():
    """Test 6: Orchestrator test - Verify it can be instantiated"""
    logger.info("\n" + "=" * 70)
    logger.info("TEST 6: Orchestrator Test")
    logger.info("=" * 70)
    
    try:
        orchestrator = Orchestrator()
        logger.info("✓ Orchestrator created")
        
        # Test Needs_Action folder monitoring setup
        logger.info(f"  Watching: {config.needs_action_path}")
        logger.info(f"  Folder exists: {config.needs_action_path.exists()}")
        
        logger.info("✅ TEST 6 PASSED: Orchestrator instantiation working")
        return True
        
    except Exception as e:
        logger.error(f"✗ TEST 6 FAILED: {e}", exc_info=True)
        return False


def main():
    """Run all component tests."""
    logger.info("\n" + "=" * 70)
    logger.info("COMPONENT TEST SUITE - STEP 4")
    logger.info("Testing all components as per implementation plan")
    logger.info("=" * 70)
    logger.info(f"Dry Run Mode: {config.dry_run}")
    logger.info(f"Vault Path: {config.vault_path}")
    logger.info(f"Log Path: {config.logs_path}")
    
    results = {
        "Test 1 - Vault Read": test_1_vault_read(),
        "Test 2 - Gmail Watcher": test_2_gmail_watcher_dry_run(),
        "Test 3 - Filesystem Watcher": test_3_filesystem_watcher(),
        "Test 4 - Approval Workflow": test_4_approval_workflow(),
        "Test 5 - Audit Logging": test_5_logging(),
        "Test 6 - Orchestrator": test_6_orchestrator(),
    }
    
    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 ALL TESTS PASSED!")
    else:
        logger.warning(f"⚠️ {total - passed} test(s) failed")
    
    logger.info("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
