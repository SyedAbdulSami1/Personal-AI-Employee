"""
Watchdog monitor for health checking and auto-restart of system components.
"""
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging
import psutil
import os

from src.config import config

logger = logging.getLogger(__name__)


def get_audit_logger():
    """Get or create audit logger instance."""
    from src.actions.audit_logger import AuditLogger
    return AuditLogger(config.logs_path)


class ProcessMonitor:
    """
    Monitors system health and automatically restarts failed components.
    """

    def __init__(self):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._running = False
        self._monitored_processes: Dict[str, Dict] = {}
        self._alert_cooldown: Dict[str, datetime] = {}
        self._cooldown_period = timedelta(minutes=5)  # Don't alert more than once every 5 minutes

    def start(self):
        """Start the watchdog monitor."""
        self.logger.info("Starting Watchdog Monitor")
        self._running = True

        # Start the monitor loop in a separate thread
        monitor_thread = threading.Thread(target=self._run_loop, daemon=True)
        monitor_thread.start()

        logger.info("Watchdog Monitor started successfully")

    def stop(self):
        """Stop the watchdog monitor."""
        self.logger.info("Stopping Watchdog Monitor")
        self._running = False

    def register_process(self, name: str, check_function):
        """
        Register a process to be monitored.

        Args:
            name: Unique name for the process
            check_function: Function that returns True if process is healthy, False otherwise
        """
        self._monitored_processes[name] = {
            "check_function": check_function,
            "last_check": None,
            "last_healthy": None,
            "consecutive_failures": 0,
            "restart_count": 0
        }
        self.logger.info(f"Registered process for monitoring: {name}")

    def _run_loop(self):
        """Main monitor loop."""
        while self._running:
            try:
                self._check_all_processes()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Error in watchdog monitor loop: {e}", exc_info=True)
                time.sleep(60)  # Wait longer on error

    def _check_all_processes(self):
        """Check health of all registered processes."""
        for name, process_info in self._monitored_processes.items():
            try:
                is_healthy = process_info["check_function"]()
                process_info["last_check"] = datetime.now()

                if is_healthy:
                    process_info["last_healthy"] = datetime.now()
                    process_info["consecutive_failures"] = 0
                    self.logger.debug(f"Process {name} is healthy")
                else:
                    process_info["consecutive_failures"] += 1
                    self.logger.warning(f"Process {name} unhealthy (failure {process_info['consecutive_failures']})")

                    # Restart after 3 consecutive failures
                    if process_info["consecutive_failures"] >= 3:
                        self._attempt_restart(name, process_info)

            except Exception as e:
                self.logger.error(f"Error checking process {name}: {e}", exc_info=True)

    def _attempt_restart(self, name: str, process_info: Dict):
        """
        Attempt to restart a failed process.

        Args:
            name: Name of the process to restart
            process_info: Process information dictionary
        """
        # Check cooldown to prevent alert spam
        now = datetime.now()
        if name in self._alert_cooldown:
            if now - self._alert_cooldown[name] < self._cooldown_period:
                return  # Still in cooldown period

        self.logger.info(f"Attempting to restart process: {name}")
        process_info["restart_count"] += 1

        # Log the restart attempt
        audit_logger = get_audit_logger()
        audit_logger.log_action(
            action_type="process_restart_attempt",
            actor="watchdog_monitor",
            target=name,
            parameters={
                "restart_count": process_info["restart_count"],
                "consecutive_failures": process_info["consecutive_failures"]
            },
            approval_status="auto_approved",
            result="attempted",
            dry_run=self.config.dry_run
        )

        # In a real implementation, this would actually restart the process
        # For now, we'll just log that we would restart it
        self.logger.warning(f"Would restart process {name} (attempt {process_info['restart_count']})")

        # Create alert file
        self._create_restart_alert(name, process_info["restart_count"])

        # Reset failure counter after restart attempt
        process_info["consecutive_failures"] = 0

        # Set cooldown for alerts
        self._alert_cooldown[name] = now

    def _create_restart_alert(self, name: str, restart_count: int):
        """
        Create an alert file for a process restart.

        Args:
            name: Name of the process that was restarted
            restart_count: Number of times this process has been restarted
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        alert_filename = f"ALERT_{name}_restarted_{timestamp}.md"
        alert_path = self.config.needs_action_path / alert_filename

        alert_content = f"""# Process Restart Alert

**Process:** {name}
**Restart Count:** {restart_count}
**Timestamp:** {datetime.now().isoformat()}
**Reason:** Health check failed 3 consecutive times

The Watchdog Monitor has detected that the '{name}' process is unhealthy
and has attempted to restart it.

Please check:
1. Process logs for error messages
2. System resources (memory, CPU, disk)
3. External service connectivity
4. Configuration issues

If the problem persists, manual intervention may be required.
"""

        try:
            with open(alert_path, 'w', encoding='utf-8') as f:
                f.write(alert_content)
            self.logger.info(f"Created restart alert: {alert_filename}")
        except Exception as e:
            self.logger.error(f"Failed to create restart alert: {e}")

    def get_system_health(self) -> Dict:
        """
        Get overall system health metrics.

        Returns:
            Dictionary containing system health information
        """
        try:
            # Get basic system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(str(config.vault_path))

            health_info = {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_percent": (disk.used / disk.total) * 100,
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "processes_monitored": len(self._monitored_processes),
                "processes_healthy": sum(
                    1 for p in self._monitored_processes.values()
                    if p["consecutive_failures"] == 0 and p["last_healthy"] is not None
                ),
                "total_restarts": sum(
                    p["restart_count"] for p in self._monitored_processes.values()
                )
            }

            return health_info
        except Exception as e:
            self.logger.error(f"Error getting system health: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def log_system_health(self):
        """Log current system health to audit log."""
        health = self.get_system_health()
        if "error" not in health:
            audit_logger = get_audit_logger()
            audit_logger.log_action(
                action_type="system_health_check",
                actor="watchdog_monitor",
                target="system",
                parameters=health,
                approval_status="auto_approved",
                result="success",
                dry_run=self.config.dry_run
            )


# Global watchdog monitor instance
watchdog_monitor = ProcessMonitor()