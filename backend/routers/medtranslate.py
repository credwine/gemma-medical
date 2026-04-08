"""Medical Translator API endpoint -- cross-language symptom translation."""

import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.services.medical_translator import translate_medical

router = APIRouter(prefix="/api", tags=["medtranslate"])


class MedTranslateRequest(BaseModel):
    patient_description: str
    source_language: str = "auto"
    target_language: str = "en"
    language: str = "en"


@router.post("/medtranslate")
async def medtranslate(req: MedTranslateRequest):
    """Translate patient symptom descriptions into standardized clinical terminology.

    Converts colloquial, cultural, and vernacular health descriptions from
    local languages into clear clinical English.
    """
    if not req.patient_description.strip():
        raise HTTPException(status_code=400, detail="Patient description cannot be empty")
    if len(req.patient_description) > 50000:
        raise HTTPException(status_code=400, detail="Patient description exceeds 50,000 character limit")

    try:
        result = await translate_medical(
            patient_description=req.patient_description,
            source_language=req.source_language,
            target_language=req.target_language,
            language=req.language,
        )
        return JSONResponse(content=result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
