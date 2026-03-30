# API Keys Setup Guide — FREE Options Only
> Quick reference for getting all required API keys and credentials

---

## 🎯 Quick Start (5 Minutes)

**For Hackathon Demo:** You only need **ONE** thing:
- ✅ **Qwen API** (use Ollama - 100% free, no signup)

**For Full Features:** Add these (all free):
- ✅ Gmail API (free with Google account)
- ✅ WhatsApp Web (no API needed)

---

## 1️⃣ Qwen API (REQUIRED)

### Option A: Ollama Local (RECOMMENDED - 100% FREE)
**Best for:** Hackathon, testing, privacy, no internet needed

```bash
# Step 1: Download Ollama
# Visit: https://ollama.ai/download
# Download and install for Windows

# Step 2: Install Qwen model (run in terminal)
ollama run qwen2.5:7b

# Step 3: Test it works
ollama run qwen2.5:7b "Hello, are you ready?"

# Step 4: Update .env file
QWEN_API_KEY=ollama
QWEN_BASE_URL=http://localhost:11434/v1
```

**Pros:**
- ✅ 100% free forever
- ✅ No API key needed
- ✅ Works offline
- ✅ No rate limits
- ✅ Private (runs locally)

**Cons:**
- ⚠️ Uses your computer's RAM (~4GB)
- ⚠️ Slightly slower than cloud API

---

### Option B: DashScope Cloud API (1M FREE tokens/month)
**Best for:** Production, faster responses, less RAM usage

```bash
# Step 1: Go to DashScope Console
# Visit: https://dashscope.console.aliyun.com/

# Step 2: Sign up / Login
# Use Alibaba Cloud account (free to create)

# Step 3: Create API Key
# - Click "API Key Management"
# - Click "Create New Key"
# - Copy the key (starts with "sk-")

# Step 4: Update .env file
QWEN_API_KEY=sk-your-key-here
QWEN_BASE_URL=https://dashscope.aliyuncs.com/api/v1
```

**Pros:**
- ✅ 1M free tokens/month (~1000 tasks)
- ✅ Fast responses
- ✅ No RAM usage on your computer

**Cons:**
- ⚠️ Requires internet
- ⚠️ Need to sign up

---

## 2️⃣ Gmail API (OPTIONAL)

### Get FREE Gmail Credentials

```bash
# Step 1: Go to Google Cloud Console
# Visit: https://console.cloud.google.com/

# Step 2: Create New Project
# - Click "Select Project" → "New Project"
# - Name: "AI Employee Test"
# - Click "Create"

# Step 3: Enable Gmail API
# - Go to "APIs & Services" → "Library"
# - Search: "Gmail API"
# - Click "Gmail API" → "Enable"

# Step 4: Create OAuth Credentials
# - Go to "APIs & Services" → "Credentials"
# - Click "Create Credentials" → "OAuth client ID"
# - Application type: "Desktop app"
# - Click "Create"
# - Download the JSON file

# Step 5: Save and Configure
# - Save JSON as: credentials.json
# - Put it in project root folder
# - Update .env:
GMAIL_CREDENTIALS=D:/D Data/Personal AI Employee Hackathon/credentials.json
```

**Important Notes:**
- ✅ Free with any Google account
- ✅ Use your own email for testing
- ⚠️ For production: Add test users in OAuth consent screen
- ⚠️ Keep `credentials.json` outside Git (already in .gitignore)

**Skip Gmail?** Yes! You can test with Filesystem Watcher only.

---

## 3️⃣ WhatsApp (OPTIONAL - No API Needed)

WhatsApp Web works automatically via Playwright.

```bash
# No API key needed!
# Just set session path in .env:
WHATSAPP_SESSION_PATH=D:/D Data/Personal AI Employee Hackathon/whatsapp_session

# First run:
# 1. Script opens browser
# 2. Scan QR code with your phone
# 3. Session saved automatically
# 4. Next runs: auto-login (no QR)
```

