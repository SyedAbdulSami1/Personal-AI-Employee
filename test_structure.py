#!/usr/bin/env python3
"""
Test script to verify the basic structure of the Personal AI Employee system.
"""
import sys
import os
from pathlib import Path

# Add src to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """Test that all core modules can be imported."""
    try:
        from src.config import config
        print("[PASS] Config imported successfully")

        from src.actions.audit_logger import audit_logger
        print("[PASS] Audit logger imported successfully")

        from src.actions.retry_handler import with_retry
        print("[PASS] Retry handler imported successfully")

        from src.actions.rate_limiter import initialize_rate_limiters
        print("[PASS] Rate limiter imported successfully")

        from src.watchers.base_watcher import BaseWatcher
        print("[PASS] Base watcher imported successfully")

        return True
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_config():
    """Test configuration loading."""
    try:
        from src.config import config

        # Check that paths exist
        assert config.vault_path.exists(), "Vault path should exist"
        assert config.needs_action_path.exists(), "Needs action path should exist"
        print("[PASS] Configuration validated successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Configuration test failed: {e}")
        return False

def test_audit_logger():
    """Test audit logger functionality."""
    try:
        from src.actions.audit_logger import audit_logger

        # Test logging an action
        audit_logger.log_action(
            action_type="test_action",
            actor="test_script",
            target="test_target",
            parameters={"test": True},
            approval_status="test_approved",
            result="success"
        )

        # Test retrieving recent actions
        recent = audit_logger.get_recent_actions(limit=5)
        assert len(recent) > 0, "Should have at least one log entry"
        print("[PASS] Audit logger working correctly")
        return True
    except Exception as e:
        print(f"[FAIL] Audit logger test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Testing Personal AI Employee system structure...\n")

    tests = [
        test_imports,
        test_config,
        test_audit_logger
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()  # Empty line between tests

    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("[SUCCESS] All tests passed! System structure is ready.")
        return 0
    else:
        print("[FAILURE] Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())