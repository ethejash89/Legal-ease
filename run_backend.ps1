if (-not (Test-Path ".venv")) {
    py -3.13 -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
