from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():
    return {
        "project": "RAVAND OS",
        "status": "running",
        "message": "Welcome Javad 🚀"
    }