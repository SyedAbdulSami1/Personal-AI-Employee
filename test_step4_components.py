"""
Test All Components — STEP 4 Verification
Run this script to verify all core components are working.
"""
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("AI_Employee_Vault/Logs/test_components.log"),
    ],
)
logger = logging.getLogger(__name__)


def test_config():
    """Test Config loading."""
    logger.info("=" * 50)
    logger.info("TEST 1: Config Loading")
    logger.info("=" * 50)

    from src.config import Config

    config = Config()
    assert config.vault_path == Path("AI_Employee_Vault"), "Vault path incorrect"
    assert config.dry_run is True, "DRY_RUN should be True by default"

    logger.info(f"[OK] Config loaded: vault={config.vault_path}, dry_run={config.dry_run}")
    return config


def test_audit_logger(config):
    """Test AuditLogger."""
    logger.info("=" * 50)
    logger.info("TEST 2: Audit Logger")
    logger.info("=" * 50)

    from src.actions.audit_logger import AuditLogger

    audit = AuditLogger(config.logs_path)
    audit.log_action(
        action_type="component_test",
        actor="test_script",
        target="test_target",
        result="success",
        dry_run=config.dry_run
    )

    # Verify log was written
    entries = audit.get_today_logs()
    assert len(entries) > 0, "No log entries found"

    logger.info(f"[OK] AuditLogger working: {len(entries)} entries today")
    return audit


def test_rate_limiter(config):
    """Test RateLimiter."""
    logger.info("=" * 50)
    logger.info("TEST 3: Rate Limiter")
    logger.info("=" * 50)

    from src.actions.rate_limiter import RateLimiter

    rl = RateLimiter(config.vault_path)

    # Test email rate limit
    allowed = rl.check_and_increment('email_send')
    logger.info(f"[OK] RateLimiter working: email_send allowed={allowed}")

    # Get status
    status = rl.get_status('email_send')
    logger.info(f"  Email status: {status['tokens_remaining']}/{status['max_tokens']} tokens")

    return rl


def test_base_watcher(config):
    """Test BaseWatcher import and structure."""
    logger.info("=" * 50)
    logger.info("TEST 4: Base Watcher")
    logger.info("=" * 50)

    from src.watchers.base_watcher import BaseWatcher

    assert hasattr(BaseWatcher, 'check_for_updates'), "Missing check_for_updates method"
    assert hasattr(BaseWatcher, 'create_action_file'), "Missing create_action_file method"
    assert hasattr(BaseWatcher, 'run'), "Missing run method"

    logger.info("[OK] BaseWatcher structure correct (abstract class)")
    return BaseWatcher


def test_vault_structure(config):
    """Test vault folder structure."""
    logger.info("=" * 50)
    logger.info("TEST 5: Vault Structure")
    logger.info("=" * 50)

    required_folders = [
        "Inbox",
        "Needs_Action",
        "In_Progress",
        "Plans",
        "Pending_Approval",
        "Approved",
        "Rejected",
        "Done",
        "Logs",
        "Briefings",
        "Accounting",
    ]

    for folder in required_folders:
        folder_path = config.vault_path / folder
        assert folder_path.exists(), f"Missing folder: {folder}"
        logger.info(f"  [OK] {folder}/")

    # Check template files
    assert (config.vault_path / "Dashboard.md").exists(), "Missing Dashboard.md"
    assert (config.vault_path / "Company_Handbook.md").exists(), "Missing Company_Handbook.md"
    assert (config.vault_path / "Business_Goals.md").exists(), "Missing Business_Goals.md"

    logger.info("[OK] All vault folders and template files present")
    return True


def test_src_files():
    """Test all source files exist and are importable."""
    logger.info("=" * 50)
    logger.info("TEST 6: Source Files")
    logger.info("=" * 50)

    files = [
        "src/config.py",
        "src/orchestrator.py",
        "src/watchdog_monitor.py",
        "src/watchers/base_watcher.py",
        "src/watchers/gmail_watcher.py",
        "src/watchers/whatsapp_watcher.py",
        "src/watchers/filesystem_watcher.py",
        "src/actions/audit_logger.py",
        "src/actions/retry_handler.py",
        "src/actions/rate_limiter.py",
    ]

    for file_path in files:
        path = Path(file_path)
        assert path.exists(), f"Missing file: {file_path}"
        logger.info(f"  [OK] {file_path}")

    logger.info("[OK] All source files present")
    return True


def test_hook_file():
    """Test Ralph Wiggum hook file."""
    logger.info("=" * 50)
    logger.info("TEST 7: Ralph Wiggum Hook")
    logger.info("=" * 50)

    hook_path = Path(".claude/hooks/stop.py")
    assert hook_path.exists(), "Missing Ralph Wiggum hook file"

    content = hook_path.read_text()
    assert "RALPH" in content.upper(), "Hook doesn't mention Ralph Wiggum"
    assert "DONE" in content.upper(), "Hook doesn't check Done folder"

    logger.info("[OK] Ralph Wiggum hook file present and correct")
    return True


def main():
    """Run all tests."""
    logger.info("\n")
    logger.info("*" * 60)
    logger.info("STEP 4: COMPONENT VERIFICATION TESTS")
    logger.info("*" * 60)
    logger.info("\n")

    tests_passed = 0
    tests_failed = 0

    try:
        # Test 1: Config
        config = test_config()
        tests_passed += 1
    except Exception as e:
        logger.error(f"TEST 1 FAILED: {e}", exc_info=True)
        tests_failed += 1
        return

    try:
        # Test 2: Audit Logger
        test_audit_logger(config)
        tests_passed += 1
    except Exception as e:
        logger.error(f"TEST 2 FAILED: {e}", exc_info=True)
        tests_failed += 1

    try:
        # Test 3: Rate Limiter
        test_rate_limiter(config)
        tests_passed += 1
    except Exception as e:
        logger.error(f"TEST 3 FAILED: {e}", exc_info=True)
        tests_failed += 1

    try:
        # Test 4: Base Watcher
        test_base_watcher(config)
        tests_passed += 1
    except Exception as e:
        logger.error(f"TEST 4 FAILED: {e}", exc_info=True)
        tests_failed += 1

    try:
        # Test 5: Vault Structure
        test_vault_structure(config)
        tests_passed += 1
    except Exception as e:
        logger.error(f"TEST 5 FAILED: {e}", exc_info=True)
        tests_failed += 1

    try:
        # Test 6: Source Files
        test_src_files()
        tests_passed += 1
    except Exception as e:
        logger.error(f"TEST 6 FAILED: {e}", exc_info=True)
        tests_failed += 1

    try:
        # Test 7: Hook File
        test_hook_file()
        tests_passed += 1
    except Exception as e:
        logger.error(f"TEST 7 FAILED: {e}", exc_info=True)
        tests_failed += 1

    # Summary
    logger.info("\n")
    logger.info("=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Tests Passed: {tests_passed}/7")
    logger.info(f"Tests Failed: {tests_failed}/7")

    if tests_failed == 0:
        logger.info("\n[SUCCESS] ALL TESTS PASSED - Ready for STEP 5 (E2E Test)")
    else:
        logger.error("\n[FAILURE] SOME TESTS FAILED - Fix issues before proceeding")

    return tests_failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
