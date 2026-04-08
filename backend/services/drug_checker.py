"""Drug Interaction Checker service -- medication safety for community health settings.

Supports text-only or multimodal (text + image) analysis using Gemma 4.
"""

import json
from pathlib import Path
from backend.ollama_client import chat

SYSTEM_PROMPT = (Path(__file__).parent.parent / "prompts" / "drug_system.txt").read_text()

LANGUAGE_NAMES = {
    "en": "English", "es": "Spanish", "zh": "Chinese (Simplified)",
    "vi": "Vietnamese", "ko": "Korean", "tl": "Tagalog",
    "ar": "Arabic", "fr": "French", "ru": "Russian", "hi": "Hindi",
}

DEFAULT_RESPONSE = {
    "interactions": [],
    "warnings": ["Unable to complete drug interaction check -- consult a pharmacist or physician"],
    "safe_combinations": [],
    "notes": "The AI analysis could not be completed. Please consult a qualified pharmacist for medication safety review.",
}


async def check_interactions(
    medications: str,
    patient_conditions: str = "",
    image: str = "",
    language: str = "en",
) -> dict:
    """Check drug interactions for a list of medications."""
    lang_instruction = ""
    if language != "en" and language in LANGUAGE_NAMES:
        lang_name = LANGUAGE_NAMES[language]
        lang_instruction = f"\n\nIMPORTANT: Respond entirely in {lang_name}. All interaction descriptions, warnings, and notes must be in {lang_name}."

    user_prompt = f"Check for drug interactions between the following medications:\n\n{medications}"
    if patient_conditions:
        user_prompt += f"\n\nPatient conditions/diagnoses:\n{patient_conditions}"
    user_prompt += lang_instruction

    if image:
        user_prompt = "Identify the medications shown in this image and check for interactions between them."
        if medications.strip():
            user_prompt += f"\n\nThe health worker also listed these medications:\n{medications}"
        if patient_conditions:
            user_prompt += f"\n\nPatient conditions/diagnoses:\n{patient_conditions}"
        user_prompt += lang_instruction
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
