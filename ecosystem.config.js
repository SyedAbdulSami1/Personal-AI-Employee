module.exports = {
  apps: [
    {
      name: "orchestrator",
      script: "uv",
      args: "run python main.py orchestrator",
      cwd: __dirname,
      env: {
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
      script: "uv",
      args: "run python main.py gmail",
      cwd: __dirname,
      env: {
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
      script: "uv",
      args: "run python main.py whatsapp",
      cwd: __dirname,
      env: {
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
      script: "uv",
      args: "run python main.py filesystem",
      cwd: __dirname,
      env: {
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
      script: "uv",
      args: "run python main.py watchdog",
      cwd: __dirname,
      env: {
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
