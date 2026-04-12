"""Drug Formulary API endpoints -- WHO Essential Medicines reference lookup."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional

from backend.services.formulary_service import (
    get_all_drugs,
    search_drugs,
    get_drug,
)

router = APIRouter(prefix="/api", tags=["formulary"])


@router.get("/formulary")
async def list_drugs():
    """List all drugs in the WHO Essential Medicines formulary."""
    drugs = get_all_drugs()
    return JSONResponse(content=drugs)


@router.get("/formulary/search")
async def search_formulary(q: Optional[str] = Query(None)):
    """Search drugs by name, category, or indication."""
    if not q or not q.strip():
        drugs = get_all_drugs()
    else:
        drugs = search_drugs(q.strip())
    return JSONResponse(content=drugs)


@router.get("/formulary/{drug_id}")
async def read_drug(drug_id: str):
    """Get detailed information for a single drug by ID."""
    drug = get_drug(drug_id)
    if not drug:
        raise HTTPException(status_code=404, detail="Drug not found in formulary")
    return JSONResponse(content=drug)
