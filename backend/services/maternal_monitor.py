"""Maternal Health Monitor service -- pregnancy risk assessment for midwives and CHWs.

Powered by Gemma 4 running locally via Ollama.
"""

import json
from pathlib import Path
from backend.ollama_client import chat

SYSTEM_PROMPT = (Path(__file__).parent.parent / "prompts" / "maternal_system.txt").read_text()

LANGUAGE_NAMES = {
    "en": "English", "es": "Spanish", "zh": "Chinese (Simplified)",
    "vi": "Vietnamese", "ko": "Korean", "tl": "Tagalog",
    "ar": "Arabic", "fr": "French", "ru": "Russian", "hi": "Hindi",
}

DEFAULT_RESPONSE = {
    "risk_level": "high",
    "risk_factors": [{"factor": "Assessment incomplete", "severity": "high", "explanation": "Unable to complete AI risk assessment"}],
    "immediate_actions": ["Refer to nearest health facility with obstetric capacity for evaluation"],
    "monitoring_plan": ["Seek professional evaluation as soon as possible"],
    "danger_signs_to_watch": ["Convulsions", "Heavy bleeding", "Severe headache", "Fever", "Difficulty breathing"],
    "referral_needed": True,
    "notes": "The AI assessment could not be completed. Err on the side of caution and refer for in-person evaluation.",
}


async def assess_maternal(
    gestational_weeks: int,
    symptoms: str,
    vitals: str = "",
    history: str = "",
    language: str = "en",
) -> dict:
    """Assess maternal health risks based on symptoms and gestational age."""
    lang_instruction = ""
    if language != "en" and language in LANGUAGE_NAMES:
        lang_name = LANGUAGE_NAMES[language]
        lang_instruction = f"\n\nIMPORTANT: Respond entirely in {lang_name}. All risk factors, actions, danger signs, and notes must be in {lang_name}."

    user_prompt = f"Gestational age: {gestational_weeks} weeks\n\nSymptoms and concerns:\n{symptoms}"
    if vitals:
        user_prompt += f"\n\nVitals:\n{vitals}"
    if history:
        user_prompt += f"\n\nObstetric/medical history:\n{history}"
    user_prompt += lang_instruction

    messages = [{"role": "user", "content": user_prompt}]

    result = await chat(messages=messages, system=SYSTEM_PROMPT)
    content_text = result.get("message", {}).get("content", "")
    return _extract_json(content_text)


def _extract_json(text: str) -> dict:
    """Extract JSON from model response text."""
    # Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block in markdown
    for marker in ["```json", "```"]:
        if marker in text:
            start = text.index(marker) + len(marker)
            end = text.index("```", start)
            try:
                return json.loads(text[start:end].strip())
            except (json.JSONDecodeError, ValueError):
                pass

    # Try to find JSON object in text
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end != -1:
        try:
            return json.loads(text[brace_start:brace_end + 1])
        except json.JSONDecodeError:
            pass

    # Return default structure if all parsing fails
    return DEFAULT_RESPONSE.copy()
