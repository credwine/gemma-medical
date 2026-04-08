"""Drug Interaction Checker API endpoint -- medication safety analysis."""

import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.services.drug_checker import check_interactions

router = APIRouter(prefix="/api", tags=["drugs"])


class DrugRequest(BaseModel):
    medications: str
    patient_conditions: str = ""
    image: str = ""
    language: str = "en"


@router.post("/drugs")
async def drug_check(req: DrugRequest):
    """Check for drug interactions between listed medications.

    Supports text-only or multimodal (text + image) analysis.
    Send base64-encoded image of medication packaging or prescriptions.
    """
    if not req.medications.strip() and not req.image:
        raise HTTPException(status_code=400, detail="Provide medication names or an image of medications")
    if len(req.medications) > 50000:
        raise HTTPException(status_code=400, detail="Medications text exceeds 50,000 character limit")

    try:
        result = await check_interactions(
            medications=req.medications,
            patient_conditions=req.patient_conditions,
            image=req.image,
            language=req.language,
        )
        return JSONResponse(content=result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
