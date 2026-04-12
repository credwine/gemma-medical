"""Drug Formulary service -- WHO Essential Medicines reference.

Loads drug data from data/who_essential_medicines.json and provides
search and lookup functionality. Designed for offline clinic use.
"""

import json
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent.parent / "data"
FORMULARY_FILE = DATA_DIR / "who_essential_medicines.json"

# Cache loaded formulary in memory
_formulary_cache: Optional[list[dict]] = None


def _load_formulary() -> list[dict]:
    """Load formulary data from JSON file, with in-memory caching."""
    global _formulary_cache
    if _formulary_cache is not None:
        return _formulary_cache

    if not FORMULARY_FILE.exists():
        return []

    text = FORMULARY_FILE.read_text(encoding="utf-8")
    _formulary_cache = json.loads(text) if text.strip() else []
    return _formulary_cache


def get_all_drugs() -> list[dict]:
    """Return all drugs in the formulary."""
    return _load_formulary()


def search_drugs(query: str) -> list[dict]:
    """Search drugs by name, category, or indication (case-insensitive)."""
    drugs = _load_formulary()
    if not query:
        return drugs

    q = query.lower()
    results = []
    for drug in drugs:
        # Search across multiple fields
        if (
            q in drug.get("name", "").lower()
            or q in drug.get("id", "").lower()
            or q in drug.get("category", "").lower()
            or any(q in ind.lower() for ind in drug.get("indications", []))
        ):
            results.append(drug)

    return results


def get_drug(drug_id: str) -> Optional[dict]:
    """Return a single drug by ID, or None if not found."""
    drugs = _load_formulary()
    for drug in drugs:
        if drug.get("id") == drug_id:
            return drug
    return None
