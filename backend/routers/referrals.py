"""Referral Letter API endpoints -- generate and retrieve clinical referral letters."""

import traceback
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from backend.services.referral_service import (
    generate_referral,
    get_referrals_by_patient,
    get_referral,
)

router = APIRouter(prefix="/api", tags=["referrals"])


class ReferralRequest(BaseModel):
    patient_id: str
    visit_id: str = ""
    referral_reason: str
    urgency: str = "routine"
    referring_facility: str = ""
    receiving_facility: str = ""


@router.post("/referrals/generate", status_code=201)
async def create_referral(req: ReferralRequest):
    """Generate a clinical referral letter using Gemma 4.

    Takes patient and visit data, generates a structured referral letter
    suitable for printing and sending with the patient to the receiving facility.
    """
    if not req.patient_id.strip():
        raise HTTPException(status_code=400, detail="patient_id is required")
    if not req.referral_reason.strip():
        raise HTTPException(status_code=400, detail="referral_reason is required")

    valid_urgencies = ["emergency", "urgent", "routine"]
    if req.urgency.lower() not in valid_urgencies:
        raise HTTPException(
            status_code=400,
            detail=f"urgency must be one of: {', '.join(valid_urgencies)}",
        )

    try:
        referral = await generate_referral(req.model_dump())
        return JSONResponse(content=referral, status_code=201)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/referrals")
async def list_referrals(patient_id: Optional[str] = Query(None)):
    """List referral history for a patient."""
    if not patient_id:
        raise HTTPException(status_code=400, detail="patient_id query parameter is required")

    referrals = get_referrals_by_patient(patient_id)
    return JSONResponse(content=referrals)


@router.get("/referrals/{referral_id}")
async def read_referral(referral_id: str):
    """Get a single referral by ID."""
    referral = get_referral(referral_id)
    if not referral:
        raise HTTPException(status_code=404, detail="Referral not found")
    return JSONResponse(content=referral)
