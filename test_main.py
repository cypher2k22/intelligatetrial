from fastapi.testclient import TestClient
from PIL import Image
import io

import main

client = TestClient(main.app)


def image_bytes():
    image = Image.new("RGB", (160, 60), color="white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_rejects_unsupported_type():
    response = client.post(
        "/ocr",
        files={"image": ("plate.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 415


def test_rejects_invalid_image():
    response = client.post(
        "/ocr",
        files={"image": ("plate.png", b"not an image", "image/png")},
    )
    assert response.status_code == 400


def test_ocr_response_marks_manual_review(monkeypatch):
    monkeypatch.setattr(main, "extract_text", lambda image: "ABC 1234")
    response = client.post(
        "/ocr",
        files={"image": ("plate.png", image_bytes(), "image/png")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["plate_candidates"] == ["ABC1234"]
    assert data["requires_manual_review"] is True
