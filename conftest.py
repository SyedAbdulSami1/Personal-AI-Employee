"""
Pytest Fixtures — Shared fixtures for all tests.
"""
import pytest
from pathlib import Path
from src.config import Config


@pytest.fixture
def config():
    """
    Create and return a Config instance for tests.
    This fixture is automatically used by tests that need 'config' parameter.
    """
    cfg = Config()
    # Ensure vault structure exists
    cfg.vault_path.mkdir(parents=True, exist_ok=True)
    cfg.needs_action_path.mkdir(parents=True, exist_ok=True)
    cfg.logs_path.mkdir(parents=True, exist_ok=True)
    return cfg
