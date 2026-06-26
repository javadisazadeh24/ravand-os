from pathlib import Path

from fastapi import FastAPI

app = FastAPI(
    title="RAVAND OS",
    version="0.1.0"
)

BASE_DIR = Path(__file__).resolve().parent.parent
COMPANY_FILE = BASE_DIR / "knowledge" / "company.md"


@app.get("/")
def root():
    return {
        "project": "RAVAND OS",
        "status": "running"
    }


@app.get("/company")
def company():
    if COMPANY_FILE.exists():
        return {
            "content": COMPANY_FILE.read_text(encoding="utf-8")
        }

    return {
        "error": "company.md not found"
    }