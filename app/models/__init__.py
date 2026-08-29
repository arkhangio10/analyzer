"""Typed data contracts for APRENDIZ."""

from app.models.evaluation import EvaluationResult
from app.models.computer_execution import (
    ComputerAction,
    ComputerActionExecution,
    ComputerActionKind,
    ComputerActionStatus,
    ComputerExecutionStatus,
    ComputerPlanValidationRequest,
    ComputerPlanValidationResult,
    ComputerSandboxExecutionRequest,
    ComputerSandboxExecutionResult,
)
from app.models.learning import (
    FrozenEvaluationRequest,
    FrozenEvaluationResult,
    ProcedureEvidence,
    ReconciliationRequest,
    ReconciliationResult,
)
from app.models.procedure import Procedure, ProcedureStep
from app.models.processing import (
    ProcessingStatus,
    RobotMotionProcessingRequest,
    RobotMotionProcessingSession,
)
from app.models.project import (
    ClarificationQuestion,
    ComputerExecutionContract,
    ExecutionDestination,
    ProjectClarificationRequest,
    ProjectDraft,
    RobotExecutionContract,
)
from app.models.robot_motion import (
    JointLimit,
    MotionWaypoint,
    RobotMotionEvaluationRequest,
    RobotMotionMetrics,
    RobotMotionTrainingRequest,
    RobotMotionTrainingResult,
    RobotMotionTrainingStatus,
)
from app.models.skill import Skill
from app.models.source import (
    SourceApprovalRequest,
    SourceApprovalResult,
    SourceSearchRequest,
    SourceSearchResult,
    VideoCandidate,
)
from app.models.task import TaskDefinition
from app.models.training import TrainingExample
from app.models.video_extraction import (
    GeminiUsage,
    VideoExtractionRequest,
    VideoExtractionResult,
)

__all__ = [
    "EvaluationResult",
    "ComputerAction",
    "ComputerActionExecution",
    "ComputerActionKind",
    "ComputerActionStatus",
    "ComputerExecutionStatus",
    "ComputerPlanValidationRequest",
    "ComputerPlanValidationResult",
    "ComputerSandboxExecutionRequest",
    "ComputerSandboxExecutionResult",
    "FrozenEvaluationRequest",
    "FrozenEvaluationResult",
    "ProcedureEvidence",
    "ReconciliationRequest",
    "ReconciliationResult",
    "Procedure",
    "ProcedureStep",
    "ProcessingStatus",
    "RobotMotionProcessingRequest",
    "RobotMotionProcessingSession",
    "ClarificationQuestion",
    "ComputerExecutionContract",
    "ExecutionDestination",
    "ProjectClarificationRequest",
    "ProjectDraft",
    "RobotExecutionContract",
    "JointLimit",
    "MotionWaypoint",
    "RobotMotionEvaluationRequest",
    "RobotMotionMetrics",
    "RobotMotionTrainingRequest",
    "RobotMotionTrainingResult",
    "RobotMotionTrainingStatus",
    "Skill",
    "SourceApprovalRequest",
    "SourceApprovalResult",
    "SourceSearchRequest",
    "SourceSearchResult",
    "VideoCandidate",
    "TaskDefinition",
    "TrainingExample",
    "GeminiUsage",
    "VideoExtractionRequest",
    "VideoExtractionResult",
]
