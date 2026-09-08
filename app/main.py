"""FastAPI entry point for the APRENDIZ service."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.agent_export_routes import router as agent_export_router
from app.api.agent_routes import router as agent_router
from app.api.routes import router
from app.api.processing_routes import router as processing_router
from app.api.learning_routes import router as learning_router
from app.api.computer_execution_routes import router as computer_execution_router
from app.api.computer_practice_routes import router as computer_practice_router
from app.api.project_routes import router as project_router
from app.api.qc_routes import router as qc_router
from app.api.project_video_procedure_routes import router as project_video_procedure_router
from app.api.robot_profile_routes import router as robot_profile_router
from app.api.source_routes import router as source_router
from app.api.training_routes import router as training_router
from app.api.upload_routes import router as upload_router
from app.api.video_extraction_routes import router as video_extraction_router
from app.services.spend_ledger import SpendCeilingReached, SpendLedgerNotConfigured


APP_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="APRENDIZ",
    description="Procedural knowledge acquisition from human demonstrations.",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
app.include_router(router)
app.include_router(agent_router)
app.include_router(agent_export_router)
app.include_router(processing_router)
app.include_router(learning_router)
app.include_router(computer_execution_router)
app.include_router(computer_practice_router)
app.include_router(project_router)
app.include_router(qc_router)
app.include_router(project_video_procedure_router)
app.include_router(robot_profile_router)
app.include_router(source_router)
app.include_router(training_router)
app.include_router(upload_router)
app.include_router(video_extraction_router)


# Registered on the application rather than in each route, so an endpoint added
# later cannot spend past the ceiling by forgetting to catch this.
@app.exception_handler(SpendCeilingReached)
async def _spend_ceiling_reached(
    request: Request,
    error: SpendCeilingReached,
) -> JSONResponse:
    """Refuse a call that would spend past the operator's own ceiling."""
    return JSONResponse(
        status_code=402,
        content={"detail": str(error), "spend": error.state.model_dump(mode="json")},
    )


@app.exception_handler(SpendLedgerNotConfigured)
async def _spend_ledger_not_configured(
    request: Request,
    error: SpendLedgerNotConfigured,
) -> JSONResponse:
    """Refuse rather than serve a ceiling that cannot be measured against."""
    return JSONResponse(status_code=503, content={"detail": str(error)})
