"""APRENDIZ agent boundaries, implemented and not.

`QcPipeline` is implemented: a deterministic ADK pipeline that checks stored
metadata against stored observations and stops at the human review gate. It
reads what the services already produced and initiates no provider call.

The rest are boundaries that deliberately raise rather than return something
fabricated. They describe work that is not done, and `tests/unit/
test_agent_boundaries.py` holds them to it. They are not superseded by the QC
pipeline, which orchestrates existing evidence rather than performing the
understanding, extraction, practice, or execution those boundaries name.
"""

from app.agents.evaluator import EvaluatorAgent
from app.agents.executor import ExecutorAgent
from app.agents.practice_agent import PracticeAgent
from app.agents.procedure_extractor import ProcedureExtractorAgent
from app.agents.qc_pipeline import (
    ApprovalGateStage,
    AuditStage,
    ExtractionStage,
    IngestStage,
    MotionStage,
    PipelineDeps,
    PipelineStage,
    QcPipeline,
    ReportStage,
    run_qc_pipeline,
)
from app.agents.reconciler import ReconcilerAgent
from app.agents.root_agent import RootAgent
from app.agents.task_clarifier import TaskClarifierAgent
from app.agents.video_instructor import VideoInstructorAgent

__all__ = [
    "ApprovalGateStage",
    "AuditStage",
    "EvaluatorAgent",
    "ExecutorAgent",
    "ExtractionStage",
    "IngestStage",
    "MotionStage",
    "PipelineDeps",
    "PipelineStage",
    "PracticeAgent",
    "ProcedureExtractorAgent",
    "QcPipeline",
    "ReconcilerAgent",
    "ReportStage",
    "RootAgent",
    "TaskClarifierAgent",
    "VideoInstructorAgent",
    "run_qc_pipeline",
]
