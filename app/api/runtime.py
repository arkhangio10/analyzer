"""Shared service graph for the local MVP process.

Workflow records are written under the configured data directory so a paid
extraction and its human review survive a restart. When that directory is
not writable the services keep working in memory and report that they are
not durable.
"""

from pathlib import Path

from app.agents.evaluator import EvaluatorAgent
from app.core.config import get_settings
from app.services.adaptation_service import DestinationAdaptationService
from app.services.browser_execution_service import BrowserExecutionService
from app.services.computer_execution_service import ComputerExecutionService
from app.services.computer_practice_service import ComputerPracticeService
from app.services.gemini_service import GeminiService
from app.services.motion_analysis_service import MotionAnalysisService
from app.services.frozen_case_store import (
    load_frozen_cases,
    resolve_frozen_cases_dir,
)
from app.services.project_reconciliation_service import (
    ProjectReconciliationService,
)
from app.services.project_service import ProjectService
from app.services.project_video_procedure_service import ProjectVideoProcedureService
from app.services.record_store import JsonRecordStore
from app.services.robot_motion_training import RobotMotionTrainingService
from app.services.storage_service import LocalVideoStorage


_settings = get_settings()
_data_root = Path(_settings.data_dir)
_records_root = _data_root / "records"

evaluator = EvaluatorAgent(
    load_frozen_cases(resolve_frozen_cases_dir(_settings.frozen_cases_dir)),
)

project_service = ProjectService(
    store=JsonRecordStore(_records_root / "projects"),
)
adaptation_service = DestinationAdaptationService()
project_reconciliation_service = ProjectReconciliationService()
computer_execution_service = ComputerExecutionService(
    store=JsonRecordStore(_records_root / "computer-executions"),
)
browser_execution_service = BrowserExecutionService(
    store=JsonRecordStore(_records_root / "browser-executions"),
)
gemini_service = GeminiService()
computer_practice_service = ComputerPracticeService(
    project_service,
    browser_execution_service,
    store=JsonRecordStore(_records_root / "computer-practices"),
)
robot_motion_training_service = RobotMotionTrainingService(
    store=JsonRecordStore(_records_root / "robot-motion-sessions"),
)
project_video_procedure_service = ProjectVideoProcedureService(
    project_service,
    gemini_service,
    store=JsonRecordStore(_records_root / "video-procedures"),
)
motion_analysis_service = MotionAnalysisService(
    gemini_service,
    store=JsonRecordStore(_records_root / "motion-analyses"),
)
video_storage = LocalVideoStorage(
    _data_root / "uploads",
    store=JsonRecordStore(_records_root / "uploads"),
)
