from pathlib import Path

from fastapi import APIRouter

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
COMPANY_FILE = BASE_DIR / "knowledge" / "company.md"


@router.get("/info")
def company_info():

    if COMPANY_FILE.exists():
        return {
            "content": COMPANY_FILE.read_text(
                encoding="utf-8"
            )
        }

    return {
        "error": f"File not found: {COMPANY_FILE}"
    }