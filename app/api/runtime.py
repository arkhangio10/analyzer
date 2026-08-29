"""Shared in-memory service graph for the local MVP process."""

from app.services.browser_execution_service import BrowserExecutionService
from app.services.computer_execution_service import ComputerExecutionService
from app.services.computer_practice_service import ComputerPracticeService
from app.services.project_service import ProjectService


project_service = ProjectService()
computer_execution_service = ComputerExecutionService()
browser_execution_service = BrowserExecutionService()
computer_practice_service = ComputerPracticeService(
    project_service,
    browser_execution_service,
)