**Pros:**
- ✅ 100% free
- ✅ No API signup
- ✅ Works with your existing WhatsApp

**Cons:**
- ⚠️ Need to scan QR first time
- ⚠️ Requires browser automation

---

## 4️⃣ Filesystem Watcher (FREE - Built-in)

No setup needed! Just create the folder:

```bash
# Create Inbox folder
mkdir AI_Employee_Vault\Inbox

# Drop files here:
# - PDFs
# - Word docs (.docx)
# - CSV files
# - Text files (.txt)
# - Markdown (.md)

# Watcher auto-detects and creates action files
```

---

## 🚀 Recommended Setup for Hackathon

### Minimal (5 minutes):
```bash
# 1. Install Ollama
# Download from: https://ollama.ai/

# 2. Install Qwen model
ollama run qwen2.5:7b

# 3. Update .env
QWEN_API_KEY=ollama
QWEN_BASE_URL=http://localhost:11434/v1
DRY_RUN=true
DEV_MODE=true

# 4. Test
uv run python src/orchestrator.py
```

### Full Featured (20 minutes):
```bash
# 1. Ollama (above)
# 2. Gmail API (follow steps in Section 2)
# 3. WhatsApp session (auto-setup on first run)

# Update .env
QWEN_API_KEY=ollama
QWEN_BASE_URL=http://localhost:11434/v1
GMAIL_CREDENTIALS=D:/D Data/Personal AI Employee Hackathon/credentials.json
WHATSAPP_SESSION_PATH=D:/D Data/Personal AI Employee Hackathon/whatsapp_session
DRY_RUN=true
DEV_MODE=true
```

---

## ✅ Verification Checklist

After setup, test each component:

```bash
# Test Qwen connection
uv run python -c "from src.config import config; print('Qwen URL:', config.qwen_base_url)"

# Test Gmail credentials
uv run python -c "from src.watchers.gmail_watcher import GmailWatcher; w = GmailWatcher(); w.test_connection()"

# Test WhatsApp (opens browser)
uv run python src/watchers/whatsapp_watcher.py

# Test Filesystem watcher
echo "test" > AI_Employee_Vault/Inbox/test.txt
# Should create: AI_Employee_Vault/Needs_Action/FILE_*.md
```

---

## 🆘 Troubleshooting

### "Qwen API connection failed"
```bash
# Check Ollama is running
ollama list

# Restart Ollama service
# Windows: Restart from system tray
# Or run: ollama serve
```

### "Gmail credentials not found"
```bash
# Check path is absolute (not relative)
# Wrong: ./credentials.json
# Right: D:/D Data/Personal AI Employee Hackathon/credentials.json

# Check file exists
dir "D:\D Data\Personal AI Employee Hackathon\credentials.json"
```

### "WhatsApp QR code not showing"
```bash
# Delete session and re-scan
rmdir /s /q whatsapp_session

# Run watcher again
uv run python src/watchers/whatsapp_watcher.py
```

---

## 📚 Free Tier Limits

| Service | Free Limit | Reset Period |
|---------|-----------|--------------|
| Ollama (Local) | Unlimited | N/A |
| DashScope Qwen | 1M tokens | Monthly |
| Gmail API | 1B requests | Daily |
| WhatsApp Web | Unlimited | N/A |

**Note:** All limits are way above hackathon needs. You won't hit them.

---

## 🔐 Security Reminders

```bash
# ✅ DO: Keep .env private
# ✅ DO: Use test accounts during development
# ✅ DO: Keep DRY_RUN=true until tested
# ❌ DON'T: Commit .env to Git (already in .gitignore)
# ❌ DON'T: Share credentials.json
# ❌ DON'T: Use production credentials for testing
```

---

**Need Help?** Check README.md or ask in hackathon Discord.

**Last Updated:** 2026-01-07  
**All options verified FREE as of:** 2026-01-07
