"""Shared in-memory service graph for the local MVP process."""

from app.services.browser_execution_service import BrowserExecutionService
from app.services.computer_execution_service import ComputerExecutionService
from app.services.computer_practice_service import ComputerPracticeService
from app.services.gemini_service import GeminiService
from app.services.project_service import ProjectService
from app.services.project_video_procedure_service import ProjectVideoProcedureService


project_service = ProjectService()
computer_execution_service = ComputerExecutionService()
browser_execution_service = BrowserExecutionService()
gemini_service = GeminiService()
computer_practice_service = ComputerPracticeService(
    project_service,
    browser_execution_service,
)
project_video_procedure_service = ProjectVideoProcedureService(
    project_service,
    gemini_service,
)
