"""Visit Records API endpoints -- clinical visit logging and retrieval."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from backend.services.visit_service import (
    get_visits_by_patient,
    get_visit,
    create_visit,
    update_visit,
)

router = APIRouter(prefix="/api", tags=["visits"])


class Vitals(BaseModel):
    bp_systolic: Optional[float] = None
    bp_diastolic: Optional[float] = None
    temperature_c: Optional[float] = None
    pulse_rate: Optional[float] = None
    respiratory_rate: Optional[float] = None
    weight_kg: Optional[float] = None
    height_cm: Optional[float] = None


class VisitCreate(BaseModel):
    patient_id: str
    chief_complaint: str = ""
    symptoms: str = ""
    vitals: Vitals = Vitals()
    diagnosis: str = ""
    treatment_plan: str = ""
    medications_prescribed: list[str] = []
    follow_up_date: str = ""
    ai_assessment: dict = {}
    notes: str = ""
    attending_worker: str = ""


class VisitUpdate(BaseModel):
    chief_complaint: Optional[str] = None
    symptoms: Optional[str] = None
    vitals: Optional[Vitals] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    medications_prescribed: Optional[list[str]] = None
    follow_up_date: Optional[str] = None
    ai_assessment: Optional[dict] = None
    notes: Optional[str] = None
    attending_worker: Optional[str] = None


@router.get("/visits")
async def list_visits(patient_id: Optional[str] = Query(None)):
    """List visits, optionally filtered by patient_id."""
    if not patient_id:
        raise HTTPException(status_code=400, detail="patient_id query parameter is required")
    results = get_visits_by_patient(patient_id)
    return JSONResponse(content=results)


@router.get("/visits/{visit_id}")
async def read_visit(visit_id: str):
    """Get a single visit by ID."""
    visit = get_visit(visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return JSONResponse(content=visit)


@router.post("/visits", status_code=201)
async def record_visit(req: VisitCreate):
    """Record a new clinical visit."""
    if not req.patient_id.strip():
        raise HTTPException(status_code=400, detail="patient_id is required")

    data = req.model_dump()
    # Convert Vitals model to plain dict for storage
    data["vitals"] = req.vitals.model_dump()
    visit = create_visit(data)
    return JSONResponse(content=visit, status_code=201)


@router.put("/visits/{visit_id}")
async def modify_visit(visit_id: str, req: VisitUpdate):
    """Update an existing visit record."""
    update_data = {}
    for k, v in req.model_dump().items():
        if v is not None:
            update_data[k] = v

    # Convert Vitals model to dict if present
    if "vitals" in update_data and hasattr(req.vitals, "model_dump"):
        update_data["vitals"] = req.vitals.model_dump(exclude_none=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    visit = update_visit(visit_id, update_data)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    return JSONResponse(content=visit)
