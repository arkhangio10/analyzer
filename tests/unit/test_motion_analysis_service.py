"""Tests for paid motion analysis, its budget guard, and its retarget verdict."""

import asyncio
from datetime import datetime, timezone

import pytest

from app.models.motion_analysis import (
    MotionAnalysisCall,
    MotionAnalysisRequest,
    MotionEvidenceVerdict,
    MotionSubjectKind,
    ObservedMotionPhase,
    ObservedMotionReport,
    ProviderJointSample,
)
from app.models.project import (
    ComputerExecutionContract,
    ProjectDraft,
    RobotExecutionContract,
)
from app.models.project_video_procedure import (
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureStatus,
)
from app.models.task import TaskDefinition
from app.services.motion_analysis_service import (
    MotionAnalysisBudgetError,
    MotionAnalysisNotApprovedError,
    MotionAnalysisNotFoundError,
    MotionAnalysisService,
)


class StubGemini:
    """Stand in for the provider and record whether it was ever reached."""

    def __init__(self, report: ObservedMotionReport) -> None:
        self.report = report
        self.calls: list[dict[str, object]] = []

    async def analyze_motion(self, **kwargs: object) -> MotionAnalysisCall:
        self.calls.append(kwargs)
        return MotionAnalysisCall(
            report=self.report,
            provider="vertex_ai",
            requested_model="gemini-2.5-flash-lite",
            model_version="gemini-2.5-flash-lite",
            elapsed_seconds=1.5,
        )


def report(samples: list[ProviderJointSample]) -> ObservedMotionReport:
    return ObservedMotionReport(
        subject_kind="human_body",
        kinematic_chain="bipedal_lower_limb",
        phases=[
            ObservedMotionPhase(
                name="stance",
                start_seconds=0.0,
                end_seconds=1.0,
                description="The subject supports weight on one leg.",
            )
        ],
        samples=samples,
        uncertainties=["Clothing hides the knees."],
    )


def rows() -> list[ProviderJointSample]:
    """Mirror the shape a real call returned: both sides identical, one score."""
    return [
        ProviderJointSample(
            t=round(60.0 + index * 0.25, 3),
            j=f"{side}.hip",
            a=10.0 + index,
            c=0.7,
            v="partial",
        )
        for index in range(12)
        for side in ("left", "right")
    ]


def project(destination: str = "robot") -> ProjectDraft:
    contract = (
        RobotExecutionContract(robot_model="APRENDIZ SimArm-6")
        if destination == "robot"
        else ComputerExecutionContract(application="Google Chrome")
    )
    return ProjectDraft(
        project_id="prj_test00000001",
        task_definition=TaskDefinition(
            task_name="Walk",
            objective="Demonstrate walking mechanics.",
        ),
        destination_contract=contract,
        is_sufficiently_clear=True,
        next_action="choose_source",
    )


def record(
    status: ProjectVideoProcedureStatus = ProjectVideoProcedureStatus.APPROVED,
) -> ProjectVideoProcedureRecord:
    return ProjectVideoProcedureRecord(
        extraction_id="vpr_test00000001",
        project_id="prj_test00000001",
        procedure_version=1,
        source_url="https://youtu.be/-fD2TSL2s7I",
        status=status,
        created_at=datetime.now(timezone.utc),
    )


def request(**overrides: object) -> MotionAnalysisRequest:
    values: dict[str, object] = {"acknowledge_cloud_cost": True}
    values.update(overrides)
    return MotionAnalysisRequest(**values)


def test_an_unapproved_procedure_is_never_analysed() -> None:
    stub = StubGemini(report(rows()))
    service = MotionAnalysisService(stub)

    with pytest.raises(MotionAnalysisNotApprovedError):
        asyncio.run(
            service.analyze(
                project(),
                record(ProjectVideoProcedureStatus.AWAITING_REVIEW),
                request(),
            )
        )

    assert stub.calls == []


def test_a_request_that_would_truncate_is_refused_before_it_is_billed() -> None:
    stub = StubGemini(report(rows()))
    service = MotionAnalysisService(stub, output_token_ceiling=16384)

    with pytest.raises(MotionAnalysisBudgetError) as error:
        asyncio.run(
            service.analyze(
                project(),
                record(),
                request(frames_per_second=4.0, window_seconds=60.0),
            )
        )

    assert "nothing was billed" in str(error.value)
    assert stub.calls == []


