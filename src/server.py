# Professional standard implementation | Global GEMINI.md
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import yaml

# Import project config
try:
    from src.config import Config
except ImportError:
    # Fallback for direct execution testing
    class Config:
        def __init__(self):
            self.vault_path = Path("AI_Employee_Vault")
            self.dry_run = True

app = FastAPI(title="AI Employee Dashboard API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

config = Config()
VAULT_PATH = config.vault_path

def get_folder_contents(folder_name: str) -> List[Dict[str, Any]]:
    """Reads metadata from .md files in a specific vault folder."""
    folder = VAULT_PATH / folder_name
    if not folder.exists():
        return []
    
    tasks = []
    for file_path in folder.glob("*.md"):
        try:
            content = file_path.read_text(encoding="utf-8")
            # Simple YAML frontmatter parser
            if content.startswith("---"):
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    metadata = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                    
                    tasks.append({
                        "id": file_path.name,
                        "filename": file_path.name,
                        "metadata": metadata,
                        "preview": body[:200] + "..." if len(body) > 200 else body,
                        "mtime": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
        except Exception as e:
            logging.error(f"Error reading {file_path}: {e}")
            
    # Sort by most recent
    return sorted(tasks, key=lambda x: x["mtime"], reverse=True)

@app.get("/api/status")
async def get_status():
    """Returns general system status."""
    return {
        "status": "online",
        "mode": "DRY_RUN" if config.dry_run else "PRODUCTION",
        "vault": str(VAULT_PATH),
        "last_update": datetime.now().isoformat()
    }

@app.get("/api/tasks/{folder}")
async def get_tasks(folder: str):
    """Fetch tasks from a specific folder (Needs_Action, Pending_Approval, Done)."""
    valid_folders = ["Needs_Action", "Pending_Approval", "Done", "Approved", "Rejected"]
    if folder not in valid_folders:
        raise HTTPException(status_code=400, detail="Invalid folder name")
    
    return get_folder_contents(folder)

@app.post("/api/tasks/move")
async def move_task(request: Request):
    """Moves a task file between folders (e.g., Pending_Approval -> Approved)."""
    data = await request.json()
    filename = data.get("filename")
    from_folder = data.get("from")
    to_folder = data.get("to")
    
    source = VAULT_PATH / from_folder / filename
    destination = VAULT_PATH / to_folder / filename
    
    if not source.exists():
        raise HTTPException(status_code=404, detail=f"Source file {filename} not found in {from_folder}")
    
    try:
        # Ensure destination folder exists
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.rename(destination)
        return {"status": "success", "message": f"Moved {filename} to {to_folder}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logs")
async def get_logs(limit: int = 50):
    """Returns the last N lines of the application log."""
    log_file = VAULT_PATH / "Logs" / "app.log"
    if not log_file.exists():
        return {"logs": ["Log file not found."]}
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            return {"logs": [line.strip() for line in lines[-limit:]]}
    except Exception as e:
        return {"logs": [f"Error reading logs: {e}"]}

@app.get("/", response_class=HTMLResponse)
async def read_dashboard():
    """Serves the dashboard.html file."""
    dashboard_path = Path("dashboard.html")
    if dashboard_path.exists():
        return dashboard_path.read_text(encoding="utf-8")
    return "<h1>Dashboard file not found</h1>"


@app.post("/api/chat")
async def chat(request: Request):
    """AI Chat with Skills system."""
    import os
    from groq import Groq
    import dotenv
    dotenv.load_dotenv(override=True)
    
    data = await request.json()
    user_message = data.get("message", "").lower()
    
    # SKILL: Email Summary - No LLM needed
    if any(word in user_message for word in ["email", "inbox", "summary", "summarize"]):
        tasks = get_folder_contents("Needs_Action")
        emails = [t for t in tasks if t.get("metadata", {}).get("type") == "email"]
        high = [e for e in emails if e.get("metadata", {}).get("priority") == "high"]
        medium = [e for e in emails if e.get("metadata", {}).get("priority") == "medium"]
        low = [e for e in emails if e.get("metadata", {}).get("priority") == "low"]
        
        response = f"""📧 **Email Summary** (No AI needed — direct skill)

**High Priority:** {len(high)}
{chr(10).join([f"• {e['metadata'].get('from','?')} — {e['metadata'].get('subject','?')}" for e in high[:3]])}

**Medium Priority:** {len(medium)}
{chr(10).join([f"• {e['metadata'].get('from','?')} — {e['metadata'].get('subject','?')}" for e in medium[:3]])}

**Low Priority:** {len(low)}
{chr(10).join([f"• {e['metadata'].get('from','?')} — {e['metadata'].get('subject','?')}" for e in low[:3]])}

**Total Emails:** {len(emails)}"""
        return {"response": response}
    
    # SKILL: Task Organizer - No LLM needed
    if any(word in user_message for word in ["task", "organize", "priority", "sort"]):
        tasks = get_folder_contents("Needs_Action")
        high = [t for t in tasks if t.get("metadata", {}).get("priority") == "high"]
        medium = [t for t in tasks if t.get("metadata", {}).get("priority") == "medium"]
        low = [t for t in tasks if t.get("metadata", {}).get("priority") == "low"]
        emails = [t for t in tasks if t.get("metadata", {}).get("type") == "email"]
        whatsapps = [t for t in tasks if t.get("metadata", {}).get("type") == "whatsapp"]
        files = [t for t in tasks if t.get("metadata", {}).get("type") == "file_drop"]
        
        response = f"""📋 **Task Summary** (Skill — no LLM)

**Total:** {len(tasks)}
🔴 High: {len(high)} | 🟡 Medium: {len(medium)} | ⚪ Low: {len(low)}

**By Type:**
📧 Email: {len(emails)}
💬 WhatsApp: {len(whatsapps)}
📁 Files: {len(files)}"""
        return {"response": response}
    
    # SKILL: Invoice - No LLM needed
    if any(word in user_message for word in ["invoice", "bill", "payment"]):
        response = """📄 **Invoice Generator** (Skill)

Invoice banane ke liye yeh likhو:
"Client [naam] ka [amount] ka invoice banao"

Example: "Client Ahmed ka 50000 ka invoice banao" """
        return {"response": response}

    # Fallback: LLM only for complex/unknown requests
    inbox_tasks = get_folder_contents("Needs_Action")
    prompt = f"""Tum ek Personal AI Employee ho. Urdu/English mix mein jawab do.
Current inbox: {len(inbox_tasks)} tasks.
User: {user_message}
Short aur helpful jawab do."""

    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        return {"response": response.choices[0].message.content}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
