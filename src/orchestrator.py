"""
Main orchestrator for the Personal AI Employee system.
Watches for action files and coordinates processing with Claude Code.
"""
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

import logging

from src.config import config
from src.actions.audit_logger import audit_logger

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Main orchestrator that watches for action files and triggers Claude Code processing.
    Implements the Ralph Wiggum loop mechanism for autonomous task completion.
    """

    def __init__(self):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._running = False
        self._ralph_counter = 0
        self._processed_files = set()  # Track files we've already processed

    def start(self):
        """Start the orchestrator."""
        self.logger.info("Starting Personal AI Employee Orchestrator")
        self._running = True

        # Start the orchestrator loop in a separate thread
        orchestrator_thread = threading.Thread(target=self._run_loop, daemon=True)
        orchestrator_thread.start()

        logger.info("Orchestrator started successfully")

    def stop(self):
        """Stop the orchestrator."""
        self.logger.info("Stopping Personal AI Employee Orchestrator")
        self._running = False

    def _run_loop(self):
        """Main orchestrator loop."""
        while self._running:
            try:
                self._process_needs_action_folder()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                self.logger.error(f"Error in orchestrator loop: {e}", exc_info=True)
                time.sleep(10)  # Wait longer on error

    def _process_needs_action_folder(self):
        """Process files in the Needs_Action folder."""
        try:
            needs_action_path = self.config.needs_action_path

            # Get all markdown files in Needs_Action
            md_files = list(needs_action_path.glob("*.md"))

            for md_file in md_files:
                # Skip if we've already processed this file recently
                if md_file in self._processed_files:
                    continue

                # Check if file is ready to process (not being written to)
                if self._is_file_ready(md_file):
                    self.logger.info(f"Processing action file: {md_file.name}")
                    self._process_action_file(md_file)
                    self._processed_files.add(md_file)

                    # Limit the size of processed files set to prevent memory growth
                    if len(self._processed_files) > 1000:
                        # Keep only the most recent 500 entries
                        self._processed_files = set(list(self._processed_files)[-500:])

        except Exception as e:
            self.logger.error(f"Error processing Needs_Action folder: {e}", exc_info=True)

    def _is_file_ready(self, file_path: Path) -> bool:
        """
        Check if a file is ready to be processed (not currently being written to).

        Args:
            file_path: Path to the file to check

        Returns:
            bool: True if file is ready, False if still being written
        """
        try:
            # Try to open the file for reading - if it fails, it might be locked
            with open(file_path, 'r'):
                pass
            return True
        except (IOError, OSError):
            return False

    def _process_action_file(self, file_path: Path):
        """
        Process an action file by triggering Claude Code and implementing Ralph Wiggum loop.

        Args:
            file_path: Path to the action file to process
        """
        try:
            # Read the action file to understand what needs to be done
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            self.logger.info(f"Triggering Claude Code for file: {file_path.name}")

            # Log that we're starting processing
            audit_logger.log_action(
                action_type="orchestrator_process_start",
                actor="orchestrator",
                target=str(file_path.name),
                parameters={"file_path": str(file_path)},
                approval_status="auto_approved",
                result="started",
                dry_run=self.config.dry_run
            )

            # In a real implementation, this would trigger Claude Code
            # For now, we'll simulate the processing by moving the file
            # through the approval workflow

            # Move to In_Progress/claude to indicate Claude is working on it
            in_progress_path = self.config.in_progress_path / file_path.name
            file_path.rename(in_progress_path)

            self.logger.info(f"Moved {file_path.name} to In_Progress/claude")

            # Log the move
            audit_logger.log_action(
                action_type="file_move",
                actor="orchestrator",
                target=str(file_path.name),
                parameters={
                    "from": str(file_path),
                    "to": str(in_progress_path),
                    "stage": "in_progress"
                },
                approval_status="auto_approved",
                result="success",
                dry_run=self.config.dry_run
            )

            # Simulate Claude Code processing time
            # In reality, Claude would process the file and create approval requests
            # For this simulation, we'll just move it to Pending_Approval after a delay
            import time
            time.sleep(2)  # Simulate processing time

            # Move to Pending_Approval for human review
            pending_approval_path = self.config.pending_approval_path / file_path.name
            in_progress_path.rename(pending_approval_path)

            self.logger.info(f"Moved {file_path.name} to Pending_Approval for review")

            # Log the move to pending approval
            audit_logger.log_action(
                action_type="file_move",
                actor="orchestrator",
                target=str(file_path.name),
                parameters={
                    "from": str(in_progress_path),
                    "to": str(pending_approval_path),
                    "stage": "pending_approval"
                },
                approval_status="auto_approved",
                result="success",
                dry_run=self.config.dry_run
            )

            # Implement Ralph Wiggum loop - check if task is done
            self._check_ralph_wiggum_loop(file_path.name)

        except Exception as e:
            self.logger.error(f"Error processing action file {file_path.name}: {e}", exc_info=True)
            audit_logger.log_action(
                action_type="orchestrator_process_error",
                actor="orchestrator",
                target=str(file_path.name),
                parameters={"error": str(e), "file_path": str(file_path)},
                approval_status="system_error",
                result="failure",
                error=str(e),
                dry_run=self.config.dry_run
            )

    def _check_ralph_wiggum_loop(self, filename: str):
        """
        Implement the Ralph Wiggum stop-hook mechanism.
        Checks if a task file exists in Done/ to allow exit, otherwise increments counter.

        Args:
            filename: Name of the file being processed
        """
        done_file_path = self.config.done_path / filename

        if done_file_path.exists():
            # Task is done - reset counter and allow normal exit
            self._ralph_counter = 0
            self.logger.info(f"Task {filename} found in Done/ - Ralph Wiggum counter reset")
        else:
            # Task not done yet - increment counter
            self._ralph_counter += 1
            self.logger.info(f"Ralph Wiggum counter: {self._ralph_counter}/10")

            if self._ralph_counter >= self.config.ralph_max_iterations:
                # Max reached - create alert and exit
                alert_filename = f"ALERT_ralph_max_{filename}"
                alert_path = self.config.needs_action_path / alert_filename

                alert_content = f"""# Ralph Wiggum Maximum Iterations Reached

