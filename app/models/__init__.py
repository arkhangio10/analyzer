"""Typed data contracts for APRENDIZ."""

from app.models.evaluation import EvaluationResult
from app.models.browser_execution import (
    ComputerBrowserActionExecution,
    ComputerBrowserExecutionRequest,
    ComputerBrowserExecutionResult,
)
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
from app.models.computer_practice import (
    ComputerPractice,
    ComputerPracticeApprovalRequest,
    ComputerPracticeDraftRequest,
    ComputerPracticeRunResult,
    ComputerPracticeStatus,
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
from app.models.robot_profile import (
    ARP1MotionContract,
    ARP1RobotProfile,
    RobotDescriptionFormat,
    RobotJointProfile,
    RobotLinkProfile,
    SimulatorRecommendation,
    URDFImportRequest,
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
    "ComputerBrowserActionExecution",
    "ComputerBrowserExecutionRequest",
    "ComputerBrowserExecutionResult",
    "ComputerAction",
    "ComputerActionExecution",
    "ComputerActionKind",
    "ComputerActionStatus",
    "ComputerExecutionStatus",
    "ComputerPlanValidationRequest",
    "ComputerPlanValidationResult",
    "ComputerSandboxExecutionRequest",
    "ComputerSandboxExecutionResult",
    "ComputerPractice",
    "ComputerPracticeApprovalRequest",
    "ComputerPracticeDraftRequest",
    "ComputerPracticeRunResult",
    "ComputerPracticeStatus",
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
    "ARP1RobotProfile",
    "ARP1MotionContract",
    "RobotDescriptionFormat",
    "RobotJointProfile",
    "RobotLinkProfile",
    "SimulatorRecommendation",
    "URDFImportRequest",
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
