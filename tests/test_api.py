import os

os.environ["MOCK_AI"] = "true"
os.environ["GEMINI_API_KEY"] = ""

from fastapi.testclient import TestClient

from backend.main import app
from backend.services.document_service import format_html_preview, sanitize_text
from backend.services.export_service import export_docx, export_pdf, export_txt

client = TestClient(app)


def sample_payload():
    return {
        "document_type": "Non-Disclosure Agreement",
        "parties": "Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)",
        "terms": "Confidentiality; No unauthorized disclosure; 30 day termination notice",
        "effective_date": "2026-10-06",
        "jurisdiction": "India",
        "additional_instructions": "Use professional language.",
    }


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_mock():
    response = client.post("/generate", json=sample_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["mock"] is True
    assert "NON-DISCLOSURE AGREEMENT" in body["content"]


def test_validation():
    payload = sample_payload()
    payload["terms"] = ""
    response = client.post("/generate", json=payload)
    assert response.status_code == 422


def test_preview():
    response = client.post(
        "/preview",
        json={"document_type": "NDA", "content": "1. CONFIDENTIALITY\nProtect information."},
    )
    assert response.status_code == 200
    assert "CONFIDENTIALITY" in response.json()["html"]


def test_exports():
    content = "NDA\n\n1. CONFIDENTIALITY\nProtect information."
    payload = {"document_type": "NDA", "content": content}

    txt = client.post("/export/txt", json=payload)
    docx = client.post("/export/docx", json=payload)
    pdf = client.post("/export/pdf", json=payload)

    assert txt.status_code == 200
    assert txt.headers["content-type"].startswith("text/plain")
    assert txt.content.startswith(b"NDA")

    assert docx.status_code == 200
    assert docx.content.startswith(b"PK")  # DOCX is a ZIP package

    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF")


def test_helpers():
    assert sanitize_text("Hello\u2014world") == "Hello-world"
    html = format_html_preview("TITLE\n\n1. SECTION\nBody")
    assert "<h2>TITLE</h2>" in html
    assert "SECTION" in html
    assert export_txt("hello") == b"hello"
    assert export_docx("hello", "NDA").startswith(b"PK")
    assert export_pdf("hello", "NDA").startswith(b"%PDF")
