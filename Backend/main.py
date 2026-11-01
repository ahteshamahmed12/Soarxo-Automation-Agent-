"""Sorax Automation Backend — FastAPI application entry point."""

from fastapi import FastAPI

from src.api.auth import router as auth_router
from src.core.config import settings
from src.core.database import init_db

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

app.include_router(auth_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()
