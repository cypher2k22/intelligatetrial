# IntelliGate — Vehicle Entry OCR API (Starter)

IntelliGate is intended to support vehicle-entry verification by reading number-plate text from images and comparing the result with an authorized-vehicle registry. This repository was empty, so this commit establishes a runnable **OCR API starter**, not a complete access-control product.

## Included

- FastAPI service with health endpoint
- JPEG, PNG, and WebP upload validation
- Upload size limit
- OCR via Tesseract / pytesseract
- Conservative plate-text candidate extraction
- Explicit manual-review warning; OCR alone must never authorize entry

## Requirements

- Python 3.10+
- Tesseract OCR installed on the host
  - macOS: `brew install tesseract`
  - Debian/Ubuntu: `sudo apt-get install tesseract-ocr`
- Python packages below

## Run locally

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## API

- `GET /health` — health check
- `POST /ocr` — multipart form upload with field name `image`

Example:

```bash
curl -X POST http://127.0.0.1:8000/ocr \
  -F "image=@sample-plate.jpg"
```

Response includes extracted text, possible plate candidates, and a mandatory manual-review flag. Candidate matching is intentionally heuristic; real-world plate formats, camera quality, lighting, and OCR errors require dataset-based evaluation.

## Tests

```bash
pytest
```

## Important limitations

This is not yet the complete mobile + authorization system described in the project concept. It does not include the React Native app, an authorized-vehicle database, user roles, audit logs, camera capture, or production deployment. Add those components and test against representative local plate images before claiming end-to-end vehicle verification.

Never expose this API publicly without authentication, rate limits, appropriate privacy controls, and deployment hardening.