**Task:** {filename}
**Counter:** {self._ralph_counter}
**Timestamp:** {datetime.now().isoformat()}

The Ralph Wiggum stop-hook has prevented exit for 10 consecutive checks.
This indicates the task may be stuck or requires manual intervention.

Please review the task and either:
1. Move the completed task to Done/ to allow normal processing
2. Investigate why the task is not completing
3. Manually intervene if necessary
"""

                try:
                    with open(alert_path, 'w', encoding='utf-8') as f:
                        f.write(alert_content)
                    self.logger.warning(f"Ralph Wiggum alert created: {alert_filename}")
                except Exception as e:
                    self.logger.error(f"Failed to create Ralph Wiggum alert: {e}")

                # Reset counter after creating alert
                self._ralph_counter = 0
            else:
                # Not max yet - in a real implementation, we would re-inject the prompt
                # and exit with code 1 to trigger the stop hook
                self.logger.debug(f"Ralph Wiggum counter incremented to {self._ralph_counter}")

    def get_status(self) -> dict:
        """Get current orchestrator status."""
        return {
            "running": self._running,
            "ralph_counter": self._ralph_counter,
            "processed_files_count": len(self._processed_files),
            "needs_action_count": len(list(self.config.needs_action_path.glob("*.md"))),
            "pending_approval_count": len(list(self.config.pending_approval_path.glob("*.md"))),
            "in_progress_count": len(list(self.config.in_progress_path.glob("*.md"))),
            "done_count": len(list(self.config.done_path.glob("*.md")))
        }


# Global orchestrator instance
orchestrator = Orchestrator()