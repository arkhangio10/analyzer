"""Shared service graph for the running process.

Workflow records are written wherever this deployment can keep them: under the
configured data directory on a machine that has one, or in a Cloud Storage
bucket when `GCS_BUCKET` names one, because a stateless container has no disk
that survives it. Setting the bucket is what switches both records and uploads
over; nothing else in the graph changes, which is what the `RecordStore`
contract is for.

When neither destination can be written the services keep working in memory and
report that they are not durable, rather than failing the request that produced
the record.
"""

from pathlib import Path

from app.agents.evaluator import EvaluatorAgent
from app.core.config import get_settings
from app.services.adaptation_service import DestinationAdaptationService
from app.services.browser_execution_service import BrowserExecutionService
from app.services.computer_execution_service import ComputerExecutionService
from app.services.computer_practice_service import ComputerPracticeService
from app.services.evidence_store import EvidenceStore
from app.services.gcs_record_store import GcsRecordStore
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
from app.services.record_store import JsonRecordStore, RecordStore
from app.services.robot_motion_training import RobotMotionTrainingService
from app.services.storage_service import (
    GcsVideoStorage,
    LocalVideoStorage,
    VideoStorage,
)


_settings = get_settings()
_data_root = Path(_settings.data_dir)
_records_root = _data_root / "records"
_bucket = _settings.gcs_bucket


def _record_store(name: str) -> RecordStore:
    """Return the store this deployment can actually keep records in."""
    if _bucket:
        return GcsRecordStore(_bucket, f"records/{name}")
    return JsonRecordStore(_records_root / name)


def _video_storage() -> VideoStorage:
    """Return the destination this deployment can actually keep uploads in."""
    if _bucket:
        return GcsVideoStorage(_bucket, "uploads", store=_record_store("uploads"))
    return LocalVideoStorage(_data_root / "uploads", store=_record_store("uploads"))

evaluator = EvaluatorAgent(
    load_frozen_cases(resolve_frozen_cases_dir(_settings.frozen_cases_dir)),
)

project_service = ProjectService(
    store=_record_store("projects"),
)
adaptation_service = DestinationAdaptationService()
project_reconciliation_service = ProjectReconciliationService()
computer_execution_service = ComputerExecutionService(
    store=_record_store("computer-executions"),
)
browser_execution_service = BrowserExecutionService(
    store=_record_store("browser-executions"),
)
gemini_service = GeminiService()
computer_practice_service = ComputerPracticeService(
    project_service,
    browser_execution_service,
    store=_record_store("computer-practices"),
)
robot_motion_training_service = RobotMotionTrainingService(
    store=_record_store("robot-motion-sessions"),
)
project_video_procedure_service = ProjectVideoProcedureService(
    project_service,
    gemini_service,
    store=_record_store("video-procedures"),
)
evidence_store = EvidenceStore(_settings)
motion_analysis_service = MotionAnalysisService(
    gemini_service,
    store=_record_store("motion-analyses"),
    evidence_store=evidence_store,
)
video_storage = _video_storage()
