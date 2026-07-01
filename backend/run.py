"""
RAVAND OS – Server Launcher
===========================
Run from the /backend directory:

    python run.py

This script sets the working directory correctly so all relative
paths (SQLite DB, .env, logs) resolve as expected.
"""

import os
import sys
from pathlib import Path

# Ensure the backend/ directory is always the working directory,
# regardless of where this script is invoked from.
BACKEND_DIR = Path(__file__).resolve().parent
os.chdir(BACKEND_DIR)

# Add backend/ to sys.path so 'app.*' imports resolve correctly
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import uvicorn

from app.core.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
    )
