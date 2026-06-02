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
        warnings = [
            "⚠ tirith security scanner enabled but not available",
            "Browser engine (Chromium, for web browsing tools) is not installed",
        ]
        for w in warnings:
            # Remove the warning line (and any continuation) wherever it appears
            while w in reply:
                idx = reply.find(w)
                # Find start of the line containing the warning
                line_start = reply.rfind("\n", 0, idx)
                line_start = line_start + 1 if line_start != -1 else 0
                # Find end of the warning block (end of line, possibly with extra text)
                line_end = reply.find("\n", idx)
                if line_end == -1:
                    line_end = len(reply)
                reply = reply[:line_start] + reply[line_end:]
            # Clean up blank lines that may result
            reply = "\n".join(line for line in reply.split("\n") if line.strip())
        return {"reply": reply}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Agent timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
