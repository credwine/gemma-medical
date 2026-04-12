"""Patient Queue service -- local JSON-backed waiting room queue.

Stores queue data in data/queue.json. Auto-sorts by priority (1=emergency first)
then by arrival time. Designed for offline clinic use.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent.parent / "data"
QUEUE_FILE = DATA_DIR / "queue.json"


def _ensure_file() -> None:
    """Create data directory and queue.json if they do not exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not QUEUE_FILE.exists():
        QUEUE_FILE.write_text("[]", encoding="utf-8")


def _read_all() -> list[dict]:
    """Read all queue entries from disk."""
    _ensure_file()
    text = QUEUE_FILE.read_text(encoding="utf-8")
    return json.loads(text) if text.strip() else []


def _write_all(queue: list[dict]) -> None:
    """Write all queue entries to disk."""
    _ensure_file()
    QUEUE_FILE.write_text(json.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")


def _sort_queue(queue: list[dict]) -> list[dict]:
    """Sort queue by priority (ascending, 1=highest) then arrival time (ascending)."""
    return sorted(queue, key=lambda q: (q.get("priority", 5), q.get("arrival_time", "")))


def get_queue() -> list[dict]:
    """Return the current queue, sorted by priority then arrival time."""
    queue = _read_all()
    # Only return active entries (not completed)
    active = [q for q in queue if q.get("status") in ("waiting", "in-progress")]
    return _sort_queue(active)


def add_to_queue(data: dict) -> dict:
    """Add a patient to the queue."""
    queue = _read_all()

    entry = {
        "queue_id": str(uuid.uuid4()),
        "patient_id": data.get("patient_id", ""),
        "patient_name": data.get("patient_name", ""),
        "priority": max(1, min(5, int(data.get("priority", 3)))),
        "reason": data.get("reason", ""),
        "status": "waiting",
        "arrival_time": datetime.now().isoformat(),
        "called_time": "",
        "completed_time": "",
    }

    queue.append(entry)
    _write_all(queue)
    return entry


def update_queue_status(queue_id: str, status: str) -> Optional[dict]:
    """Update the status of a queue entry."""
    valid_statuses = ("waiting", "in-progress", "completed", "referred")
    if status not in valid_statuses:
        return None

    queue = _read_all()
    for i, q in enumerate(queue):
        if q["queue_id"] == queue_id:
            queue[i]["status"] = status
            if status == "in-progress":
                queue[i]["called_time"] = datetime.now().isoformat()
            elif status in ("completed", "referred"):
                queue[i]["completed_time"] = datetime.now().isoformat()
            _write_all(queue)
            return queue[i]

    return None


def remove_from_queue(queue_id: str) -> bool:
    """Remove an entry from the queue. Returns True if removed."""
    queue = _read_all()
    original_len = len(queue)
    queue = [q for q in queue if q["queue_id"] != queue_id]

    if len(queue) < original_len:
        _write_all(queue)
        return True
    return False


def call_next() -> Optional[dict]:
    """Move the top waiting patient to in-progress status. Returns the entry or None."""
    queue = _read_all()
    waiting = [q for q in queue if q.get("status") == "waiting"]
    sorted_waiting = _sort_queue(waiting)

    if not sorted_waiting:
        return None

    next_entry = sorted_waiting[0]
    return update_queue_status(next_entry["queue_id"], "in-progress")
