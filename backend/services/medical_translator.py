"""Medical Translator service -- cross-language symptom translation for health workers.

Converts colloquial symptom descriptions from local languages into standardized clinical English.
Powered by Gemma 4 running locally via Ollama.
"""

import json
from pathlib import Path
from backend.ollama_client import chat

SYSTEM_PROMPT = (Path(__file__).parent.parent / "prompts" / "medtranslate_system.txt").read_text()

LANGUAGE_NAMES = {
    "en": "English", "es": "Spanish", "zh": "Chinese (Simplified)",
    "vi": "Vietnamese", "ko": "Korean", "tl": "Tagalog",
    "ar": "Arabic", "fr": "French", "ru": "Russian", "hi": "Hindi",
}

DEFAULT_RESPONSE = {
    "clinical_translation": "Unable to complete translation. Please try again or consult an interpreter.",
    "medical_terms": [],
    "suggested_questions": ["Can you describe the symptoms again in simpler terms?", "When did the symptoms start?", "Is there pain? Where?"],
    "possible_conditions_mentioned": [],
    "notes": "The AI translation could not be completed. Consider using a human interpreter for accurate medical communication.",
}


async def translate_medical(
    patient_description: str,
    source_language: str = "auto",
    target_language: str = "en",
    language: str = "en",
) -> dict:
    """Translate patient symptom descriptions into clinical terminology."""
    lang_instruction = ""
    if language != "en" and language in LANGUAGE_NAMES:
        lang_name = LANGUAGE_NAMES[language]
        lang_instruction = f"\n\nIMPORTANT: Respond entirely in {lang_name}. The clinical_translation should still be in clinical English, but all explanations, suggested questions, and notes must be in {lang_name}."

    user_prompt = f"Patient description (source language: {source_language}, translate to: {target_language}):\n\n\"{patient_description}\""
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
