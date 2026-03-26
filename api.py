"""
api.py — LLM Firewall API
Screens every prompt through the firewall classifier before forwarding
allowed requests to the Groq LLM.
"""

import os

from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq

from llm_firewall import classify_prompt

# ── App & client — initialised once ──────────────────────────────────────────

app = FastAPI(title="LLM Firewall API")

api_key = os.getenv("GROQ_API_KEY")
client  = Groq(api_key=api_key)

# ── Request model ─────────────────────────────────────────────────────────────

class PromptRequest(BaseModel):
    text: str

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "LLM Firewall API running"}


@app.post("/check")
def check_prompt(request: PromptRequest):
    """
    Classify the prompt, then either block it or forward it to Groq.
    Never raises — all error states are returned as structured JSON.
    """
    # Step 1 & 2 — classify and extract verdict
    classification = classify_prompt(request.text)
    verdict        = classification.get("verdict")

    # Step 3a — blocked: return immediately, no LLM call
    if verdict == "blocked":
        return {
            "status": "blocked",
            "reason": classification,
        }

    # Step 3b — allowed: forward to Groq
    try:
        response     = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": request.text}],
        )
        llm_response = response.choices[0].message.content

    except Exception as exc:
        llm_response = f"Groq API error: {exc}"

    return {
        "status":         "allowed",
        "llm_response":   llm_response,
        "classification": classification,
    }
