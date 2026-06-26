from fastapi import FastAPI

app = FastAPI(
    title="RAVAND OS",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "project": "RAVAND OS",
        "status": "running",
        "message": "Welcome Javad 🚀"
    }