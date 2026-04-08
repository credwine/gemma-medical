"""AI Assistant API endpoint -- general-purpose medical chat powered by Gemma 4."""

import traceback
from typing import Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.ollama_client import chat

router = APIRouter(prefix="/api", tags=["assistant"])

SYSTEM_PROMPT = (
    "You are Gemma Medical Assistant, an AI clinical decision support tool running "
    "locally on this device. You help community health workers with medical questions, "
    "symptom assessment, drug information, clinical guidelines, and medical terminology. "
    "You follow WHO guidelines. You always remind users that you provide guidance only "
    "and professional medical consultation should be sought for serious conditions. "
    "Respond in clear, simple language appropriate for community health workers."
)

LANGUAGE_NAMES = {
    "en": "English", "es": "Spanish", "zh": "Chinese (Simplified)",
    "vi": "Vietnamese", "ko": "Korean", "tl": "Tagalog",
    "ar": "Arabic", "fr": "French", "ru": "Russian", "hi": "Hindi",
    "sw": "Swahili", "ha": "Hausa", "yo": "Yoruba", "am": "Amharic",
    "bn": "Bengali",
}


class AssistantRequest(BaseModel):
    message: str
    history: list = []
    language: str = "en"


@router.post("/assistant")
async def assistant_chat(req: AssistantRequest):
    """General-purpose medical AI chat endpoint.

    Accepts a message and optional conversation history. Returns the AI response
    as plain text. All processing happens locally via Ollama -- no data leaves the device.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if len(req.message) > 50000:
        raise HTTPException(status_code=400, detail="Message exceeds 50,000 character limit")

    try:
        # Build system prompt with optional language instruction
        system = SYSTEM_PROMPT
        if req.language != "en" and req.language in LANGUAGE_NAMES:
            lang_name = LANGUAGE_NAMES[req.language]
            system += (
                f"\n\nIMPORTANT: Respond entirely in {lang_name}. "
                f"Use clear, simple {lang_name} appropriate for community health workers."
            )

        # Build message list from history + current message
        messages = []
        for msg in req.history:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content.strip():
                messages.append({"role": role, "content": content})

        # Append the current user message
        messages.append({"role": "user", "content": req.message})

        # Call Gemma 4 via Ollama
        result = await chat(messages=messages, system=system)
        response_text = result.get("message", {}).get("content", "")

        if not response_text.strip():
            response_text = "I was unable to generate a response. Please rephrase your question and try again."

        return JSONResponse(content={"response": response_text})

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
