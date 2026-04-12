"""Patient Queue API endpoints -- waiting room management."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from backend.services.queue_service import (
    get_queue,
    add_to_queue,
    update_queue_status,
    remove_from_queue,
    call_next,
)

router = APIRouter(prefix="/api", tags=["queue"])


class QueueAddRequest(BaseModel):
    patient_id: str
    patient_name: str = ""
    priority: int = 3
    reason: str = ""


class QueueStatusUpdate(BaseModel):
    status: str


@router.get("/queue")
async def list_queue():
    """Get the current patient queue, sorted by priority then arrival time."""
    queue = get_queue()
    return JSONResponse(content=queue)


@router.post("/queue", status_code=201)
async def enqueue_patient(req: QueueAddRequest):
    """Add a patient to the waiting room queue."""
    if not req.patient_id.strip():
        raise HTTPException(status_code=400, detail="patient_id is required")

    if req.priority < 1 or req.priority > 5:
        raise HTTPException(status_code=400, detail="priority must be between 1 and 5")

    entry = add_to_queue(req.model_dump())
    return JSONResponse(content=entry, status_code=201)


@router.put("/queue/{queue_id}/status")
async def modify_queue_status(queue_id: str, req: QueueStatusUpdate):
    """Update the status of a queue entry (waiting, in-progress, completed, referred)."""
    valid = ("waiting", "in-progress", "completed", "referred")
    if req.status not in valid:
        raise HTTPException(
            status_code=400,
            detail=f"status must be one of: {', '.join(valid)}",
        )

    entry = update_queue_status(queue_id, req.status)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return JSONResponse(content=entry)


@router.post("/queue/call-next")
async def call_next_patient():
    """Call the next patient in queue (highest priority, earliest arrival)."""
    entry = call_next()
    if not entry:
        return JSONResponse(content={"message": "No patients waiting in queue"}, status_code=200)
    return JSONResponse(content=entry)


@router.delete("/queue/{queue_id}")
async def dequeue_patient(queue_id: str):
    """Remove a patient from the queue."""
    deleted = remove_from_queue(queue_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return JSONResponse(content={"deleted": True})
