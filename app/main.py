"""FastAPI entry point for the APRENDIZ service."""

from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="APRENDIZ",
    description="Procedural knowledge acquisition from human demonstrations.",
    version="0.1.0",
)
app.include_router(router)
