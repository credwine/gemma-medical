"""Analytics API endpoint -- clinic dashboard statistics."""

import traceback
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from backend.services.analytics_service import get_summary

router = APIRouter(prefix="/api", tags=["analytics"])


@router.get("/analytics/summary")
async def analytics_summary():
    """Return clinic summary statistics: patient counts, visit counts,
    top diagnoses, and recent visits."""
    try:
        result = get_summary()
        return JSONResponse(content=result)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
