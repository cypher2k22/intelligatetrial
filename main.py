import io
import os
import re

import pytesseract
from fastapi import FastAPI, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

app = FastAPI(
    title="IntelliGate OCR API",
    description="Starter OCR service for vehicle-entry verification prototypes.",
    version="0.1.0",
)

MAX_IMAGE_BYTES = int(os.getenv("MAX_IMAGE_BYTES", str(5 * 1024 * 1024)))
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


def extract_text(image: Image.Image) -> str:
    """Run OCR on an uploaded image. OCR output must be reviewed before access decisions."""
    return pytesseract.image_to_string(image, config="--psm 6")


def find_plate_candidates(text: str) -> list[str]:
    """Return conservative alphanumeric candidates for review, not verified plate numbers."""
    normalized = re.sub(r"[^A-Z0-9\s-]", " ", text.upper())
    candidates = re.findall(r"\b[A-Z0-9]{2,4}[- ]?[A-Z0-9]{3,6}\b", normalized)
    return list(dict.fromkeys(re.sub(r"[-\s]", "", candidate) for candidate in candidates))


@app.get("/health")
def health():
    return {"status": "ok", "service": "intelligate-ocr-api"}


@app.post("/ocr")
async def recognize_plate(image: UploadFile = File(...)):
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=415, detail="Upload a JPEG, PNG, or WebP image")

    data = await image.read(MAX_IMAGE_BYTES + 1)
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded image is empty")
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail=f"Image exceeds {MAX_IMAGE_BYTES} bytes")

    try:
        with Image.open(io.BytesIO(data)) as uploaded:
            uploaded.verify()
        with Image.open(io.BytesIO(data)) as uploaded:
            image_rgb = uploaded.convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError):
        raise HTTPException(status_code=400, detail="Uploaded file is not a valid image") from None
    finally:
        await image.close()

    try:
        text = extract_text(image_rgb).strip()
    except Exception:
        raise HTTPException(status_code=503, detail="OCR processing is unavailable") from None

    return {
        "text": text,
        "plate_candidates": find_plate_candidates(text),
        "requires_manual_review": True,
        "notice": "OCR candidates are not verified identities. Confirm the plate and authorization before granting entry.",
    }
