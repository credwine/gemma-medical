"""Visit Records service -- local JSON-backed clinical visit logs.

Stores visit data in data/visits.json. Auto-creates the data directory
and empty JSON array on first access. Designed for offline clinic use.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent.parent / "data"
VISITS_FILE = DATA_DIR / "visits.json"


def _ensure_file() -> None:
    """Create data directory and visits.json if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not VISITS_FILE.exists():
        VISITS_FILE.write_text("[]", encoding="utf-8")


def _read_all() -> list[dict]:
    """Read all visit records from disk."""
    _ensure_file()
    text = VISITS_FILE.read_text(encoding="utf-8")
    return json.loads(text) if text.strip() else []


def _write_all(visits: list[dict]) -> None:
    """Write all visit records to disk."""
    _ensure_file()
    VISITS_FILE.write_text(json.dumps(visits, indent=2, ensure_ascii=False), encoding="utf-8")


def _default_vitals() -> dict:
    """Return an empty vitals template."""
    return {
        "bp_systolic": None,
        "bp_diastolic": None,
        "temperature_c": None,
        "pulse_rate": None,
        "respiratory_rate": None,
        "weight_kg": None,
        "height_cm": None,
    }


def get_visits_by_patient(patient_id: str) -> list[dict]:
    """Return all visits for a given patient, sorted newest first."""
    visits = _read_all()
    patient_visits = [v for v in visits if v.get("patient_id") == patient_id]
    patient_visits.sort(key=lambda v: v.get("visit_date", ""), reverse=True)
    return patient_visits


def get_visit(visit_id: str) -> Optional[dict]:
    """Return a single visit by ID, or None if not found."""
    visits = _read_all()
    for v in visits:
        if v["visit_id"] == visit_id:
            return v
    return None


def create_visit(data: dict) -> dict:
    """Create a new visit record with auto-generated ID and visit date."""
    visits = _read_all()

    # Merge provided vitals with defaults so all keys always exist
    provided_vitals = data.get("vitals", {})
    vitals = _default_vitals()
    vitals.update(provided_vitals)

    visit = {
        "visit_id": str(uuid.uuid4()),
        "patient_id": data.get("patient_id", ""),
        "visit_date": datetime.now().isoformat(),
        "chief_complaint": data.get("chief_complaint", ""),
        "symptoms": data.get("symptoms", ""),
        "vitals": vitals,
        "diagnosis": data.get("diagnosis", ""),
        "treatment_plan": data.get("treatment_plan", ""),
        "medications_prescribed": data.get("medications_prescribed", []),
        "follow_up_date": data.get("follow_up_date", ""),
        "ai_assessment": data.get("ai_assessment", {}),
        "notes": data.get("notes", ""),
        "attending_worker": data.get("attending_worker", ""),
    }

    visits.append(visit)
    _write_all(visits)

    # Update last_visit on the patient record
    _update_patient_last_visit(visit["patient_id"], visit["visit_date"])

    return visit


def update_visit(visit_id: str, data: dict) -> Optional[dict]:
    """Update an existing visit record. Returns updated record or None if not found."""
    visits = _read_all()

    for i, v in enumerate(visits):
        if v["visit_id"] == visit_id:
            immutable = {"visit_id", "patient_id", "visit_date"}
            for key, value in data.items():
                if key not in immutable:
                    # For vitals, merge rather than replace so partial updates work
                    if key == "vitals" and isinstance(value, dict):
                        visits[i]["vitals"].update(value)
                    else:
                        visits[i][key] = value
            _write_all(visits)
            return visits[i]

    return None


def _update_patient_last_visit(patient_id: str, visit_date: str) -> None:
    """Side-effect: stamp last_visit on the patient record when a visit is created."""
    from backend.services.patient_service import _read_all as read_patients, _write_all as write_patients

    patients = read_patients()
    for i, p in enumerate(patients):
        if p["patient_id"] == patient_id:
            patients[i]["last_visit"] = visit_date
            write_patients(patients)
            return