def test_the_budget_shrinks_the_window_as_the_frame_rate_rises() -> None:
    service = MotionAnalysisService(
        StubGemini(report(rows())),
        output_token_ceiling=16384,
    )

    assert service.max_window_seconds(2.0) > service.max_window_seconds(4.0)
    assert service.max_window_seconds(4.0) > service.max_window_seconds(8.0)
    assert service.max_window_seconds(4.0) == pytest.approx(14.9, abs=0.1)


def test_the_window_and_frame_rate_reach_the_provider_unchanged() -> None:
    stub = StubGemini(report(rows()))
    service = MotionAnalysisService(stub)

    asyncio.run(
        service.analyze(
            project(),
            record(),
            request(
                frames_per_second=4.0,
                window_start_seconds=60.0,
                window_seconds=12.0,
            ),
        )
    )

    assert stub.calls[0]["frames_per_second"] == 4.0
    assert stub.calls[0]["window_start_seconds"] == 60.0
    assert stub.calls[0]["window_end_seconds"] == 72.0
    assert stub.calls[0]["video_url"] == "https://youtu.be/-fD2TSL2s7I"


def test_a_mirrored_analysis_is_recorded_but_never_called_evidence() -> None:
    service = MotionAnalysisService(StubGemini(report(rows())))

    analysis = asyncio.run(service.analyze(project(), record(), request()))

    assert analysis.sample_count == 24
    assert analysis.subject_kind is MotionSubjectKind.HUMAN_BODY
    assert analysis.joint_names == ["hip"]
    assert analysis.physically_measured is False
    assert analysis.measurement_method == "vision_model_estimate"
    assert analysis.audit.verdict is not MotionEvidenceVerdict.USABLE
    assert analysis.retarget.retarget_supported is False
    assert analysis.retarget.approved_for_execution is False
    assert any(
        "plausibility audit" in item for item in analysis.retarget.missing_evidence
    )


def test_compact_rows_are_expanded_into_sides_and_joints() -> None:
    stub = StubGemini(
        report(
            [
                ProviderJointSample(t=1.0, j="left.knee", a=5.0, c=0.4, v="clear"),
                ProviderJointSample(t=1.0, j="pelvis", a=1.0, c=0.9, v="occluded"),
                ProviderJointSample(t=1.5, j="right.ankle", a=-3.0, c=2.0, v="odd"),
            ]
        )
    )
    service = MotionAnalysisService(stub)

    analysis = asyncio.run(service.analyze(project(), record(), request()))
    by_joint = {item.joint_name: item for item in analysis.samples}

    assert by_joint["knee"].side == "left"
    assert by_joint["pelvis"].side == "center"
    assert by_joint["ankle"].side == "right"
    assert by_joint["ankle"].confidence == 1.0
    assert by_joint["ankle"].visibility.value == "partial"
    assert any("clamped" in item for item in analysis.uncertainties)
    assert any("unrecognised" in item for item in analysis.uncertainties)


def test_a_computer_project_gets_no_retarget_claim() -> None:
    service = MotionAnalysisService(StubGemini(report(rows())))

    analysis = asyncio.run(
        service.analyze(project("computer"), record(), request())
    )

    assert analysis.retarget.retarget_supported is False
    assert analysis.retarget.destination_robot_model is None
    assert "nothing to drive" in analysis.retarget.reason


def test_the_newest_analysis_is_returned_and_missing_ones_raise() -> None:
    service = MotionAnalysisService(StubGemini(report(rows())))

    with pytest.raises(MotionAnalysisNotFoundError):
        service.latest_for_extraction("vpr_test00000001")

    first = asyncio.run(service.analyze(project(), record(), request()))
    second = asyncio.run(service.analyze(project(), record(), request()))
    latest = service.latest_for_extraction("vpr_test00000001")

    assert latest.analysis_id in {first.analysis_id, second.analysis_id}
    assert latest.created_at >= first.created_at


def test_reported_density_describes_what_arrived_not_what_was_asked() -> None:
    stub = StubGemini(
        report(
            [
                ProviderJointSample(t=0.0, j="left.hip", a=1.0, c=0.5, v="clear"),
                ProviderJointSample(t=2.0, j="left.hip", a=9.0, c=0.5, v="clear"),
            ]
        )
    )
    service = MotionAnalysisService(stub)

    analysis = asyncio.run(
        service.analyze(
            project(),
            record(),
            request(frames_per_second=4.0, window_seconds=12.0),
        )
    )

    assert analysis.requested_fps == 4.0
    assert analysis.observed_span_seconds == 2.0
    assert analysis.samples_per_second == 1.0
    assert analysis.clear_sample_count == 2
