module.exports = {
  apps: [
    {
      name: "orchestrator",
      script: "python",
      args: "src/orchestrator.py",
      cwd: __dirname,
      env: {
        PYTHONPATH: "./src",
        DRY_RUN: "true",
        DEV_MODE: "true"
      },
      error_file: "AI_Employee_Vault/Logs/pm2/orchestrator.err.log",
      out_file: "AI_Employee_Vault/Logs/pm2/orchestrator.out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      restart_delay: 5000,
      max_restarts: 10,
      instances: 1,
      autorestart: true
    },
    {
      name: "gmail_watcher",
      script: "python",
      args: "src/watchers/gmail_watcher.py",
      cwd: __dirname,
      env: {
        PYTHONPATH: "./src",
        DRY_RUN: "true",
        DEV_MODE: "true"
      },
      error_file: "AI_Employee_Vault/Logs/pm2/gmail_watcher.err.log",
      out_file: "AI_Employee_Vault/Logs/pm2/gmail_watcher.out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      restart_delay: 5000,
      max_restarts: 10,
      instances: 1,
      autorestart: true
    },
    {
      name: "whatsapp_watcher",
      script: "python",
      args: "src/watchers/whatsapp_watcher.py",
      cwd: __dirname,
      env: {
        PYTHONPATH: "./src",
        DRY_RUN: "true",
        DEV_MODE: "true"
      },
      error_file: "AI_Employee_Vault/Logs/pm2/whatsapp_watcher.err.log",
      out_file: "AI_Employee_Vault/Logs/pm2/whatsapp_watcher.out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      restart_delay: 5000,
      max_restarts: 10,
      instances: 1,
      autorestart: true
    },
    {
      name: "filesystem_watcher",
      script: "python",
      args: "src/watchers/filesystem_watcher.py",
      cwd: __dirname,
      env: {
        PYTHONPATH: "./src",
        DRY_RUN: "true",
        DEV_MODE: "true"
      },
      error_file: "AI_Employee_Vault/Logs/pm2/filesystem_watcher.err.log",
      out_file: "AI_Employee_Vault/Logs/pm2/filesystem_watcher.out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      restart_delay: 5000,
      max_restarts: 10,
      instances: 1,
      autorestart: true
    },
    {
      name: "watchdog",
      script: "python",
      args: "src/watchdog.py",
      cwd: __dirname,
      env: {
        PYTHONPATH: "./src",
        DRY_RUN: "true",
        DEV_MODE: "true"
      },
      error_file: "AI_Employee_Vault/Logs/pm2/watchdog.err.log",
      out_file: "AI_Employee_Vault/Logs/pm2/watchdog.out.log",
      log_date_format: "YYYY-MM-DD HH:mm:ss",
      restart_delay: 5000,
      max_restarts: 10,
      instances: 1,
      autorestart: true
    }
  ]
};
