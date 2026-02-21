# backend/main.py

from fastapi import FastAPI 
from backend.api.routes import router

app = FastAPI(title="Intelligent Document Assistant")

app.include_router(router)

@app.get("/")
def root():
    return {"status": "Backend is running"}
