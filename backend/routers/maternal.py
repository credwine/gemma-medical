"""Maternal Health Monitor API endpoint -- pregnancy risk assessment."""

import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.services.maternal_monitor import assess_maternal

router = APIRouter(prefix="/api", tags=["maternal"])


class MaternalRequest(BaseModel):
    gestational_weeks: int
    symptoms: str
    vitals: str = ""
    history: str = ""
    language: str = "en"


@router.post("/maternal")
async def maternal_assess(req: MaternalRequest):
    """Assess maternal health risks based on symptoms and gestational age.

    Provide gestational weeks, symptoms, and optionally vitals and obstetric history.
    """
    if not req.symptoms.strip():
        raise HTTPException(status_code=400, detail="Symptoms description cannot be empty")
    if req.gestational_weeks < 0 or req.gestational_weeks > 45:
        raise HTTPException(status_code=400, detail="Gestational weeks must be between 0 and 45")
    if len(req.symptoms) > 50000:
        raise HTTPException(status_code=400, detail="Symptoms description exceeds 50,000 character limit")

    try:
        result = await assess_maternal(
            gestational_weeks=req.gestational_weeks,
            symptoms=req.symptoms,
            vitals=req.vitals,
            history=req.history,
            language=req.language,
        )
        return JSONResponse(content=result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
