"""Feed a project's approved procedures into the reconciler, honestly.

The reconciler has always been able to compare procedures; nothing supplied it
with any. This connects it to the extractions a person actually approved, and
reports one thing the reconciler itself cannot know: whether those extractions
came from different videos.

That distinction is the whole point. Two readings of the same video agreeing
means the model repeated itself. Only two different sources agreeing is
evidence about the task rather than about the model.
"""

from __future__ import annotations

from app.agents.reconciler import ReconcilerAgent
from app.models.learning import (
    ProcedureEvidence,
    ProjectReconciliation,
    ReconciledSource,
    ReconciliationRequest,
)
from app.models.project_video_procedure import (
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureStatus,
)


CROSS_SOURCE_NOTE = (
    "These procedures came from different approved videos, so agreement "
    "between them is evidence about the task rather than about one model run."
)
SAME_SOURCE_NOTE = (
    "Every approved procedure here came from the same video, so agreement "
    "shows the model repeating itself, not independent confirmation. Approve a "
    "second, different source before treating this as validation."
)


class NotEnoughApprovedSourcesError(ValueError):
    """Raised when fewer than two approved procedures exist to compare."""


class ProjectReconciliationService:
    """Reconcile a project's approved procedures and report their independence."""

    def __init__(self, reconciler: ReconcilerAgent | None = None) -> None:
        self._reconciler = reconciler or ReconcilerAgent()

    def reconcile(
        self,
        project_id: str,
        records: list[ProjectVideoProcedureRecord],
        task: str,
    ) -> ProjectReconciliation:
        """Compare every approved procedure, or refuse when there are too few."""
        approved = [
            record
            for record in sorted(records, key=lambda item: item.created_at)
            if record.status is ProjectVideoProcedureStatus.APPROVED
            and record.procedure is not None
        ]
        if len(approved) < 2:
            raise NotEnoughApprovedSourcesError(
                f"Reconciliation compares approved procedures, and this project "
                f"has {len(approved)}. Approve a second extraction first."
            )

        result = self._reconciler.reconcile(
            ReconciliationRequest(
                task=task,
                sources=[
                    ProcedureEvidence(
                        source_id=record.extraction_id,
                        approved=True,
                        procedure=record.procedure,
                    )
                    for record in approved
                ],
            )
        )
        distinct = len({record.source_url for record in approved})
        cross_source = distinct >= 2
        return ProjectReconciliation(
            project_id=project_id,
            result=result,
            sources=[
                ReconciledSource(
                    extraction_id=record.extraction_id,
                    procedure_version=record.procedure_version,
                    source_url=record.source_url,
                    step_count=len(record.procedure.steps),
                )
                for record in approved
            ],
            distinct_source_count=distinct,
            is_cross_source=cross_source,
            independence_note=CROSS_SOURCE_NOTE if cross_source else SAME_SOURCE_NOTE,
        )
