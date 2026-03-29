#!/usr/bin/env python3
"""
Ralph Wiggum stop-hook for preventing premature exit until tasks are complete.
"""
import os
import sys
from pathlib import Path

def main():
    """Implement Ralph Wiggum stop-hook logic."""
    # Get the Ralph Wiggum counter from environment (default to 0)
    ralph_counter = int(os.environ.get("RALPH_COUNTER", "0"))

    # Get the vault path - in a real implementation, this would come from config
    # For now, we'll look for the Done folder in common locations
    possible_vault_paths = [
        Path("./AI_Employee_Vault/Done"),
        Path("../AI_Employee_Vault/Done"),
        Path("../../AI_Employee_Vault/Done"),
        Path(os.environ.get("VAULT_PATH", "./AI_Employee_Vault")) / "Done"
    ]

    done_folder = None
    for path in possible_vault_paths:
        if path.exists():
            done_folder = path
            break

    if done_folder is None:
        # If we can't find the Done folder, assume we're in a test environment
        # and allow exit to prevent infinite loops during development
        print("RALPH WIGGUM: Done folder not found - allowing exit (test mode)")
        sys.exit(0)

    # In a real implementation, we would check for a specific task file
    # For this simulation, we'll check if there are ANY files in Done/
    try:
        done_files = list(done_folder.glob("*.md"))
        has_done_files = len(done_files) > 0
    except Exception as e:
        print(f"RALPH WIGGUM: Error checking Done folder: {e}")
        # Allow exit on error to prevent infinite loops
        sys.exit(0)

    # Ralph Wiggum logic:
    # Exit allowed : task file exists in Done/
    # Exit blocked : counter < 10 → increment, re-inject prompt, sys.exit(1)
    # Max reached  : counter == 10 → write ALERT_ralph_max_<task>.md → sys.exit(0)

    if has_done_files:
        # Exit allowed - reset counter and exit normally
        print(f"RALPH WIGGUM: Found {len(done_files)} files in Done/ - allowing exit")
        os.environ["RALPH_COUNTER"] = "0"  # Reset counter
        sys.exit(0)
    else:
        # Exit blocked - check if we've reached max iterations
        if ralph_counter >= 10:
            # Max reached - write alert and exit normally
            print(f"RALPH WIGGUM: Maximum iterations ({ralph_counter}) reached - creating alert and exiting")

            # Create alert file in Needs_Action
            needs_action_paths = [
                Path("./AI_Employee_Vault/Needs_Action"),
                Path("../AI_Employee_Vault/Needs_Action"),
                Path("../../AI_Employee_Vault/Needs_Action"),
                Path(os.environ.get("VAULT_PATH", "./AI_Employee_Vault")) / "Needs_Action"
            ]

            needs_action_folder = None
            for path in needs_action_paths:
                if path.exists():
                    needs_action_folder = path
                    break

            if needs_action_folder:
                alert_content = f"""# Ralph Wiggum Maximum Iterations Reached

**Timestamp:** {os.environ.get('TIMESTAMP', 'unknown')}
**Counter:** {ralph_counter}
**Message:** The Ralph Wiggum stop-hook has prevented exit for 10 consecutive checks.

This indicates that the autonomous AI employee may be stuck on a task
or requires manual intervention to complete the current workflow.

Please check:
1. The Needs_Action folder for unprocessed items
2. The Pending_Approval folder for items awaiting review
3. The In_Progress/claude folder for items being processed
4. System logs for error messages
5. Whether external services (Gmail, WhatsApp) are accessible

After resolving the issue, manually move a completed task to the Done/
folder to allow normal processing to resume.
"""

                alert_file = needs_action_folder / f"ALERT_ralph_max_{ralph_counter}_{int(os.environ.get('TIMESTAMP', '0'))}.md"
                try:
                    with open(alert_file, 'w') as f:
                        f.write(alert_content)
                    print(f"RALPH WIGGUM: Alert created at {alert_file}")
                except Exception as e:
                    print(f"RALPH WIGGUM: Failed to create alert: {e}")

            # Reset counter and exit
            os.environ["RALPH_COUNTER"] = "0"
            sys.exit(0)
        else:
            # Counter < 10 - increment and block exit
            new_counter = ralph_counter + 1
            print(f"RALPH WIGGUM: Counter {ralph_counter} -> {new_counter} - blocking exit")
            os.environ["RALPH_COUNTER"] = str(new_counter)

            # In a real implementation, we would re-inject the original prompt here
            # For this simulation, we just exit with code 1 to trigger the hook again
            sys.exit(1)

if __name__ == "__main__":
    main()