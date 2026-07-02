from fastapi import APIRouter
import psutil

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/status")
def system_status():
    memory = psutil.virtual_memory()

    return {
        "status": "online",
        "model": "gpt-oss:20b",
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "memory_percent": memory.percent,
        "memory_used_gb": round(memory.used / (1024**3), 2),
        "memory_total_gb": round(memory.total / (1024**3), 2),
    }