# Professional standard implementation | Global GEMINI.md
"""
Ralph Wiggum Stop Hook — Persistent iteration counter.
Saves counter to vault/Logs/ralph_counter.txt to persist across Claude restarts.
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime, timezone

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [RalphWiggum] %(levelname)s — %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("AI_Employee_Vault/Logs/ralph_wiggum.log"),
    ],
)
logger = logging.getLogger(__name__)

VAULT_PATH = Path(os.getenv("VAULT_PATH", "./AI_Employee_Vault"))
COUNTER_FILE = VAULT_PATH / "Logs" / "ralph_counter.txt"

def get_persistent_counter() -> int:
    """Read counter from file, fallback to env, then 0."""
    if COUNTER_FILE.exists():
        try:
            return int(COUNTER_FILE.read_text().strip())
        except (ValueError, TypeError):
            pass
    
    try:
        return int(os.getenv("RALPH_COUNTER", "0"))
    except ValueError:
        return 0

def set_persistent_counter(counter: int) -> None:
    """Save counter to file."""
    try:
        COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
        COUNTER_FILE.write_text(str(counter))
        logger.debug(f"Persistent Ralph counter set to: {counter}")
    except Exception as e:
        logger.error(f"Failed to save counter file: {e}")

def check_task_completion() -> bool:
    """Check if task file exists in /Done/."""
    done_path = VAULT_PATH / "Done"
    if not done_path.exists():
        return False

    # Check for specific task file if TASK_FILE env exists
    task_file = os.getenv("TASK_FILE")
    if task_file:
        task_name = Path(task_file).name
        if (done_path / task_name).exists():
            return True

    # Fallback: Is there ANY .md file in Done?
    # Note: In production, we'd want a more precise check
    return any(done_path.glob("*.md"))

def write_alert(counter: int) -> None:
    """Escalate to human via ALERT file in Needs_Action."""
    needs_action_path = VAULT_PATH / "Needs_Action"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    alert_file = needs_action_path / f"ALERT_ralph_max_{timestamp}.md"

    content = f"""---
type: alert
from: RalphWiggum
subject: Max iterations reached ({counter})
received: {datetime.now(timezone.utc).isoformat()}
priority: high
status: pending
---
## Ralph Wiggum Alert: Max Iterations Reached

The autonomous agent failed to complete the task after {counter} attempts.

**Task File**: {os.getenv("TASK_FILE", "Not specified")}
**Timestamp**: {datetime.now(timezone.utc).isoformat()}

Please review the logs in `AI_Employee_Vault/Logs/ralph_wiggum.log` and the current state of the vault.
"""
    alert_file.write_text(content, encoding='utf-8')
    logger.error(f"Max iterations reached. ALERT: {alert_file}")

def main():
    max_iterations = int(os.getenv("RALPH_MAX_ITERATIONS", "10"))
    current_counter = get_persistent_counter()

    if check_task_completion():
        logger.info("✓ Task complete — allowing exit")
        set_persistent_counter(0) # Reset
        sys.exit(0)

    if current_counter >= max_iterations:
        write_alert(current_counter)
        set_persistent_counter(0) # Reset
        sys.exit(0) # Exit and let human handle it

    # Not complete, increment and block exit
    new_counter = current_counter + 1
    set_persistent_counter(new_counter)
    
    logger.warning(f"✗ Task not complete — blocking exit ({new_counter}/{max_iterations})")
    print(f"RALPH_WIGGUM: Attempt {new_counter}/{max_iterations}. Re-injecting prompt.")
    
    # Signalling orchestrator/Claude to continue
    sys.exit(1)

if __name__ == "__main__":
    main()
