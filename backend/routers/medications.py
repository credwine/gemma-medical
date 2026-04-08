"""Medication Log API endpoints -- prescription tracking per patient."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from backend.services.medication_service import (
    get_medications_by_patient,
    get_active_medications,
    create_medication,
)

router = APIRouter(prefix="/api", tags=["medications"])


class MedicationCreate(BaseModel):
    patient_id: str
    medication_name: str
    dosage: str = ""
    frequency: str = ""
    start_date: str = ""
    end_date: str = ""
    prescribed_by: str = ""
    notes: str = ""


@router.get("/medications")
async def list_medications(patient_id: Optional[str] = Query(None)):
    """List all medications for a patient."""
    if not patient_id:
        raise HTTPException(status_code=400, detail="patient_id query parameter is required")
    results = get_medications_by_patient(patient_id)
    return JSONResponse(content=results)


@router.get("/medications/active")
async def list_active_medications(patient_id: Optional[str] = Query(None)):
    """List only active (ongoing) medications for a patient."""
    if not patient_id:
        raise HTTPException(status_code=400, detail="patient_id query parameter is required")
    results = get_active_medications(patient_id)
    return JSONResponse(content=results)


@router.post("/medications", status_code=201)
async def prescribe_medication(req: MedicationCreate):
    """Record a new medication prescription."""
    if not req.patient_id.strip():
        raise HTTPException(status_code=400, detail="patient_id is required")
    if not req.medication_name.strip():
        raise HTTPException(status_code=400, detail="medication_name is required")

    med = create_medication(req.model_dump())
    return JSONResponse(content=med, status_code=201)
