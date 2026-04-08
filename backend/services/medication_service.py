"""Medication Log service -- local JSON-backed medication tracking.

Stores medication data in data/medications.json. Auto-creates the data
directory and empty JSON array on first access. Designed for offline clinic use.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent.parent / "data"
MEDICATIONS_FILE = DATA_DIR / "medications.json"


def _ensure_file() -> None:
    """Create data directory and medications.json if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not MEDICATIONS_FILE.exists():
        MEDICATIONS_FILE.write_text("[]", encoding="utf-8")


def _read_all() -> list[dict]:
    """Read all medication records from disk."""
    _ensure_file()
    text = MEDICATIONS_FILE.read_text(encoding="utf-8")
    return json.loads(text) if text.strip() else []


def _write_all(medications: list[dict]) -> None:
    """Write all medication records to disk."""
    _ensure_file()
    MEDICATIONS_FILE.write_text(json.dumps(medications, indent=2, ensure_ascii=False), encoding="utf-8")


def get_medications_by_patient(patient_id: str) -> list[dict]:
    """Return all medications for a given patient, sorted newest first."""
    meds = _read_all()
    patient_meds = [m for m in meds if m.get("patient_id") == patient_id]
    patient_meds.sort(key=lambda m: m.get("start_date", ""), reverse=True)
    return patient_meds


def get_active_medications(patient_id: str) -> list[dict]:
    """Return only active (ongoing) medications for a patient.

    A medication is active when its end_date is empty or not set.
    """
    meds = get_medications_by_patient(patient_id)
    return [m for m in meds if not m.get("end_date")]


def create_medication(data: dict) -> dict:
    """Create a new medication record with auto-generated ID."""
    meds = _read_all()

    med = {
        "med_id": str(uuid.uuid4()),
        "patient_id": data.get("patient_id", ""),
        "medication_name": data.get("medication_name", ""),
        "dosage": data.get("dosage", ""),
        "frequency": data.get("frequency", ""),
        "start_date": data.get("start_date", datetime.now().strftime("%Y-%m-%d")),
        "end_date": data.get("end_date", ""),
        "prescribed_by": data.get("prescribed_by", ""),
        "notes": data.get("notes", ""),
    }

    meds.append(med)
    _write_all(meds)
    return med
