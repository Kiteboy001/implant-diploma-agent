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
            return {"reply": f"Error: {result.stderr[:500]}"}
        
        reply = result.stdout.strip()
        if not reply:
            reply = "I processed your message but received an empty response."
        return {"reply": reply}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Agent timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
