"""QR Code Patient ID endpoint -- generates QR codes for patient identification."""

import base64
import io
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api", tags=["qrcode"])


@router.get("/patients/{patient_id}/qr")
async def generate_patient_qr(patient_id: str):
    """Generate a QR code containing patient identification data.

    Returns a base64-encoded PNG image of the QR code containing
    patient_id, name, DOB, and blood_type.
    """
    from backend.services.patient_service import get_patient

    patient = get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    try:
        import qrcode
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="qrcode library not installed. Run: pip install qrcode[pil]",
        )

    # Data to encode in QR
    qr_data = json.dumps({
        "patient_id": patient.get("patient_id", ""),
        "name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}",
        "dob": patient.get("date_of_birth", ""),
        "blood_type": patient.get("blood_type", ""),
    })

    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return JSONResponse(content={
        "qr_base64": b64,
        "patient_id": patient.get("patient_id", ""),
        "name": f"{patient.get('first_name', '')} {patient.get('last_name', '')}",
        "dob": patient.get("date_of_birth", ""),
        "blood_type": patient.get("blood_type", ""),
        "allergies": patient.get("allergies", []),
    })
