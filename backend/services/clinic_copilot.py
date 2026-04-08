"""Clinic Copilot service -- differential diagnosis support for community health workers.

Supports text-only or multimodal (text + image) assessment using Gemma 4.
"""

import json
from pathlib import Path
from backend.ollama_client import chat

SYSTEM_PROMPT = (Path(__file__).parent.parent / "prompts" / "clinic_system.txt").read_text()

LANGUAGE_NAMES = {
    "en": "English", "es": "Spanish", "zh": "Chinese (Simplified)",
    "vi": "Vietnamese", "ko": "Korean", "tl": "Tagalog",
    "ar": "Arabic", "fr": "French", "ru": "Russian", "hi": "Hindi",
}

DEFAULT_RESPONSE = {
    "possible_conditions": [],
    "recommended_actions": ["Refer patient to nearest health facility for proper evaluation"],
    "red_flags": ["Unable to complete assessment -- seek professional medical evaluation"],
    "referral_urgency": "urgent",
    "notes": "The AI assessment could not be completed. Please refer the patient for in-person evaluation.",
}


async def assess_patient(
    symptoms: str,
    patient_age: str,
    patient_sex: str,
    image: str = "",
    language: str = "en",
) -> dict:
    """Assess patient symptoms and provide differential diagnosis guidance."""
    lang_instruction = ""
    if language != "en" and language in LANGUAGE_NAMES:
        lang_name = LANGUAGE_NAMES[language]
        lang_instruction = f"\n\nIMPORTANT: Respond entirely in {lang_name}. All conditions, actions, red flags, and notes must be in {lang_name}."

    user_prompt = f"Patient: {patient_age} year old {patient_sex}\n\nSymptoms and presentation:\n{symptoms}"
    user_prompt += lang_instruction

    if image:
        messages = [{"role": "user", "content": user_prompt, "images": [image]}]
    else:
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
