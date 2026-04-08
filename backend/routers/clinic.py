"""Clinic Copilot API endpoint -- differential diagnosis support."""

import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.services.clinic_copilot import assess_patient

router = APIRouter(prefix="/api", tags=["clinic"])


class ClinicRequest(BaseModel):
    symptoms: str
    patient_age: str
    patient_sex: str
    image: str = ""
    language: str = "en"


@router.post("/clinic")
async def clinic_assess(req: ClinicRequest):
    """Assess patient symptoms and provide differential diagnosis guidance.

    Supports text-only or multimodal (text + image) assessment.
    Send base64-encoded image in the 'image' field for visual symptom analysis.
    """
    if not req.symptoms.strip():
        raise HTTPException(status_code=400, detail="Symptoms description cannot be empty")
    if len(req.symptoms) > 50000:
        raise HTTPException(status_code=400, detail="Symptoms description exceeds 50,000 character limit")

    try:
        result = await assess_patient(
            symptoms=req.symptoms,
            patient_age=req.patient_age,
            patient_sex=req.patient_sex,
            image=req.image,
            language=req.language,
        )
        return JSONResponse(content=result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
