"""Patient Registry API endpoints -- CRUD for patient records."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from backend.services.patient_service import (
    get_all_patients,
    get_patient,
    create_patient,
    update_patient,
    delete_patient,
)

router = APIRouter(prefix="/api", tags=["patients"])


class PatientCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: str = ""
    sex: str = ""
    blood_type: str = ""
    allergies: list[str] = []
    chronic_conditions: list[str] = []
    emergency_contact_name: str = ""
    emergency_contact_phone: str = ""
    village_or_address: str = ""
    notes: str = ""


class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    sex: Optional[str] = None
    blood_type: Optional[str] = None
    allergies: Optional[list[str]] = None
    chronic_conditions: Optional[list[str]] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    village_or_address: Optional[str] = None
    notes: Optional[str] = None


@router.get("/patients")
async def list_patients(search: Optional[str] = Query(None)):
    """List all patients, optionally filtered by search query."""
    results = get_all_patients(search_query=search)
    return JSONResponse(content=results)


@router.get("/patients/{patient_id}")
async def read_patient(patient_id: str):
    """Get a single patient by ID."""
    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return JSONResponse(content=patient)


@router.post("/patients", status_code=201)
async def register_patient(req: PatientCreate):
    """Register a new patient."""
    if not req.first_name.strip() or not req.last_name.strip():
        raise HTTPException(status_code=400, detail="First name and last name are required")
    patient = create_patient(req.model_dump())
    return JSONResponse(content=patient, status_code=201)


@router.put("/patients/{patient_id}")
async def modify_patient(patient_id: str, req: PatientUpdate):
    """Update an existing patient record."""
    # Only send non-None fields to the service
    update_data = {k: v for k, v in req.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    patient = update_patient(patient_id, update_data)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return JSONResponse(content=patient)


@router.delete("/patients/{patient_id}")
async def remove_patient(patient_id: str):
    """Delete a patient record."""
    deleted = delete_patient(patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Patient not found")
    return JSONResponse(content={"deleted": True})
