"""Referral Letter service -- local JSON-backed referral records.

Stores referral data in data/referrals.json. Uses Gemma 4 to generate
structured clinical referral letters for patient transfers between facilities.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from backend.ollama_client import generate
from backend.services.patient_service import get_patient
from backend.services.visit_service import get_visit

DATA_DIR = Path(__file__).parent.parent.parent / "data"
REFERRALS_FILE = DATA_DIR / "referrals.json"
PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "referral_system.txt"


def _ensure_file() -> None:
    """Create data directory and referrals.json if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not REFERRALS_FILE.exists():
        REFERRALS_FILE.write_text("[]", encoding="utf-8")


def _read_all() -> list[dict]:
    """Read all referral records from disk."""
    _ensure_file()
    text = REFERRALS_FILE.read_text(encoding="utf-8")
    return json.loads(text) if text.strip() else []


def _write_all(referrals: list[dict]) -> None:
    """Write all referral records to disk."""
    _ensure_file()
    REFERRALS_FILE.write_text(json.dumps(referrals, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_system_prompt() -> str:
    """Load the referral system prompt from file."""
    if PROMPT_FILE.exists():
        return PROMPT_FILE.read_text(encoding="utf-8")
    return "You are a clinical referral letter generator."


def get_referrals_by_patient(patient_id: str) -> list[dict]:
    """Return all referrals for a given patient, sorted newest first."""
    referrals = _read_all()
    patient_referrals = [r for r in referrals if r.get("patient_id") == patient_id]
    patient_referrals.sort(key=lambda r: r.get("created_at", ""), reverse=True)
    return patient_referrals


def get_referral(referral_id: str) -> Optional[dict]:
    """Return a single referral by ID, or None if not found."""
    referrals = _read_all()
    for r in referrals:
        if r["referral_id"] == referral_id:
            return r
    return None


async def generate_referral(data: dict) -> dict:
    """Generate a referral letter using Gemma 4 and store the record."""
    patient_id = data.get("patient_id", "")
    visit_id = data.get("visit_id", "")
    referral_reason = data.get("referral_reason", "")
    urgency = data.get("urgency", "routine")
    referring_facility = data.get("referring_facility", "")
    receiving_facility = data.get("receiving_facility", "")

    # Fetch patient and visit data
    patient = get_patient(patient_id)
    visit = get_visit(visit_id) if visit_id else None

    # Build context for AI
    patient_info = ""
    if patient:
        age = ""
        if patient.get("date_of_birth"):
            try:
                dob = datetime.fromisoformat(patient["date_of_birth"])
                age = str((datetime.now() - dob).days // 365)
            except (ValueError, TypeError):
                age = "Unknown"

        patient_info = f"""
Patient Name: {patient.get('first_name', '')} {patient.get('last_name', '')}
Date of Birth: {patient.get('date_of_birth', 'Unknown')}
Age: {age}
Sex: {patient.get('sex', 'Unknown')}
Blood Type: {patient.get('blood_type', 'Unknown')}
Address: {patient.get('village_or_address', 'Unknown')}
Allergies: {', '.join(patient.get('allergies', [])) or 'None known'}
Chronic Conditions: {', '.join(patient.get('chronic_conditions', [])) or 'None known'}
Emergency Contact: {patient.get('emergency_contact_name', 'N/A')} {patient.get('emergency_contact_phone', '')}
"""

    visit_info = ""
    if visit:
        vitals = visit.get("vitals", {})
        vitals_str = []
        if vitals.get("bp_systolic") and vitals.get("bp_diastolic"):
            vitals_str.append(f"BP: {vitals['bp_systolic']}/{vitals['bp_diastolic']} mmHg")
        if vitals.get("temperature_c"):
            vitals_str.append(f"Temperature: {vitals['temperature_c']} C")
        if vitals.get("pulse_rate"):
            vitals_str.append(f"Pulse: {vitals['pulse_rate']} bpm")
        if vitals.get("respiratory_rate"):
            vitals_str.append(f"Respiratory Rate: {vitals['respiratory_rate']} breaths/min")
        if vitals.get("weight_kg"):
            vitals_str.append(f"Weight: {vitals['weight_kg']} kg")

        visit_info = f"""
Visit Date: {visit.get('visit_date', 'Unknown')}
Chief Complaint: {visit.get('chief_complaint', 'Not documented')}
Symptoms: {visit.get('symptoms', 'Not documented')}
Vitals: {', '.join(vitals_str) if vitals_str else 'Not recorded'}
Diagnosis: {visit.get('diagnosis', 'Pending')}
Treatment Plan: {visit.get('treatment_plan', 'Not documented')}
Medications Prescribed: {', '.join(visit.get('medications_prescribed', [])) or 'None'}
Notes: {visit.get('notes', '')}
"""

    prompt = f"""Generate a formal clinical referral letter with the following information:

Referring Facility: {referring_facility or 'Not specified'}
Receiving Facility: {receiving_facility or 'Not specified'}
Referral Reason: {referral_reason}
Urgency Level: {urgency.upper()}
Date: {datetime.now().strftime('%B %d, %Y')}

PATIENT INFORMATION:
{patient_info or 'No patient data available'}

CLINICAL VISIT DATA:
{visit_info or 'No visit data available'}

Please generate the complete referral letter now."""

    system_prompt = _load_system_prompt()
    letter_text = await generate(prompt=prompt, system=system_prompt)

    # Store referral record
    referral = {
        "referral_id": str(uuid.uuid4()),
        "patient_id": patient_id,
        "visit_id": visit_id,
        "referral_reason": referral_reason,
        "urgency": urgency,
        "referring_facility": referring_facility,
        "receiving_facility": receiving_facility,
        "letter": letter_text,
        "created_at": datetime.now().isoformat(),
    }

    referrals = _read_all()
    referrals.append(referral)
    _write_all(referrals)

    return referral
