"""Patient Registry service -- local JSON-backed patient records.

Stores patient data in data/patients.json. Auto-creates the data directory
and empty JSON array on first access. Designed for offline clinic use.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent.parent / "data"
PATIENTS_FILE = DATA_DIR / "patients.json"


def _ensure_file() -> None:
    """Create data directory and patients.json if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PATIENTS_FILE.exists():
        PATIENTS_FILE.write_text("[]", encoding="utf-8")


def _read_all() -> list[dict]:
    """Read all patient records from disk."""
    _ensure_file()
    text = PATIENTS_FILE.read_text(encoding="utf-8")
    return json.loads(text) if text.strip() else []


def _write_all(patients: list[dict]) -> None:
    """Write all patient records to disk."""
    _ensure_file()
    PATIENTS_FILE.write_text(json.dumps(patients, indent=2, ensure_ascii=False), encoding="utf-8")


def get_all_patients(search_query: Optional[str] = None) -> list[dict]:
    """Return all patients, optionally filtered by a case-insensitive search
    across first_name, last_name, and village_or_address."""
    patients = _read_all()
    if not search_query:
        return patients

    q = search_query.lower()
    return [
        p for p in patients
        if q in p.get("first_name", "").lower()
        or q in p.get("last_name", "").lower()
        or q in p.get("village_or_address", "").lower()
        or q in p.get("patient_id", "").lower()
    ]


def get_patient(patient_id: str) -> Optional[dict]:
    """Return a single patient by ID, or None if not found."""
    patients = _read_all()
    for p in patients:
        if p["patient_id"] == patient_id:
            return p
    return None


def create_patient(data: dict) -> dict:
    """Create a new patient record with auto-generated ID and registration date."""
    patients = _read_all()

    patient = {
        "patient_id": str(uuid.uuid4()),
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "date_of_birth": data.get("date_of_birth", ""),
        "sex": data.get("sex", ""),
        "blood_type": data.get("blood_type", ""),
        "allergies": data.get("allergies", []),
        "chronic_conditions": data.get("chronic_conditions", []),
        "emergency_contact_name": data.get("emergency_contact_name", ""),
        "emergency_contact_phone": data.get("emergency_contact_phone", ""),
        "village_or_address": data.get("village_or_address", ""),
        "registered_date": datetime.now().isoformat(),
        "last_visit": "",
        "notes": data.get("notes", ""),
    }

    patients.append(patient)
    _write_all(patients)
    return patient


def update_patient(patient_id: str, data: dict) -> Optional[dict]:
    """Update an existing patient record. Returns updated record or None if not found."""
    patients = _read_all()

    for i, p in enumerate(patients):
        if p["patient_id"] == patient_id:
            # Update only provided fields, preserve patient_id and registered_date
            immutable = {"patient_id", "registered_date"}
            for key, value in data.items():
                if key not in immutable:
                    patients[i][key] = value
            _write_all(patients)
            return patients[i]

    return None


def delete_patient(patient_id: str) -> bool:
    """Delete a patient by ID. Returns True if deleted, False if not found."""
    patients = _read_all()
    original_len = len(patients)
    patients = [p for p in patients if p["patient_id"] != patient_id]

    if len(patients) < original_len:
        _write_all(patients)
        return True
    return False
