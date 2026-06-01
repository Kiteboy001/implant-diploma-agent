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
            env={**os.environ, "HOME": "/root"},
        )
        reply = result.stdout.strip()
        if not reply and result.stderr:
            reply = "I'm having trouble processing that. Please try again."
        return {"reply": reply}
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Agent timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
