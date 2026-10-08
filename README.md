# LegalEase — AI-Powered Legal Document Generator

LegalEase is a full-stack demo application based on the supplied project specification:
- Streamlit frontend
- FastAPI backend
- Google Gemini generation
- Editable document preview
- TXT, DOCX and PDF export
- Optional logo/branding
- Automated tests
- Local mock mode so the app can be tested without an API key

> Legal disclaimer: LegalEase generates draft text for informational/productivity purposes. It is not a law firm and does not provide legal advice. Users should have important documents reviewed by a qualified lawyer in the relevant jurisdiction.

## Architecture

```text
Streamlit UI
   |
   | POST /generate
   v
FastAPI
   |
   v
GeminiDocumentGenerator
   |
   v
Google Gemini API

Generated text
   |
   +--> editable preview
   +--> TXT
   +--> DOCX
   +--> PDF
```

The supplied PDF specifies Streamlit, FastAPI, Gemini, editable previews, and TXT/DOCX/PDF export. This implementation keeps that architecture while using the current `google-genai` SDK.

## Requirements

- Python 3.11–3.13
- VS Code
- A Gemini API key for live AI generation (optional for local mock mode)

## Windows / VS Code setup

Open the project folder in VS Code.

### 1. Create a virtual environment

PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure `.env`

Copy `.env.example` to `.env`.

For live Gemini:

```env
GEMINI_API_KEY=your_real_key_here
GEMINI_MODEL=gemini-3.8-flash
MOCK_AI=false
BACKEND_URL=http://127.0.0.1:8000
```

If you only want to test the application without Gemini:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.8-flash
MOCK_AI=true
BACKEND_URL=http://127.0.0.1:8000
```

### 4. Run backend

Terminal 1:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Test:

- http://127.0.0.1:8000/
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs

### 5. Run frontend

Terminal 2:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```

Open the URL printed by Streamlit, normally:

```text
http://localhost:8501
```

## Important Windows command note

Do NOT run:

```powershell
Python313\Scripts\uvicorn.exe
```

That is not a valid command unless you are actually inside a matching directory structure.

Use:

```powershell
python -m uvicorn backend.main:app --reload
```

after activating `.venv`. This also avoids PATH problems.

## Testing

Run:

```powershell
python -m pytest -q
```

The tests cover:
- health endpoint
- validation
- mock document generation
- TXT export
- DOCX export
- PDF export
- HTML preview
- AI fallback behavior

## API

### POST `/generate`

Example JSON:

```json
{
  "document_type": "Non-Disclosure Agreement",
  "parties": "Jane Doe (Disclosing Party), TechNova Inc. (Receiving Party)",
  "terms": "Confidential information must be protected; No disclosure to unauthorized third parties; Agreement may be terminated with 30 days notice",
  "effective_date": "2026-10-06",
  "jurisdiction": "India",
  "additional_instructions": "Use clear professional language."
}
```

### POST `/export/txt`

```json
{
  "document_type": "NDA",
  "content": "..."
}
```

### POST `/export/docx`

Same payload, returns a `.docx` binary response.

### POST `/export/pdf`

Same payload, returns a `.pdf` binary response.

## Project structure

```text
LegalEase/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── schemas.py
│   └── services/
│       ├── __init__.py
│       ├── document_service.py
│       ├── export_service.py
│       └── ai/
│           ├── __init__.py
│           └── gemini_generator.py
├── frontend/
│   ├── __init__.py
│   └── app.py
├── tests/
│   ├── __init__.py
│   └── test_api.py
├── assets/
│   └── legal_ease_logo.svg
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Procfile
└── README.md
```

## Production notes

For production:
1. Put the frontend and backend behind HTTPS.
2. Restrict CORS to the actual frontend origin.
3. Store secrets in the deployment platform's secret manager.
4. Add authentication and authorization.
5. Add request rate limiting.
6. Avoid logging confidential document contents.
7. Add jurisdiction-specific legal review before using generated templates in real legal workflows.
