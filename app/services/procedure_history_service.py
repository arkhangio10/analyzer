"""Deterministic history and diffs across retained procedure versions.

Nothing here calls a provider or changes a stored version. It reads what was
already retained and reports the difference, so a person can see whether a
second extraction confirmed the first or quietly rewrote it.

Steps are compared by their position, because that is the only correspondence
the source actually provides. Guessing that step 4 "became" step 5 would be an
interpretation, and an interpretation presented as a diff is a lie about
evidence.
"""

from __future__ import annotations

from app.models.procedure import Procedure
from app.models.procedure_history import (
    ListDifference,
    ProcedureHistory,
    ProcedureVersionDiff,
    ProcedureVersionSummary,
    StepChangeKind,
    StepDifference,
)
from app.models.project_video_procedure import ProjectVideoProcedureRecord


COMPARED_LISTS = ("rules", "conditions", "exceptions", "uncertainties")


def _normalize(value: str) -> str:
    return " ".join((value or "").casefold().split()).rstrip(".")


def summarize(record: ProjectVideoProcedureRecord) -> ProcedureVersionSummary:
    """Describe one retained version without unpacking the whole procedure."""
    procedure = record.procedure
    return ProcedureVersionSummary(
        extraction_id=record.extraction_id,
        procedure_version=record.procedure_version,
        status=record.status,
        source_url=record.source_url,
        task=procedure.task if procedure else None,
        step_count=len(procedure.steps) if procedure else 0,
        cloud_calls_made=record.cloud_calls_made,
        total_tokens=record.usage.total_tokens,
        created_at=record.created_at,
        reviewed_at=record.reviewed_at,
    )


def _diff_steps(before: Procedure | None, after: Procedure | None) -> list[StepDifference]:
    earlier = before.steps if before else []
    later = after.steps if after else []
    differences: list[StepDifference] = []
    for index in range(max(len(earlier), len(later))):
        old = earlier[index] if index < len(earlier) else None
        new = later[index] if index < len(later) else None
        if old is None:
            kind = StepChangeKind.ADDED
        elif new is None:
            kind = StepChangeKind.REMOVED
        elif _normalize(old.action) == _normalize(new.action):
            kind = StepChangeKind.UNCHANGED
        else:
            kind = StepChangeKind.CHANGED
        differences.append(
            StepDifference(
                step=index + 1,
                kind=kind,
                before=old.action if old else None,
                after=new.action if new else None,
                before_timestamps=list(old.source_timestamps) if old else [],
                after_timestamps=list(new.source_timestamps) if new else [],
            )
        )
    return differences


def _diff_lists(
    before: Procedure | None,
    after: Procedure | None,
) -> list[ListDifference]:
    differences: list[ListDifference] = []
    for field in COMPARED_LISTS:
        earlier = {_normalize(item): item for item in getattr(before, field, [])}
        later = {_normalize(item): item for item in getattr(after, field, [])}
        added = [later[key] for key in later if key not in earlier]
        removed = [earlier[key] for key in earlier if key not in later]
        if added or removed:
            differences.append(
                ListDifference(field=field, added=added[:60], removed=removed[:60])
            )
    return differences


def diff_versions(
    earlier: ProjectVideoProcedureRecord,
    later: ProjectVideoProcedureRecord,
) -> ProcedureVersionDiff:
    """Report what changed between two retained versions, and nothing more."""
    steps = _diff_steps(earlier.procedure, later.procedure)
    counts = {kind: 0 for kind in StepChangeKind}
    for difference in steps:
        counts[difference.kind] += 1
    lists = _diff_lists(earlier.procedure, later.procedure)
    return ProcedureVersionDiff(
        project_id=later.project_id,
        from_extraction_id=earlier.extraction_id,
        to_extraction_id=later.extraction_id,
        from_version=earlier.procedure_version,
        to_version=later.procedure_version,
        same_source=earlier.source_url == later.source_url,
        from_source_url=earlier.source_url,
        to_source_url=later.source_url,
        steps=steps,
        added_step_count=counts[StepChangeKind.ADDED],
        removed_step_count=counts[StepChangeKind.REMOVED],
        changed_step_count=counts[StepChangeKind.CHANGED],
        unchanged_step_count=counts[StepChangeKind.UNCHANGED],
        lists=lists,
        has_changes=bool(
            lists
            or counts[StepChangeKind.ADDED]
            or counts[StepChangeKind.REMOVED]
            or counts[StepChangeKind.CHANGED]
        ),
    )


def build_history(
    project_id: str,
    records: list[ProjectVideoProcedureRecord],
) -> ProcedureHistory:
    """Summarize every retained version and diff the two most recent."""
    ordered = sorted(records, key=lambda record: record.created_at)
    with_procedure = [record for record in ordered if record.procedure is not None]
    latest_diff = (
        diff_versions(with_procedure[-2], with_procedure[-1])
        if len(with_procedure) >= 2
        else None
    )
    return ProcedureHistory(
        project_id=project_id,
        versions=[summarize(record) for record in ordered],
        total_cloud_calls=sum(record.cloud_calls_made for record in ordered),
        total_tokens=sum(record.usage.total_tokens or 0 for record in ordered),
        latest_diff=latest_diff,
    )
