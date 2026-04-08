"""Analytics service -- dashboard statistics from local JSON data.

Reads patients.json and visits.json to compute summary metrics.
No writes, no external dependencies. Designed for offline clinic use.
"""

from collections import Counter
from datetime import datetime, timedelta

from backend.services.patient_service import _read_all as read_patients
from backend.services.visit_service import _read_all as read_visits


def get_summary() -> dict:
    """Compute clinic summary statistics.

    Returns total patients, visit counts (today / this week / this month),
    top diagnoses, and the five most recent visits with patient names.
    """
    patients = read_patients()
    visits = read_visits()

    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Build patient name lookup
    patient_map = {p["patient_id"]: f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
                   for p in patients}

    # Count visits by period
    visits_today = 0
    visits_week = 0
    visits_month = 0
    diagnoses: list[str] = []

    for v in visits:
        visit_date_str = v.get("visit_date", "")
        if not visit_date_str:
            continue

        try:
            visit_dt = datetime.fromisoformat(visit_date_str)
        except (ValueError, TypeError):
            continue

        if visit_dt.strftime("%Y-%m-%d") == today_str:
            visits_today += 1
        if visit_dt >= week_ago:
            visits_week += 1
        if visit_dt >= month_ago:
            visits_month += 1

        diagnosis = v.get("diagnosis", "").strip()
        if diagnosis:
            diagnoses.append(diagnosis)

    # Top diagnoses
    diagnosis_counts = Counter(diagnoses).most_common(10)
    common_diagnoses = [{"diagnosis": d, "count": c} for d, c in diagnosis_counts]

    # Recent visits (last 5) sorted newest first
    sorted_visits = sorted(visits, key=lambda v: v.get("visit_date", ""), reverse=True)
    recent_visits = []
    for v in sorted_visits[:5]:
        recent_visits.append({
            "visit_id": v.get("visit_id", ""),
            "patient_id": v.get("patient_id", ""),
            "patient_name": patient_map.get(v.get("patient_id", ""), "Unknown"),
            "visit_date": v.get("visit_date", ""),
            "chief_complaint": v.get("chief_complaint", ""),
            "diagnosis": v.get("diagnosis", ""),
        })

    return {
        "total_patients": len(patients),
        "total_visits_today": visits_today,
        "total_visits_week": visits_week,
        "total_visits_month": visits_month,
        "common_diagnoses": common_diagnoses,
        "recent_visits": recent_visits,
    }
