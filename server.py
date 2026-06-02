import subprocess
import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Implant Diploma Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
def health():
    return {"status": "ok", "agent": "implant-diploma-coach"}

@app.get("/debug")
def debug():
    env = dict(os.environ)
    return {
        "openrouter_key": "set" if env.get("OPENROUTER_API_KEY") else "missing",
        "openrouter_len": len(env.get("OPENROUTER_API_KEY", "")),
        "deepseek_key": "set" if env.get("DEEPSEEK_API_KEY") else "missing",
    }

@app.post("/api/chat")
def chat(req: ChatRequest):
    try:
        # Build env with Railway variables
        env = dict(os.environ)
        env["HOME"] = "/root"
        env["HERMES_HOME"] = "/root/.hermes"
        
        result = subprocess.run(
            [
                "hermes",
                "--profile", "implant-diploma",
                "--skills", "implant-diploma-coach",
                "chat",
                "-q", req.message,
                "-Q",
            ],
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        
        if result.returncode != 0:
            err = result.stderr.strip() or result.stdout.strip() or "(no output)"
            return {"reply": f"Error (code {result.returncode}): {err[:500]}"}
        
        reply = result.stdout.strip()
        if not reply:
            reply = "I processed your message but received an empty response."
        
        # Strip Chromium/browser engine warnings from Railway
        warning = "Browser engine (Chromium, for web browsing tools) is not installed"
        if reply.startswith(warning):
            lines = reply.split("\n", 1)
            reply = lines[1].strip() if len(lines) > 1 else reply
        return {"reply": reply}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Agent timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
