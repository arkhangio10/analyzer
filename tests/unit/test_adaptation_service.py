"""Tests for destination adaptation and its refusal to invent evidence."""

from datetime import datetime, timezone

import pytest

from app.models.adaptation import AdaptationActionKind, AdaptationReadiness
from app.models.motion_analysis import (
    JointVisibility,
    MotionAuditCode,
    MotionAuditFinding,
    MotionAnalysisRecord,
    MotionEvidenceAudit,
    MotionEvidenceVerdict,
    MotionRetargetVerdict,
    MotionSubjectKind,
    ObservedJointAngle,
)
from app.models.procedure import Procedure, ProcedureStep
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
from app.services.adaptation_service import (
    AdaptationNotApprovedError,
    DestinationAdaptationService,
)


def procedure(actions: list[str]) -> Procedure:
    return Procedure(
        task="Walk",
        objective="Demonstrate walking mechanics.",
        steps=[
            ProcedureStep(step=index + 1, action=action, source_timestamps=["01:07"])
            for index, action in enumerate(actions)
        ],
    )


def project(destination: str) -> ProjectDraft:
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
    actions: list[str],
    status: ProjectVideoProcedureStatus = ProjectVideoProcedureStatus.APPROVED,
) -> ProjectVideoProcedureRecord:
    return ProjectVideoProcedureRecord(
        extraction_id="vpr_test00000001",
        project_id="prj_test00000001",
        procedure_version=1,
        source_url="https://youtu.be/-fD2TSL2s7I",
        status=status,
        procedure=procedure(actions) if actions else None,
        created_at=datetime.now(timezone.utc),
    )


def test_an_unapproved_procedure_cannot_be_adapted() -> None:
    service = DestinationAdaptationService()

    for status in [
        ProjectVideoProcedureStatus.AWAITING_REVIEW,
        ProjectVideoProcedureStatus.REJECTED,
        ProjectVideoProcedureStatus.EXTRACTION_FAILED,
    ]:
        with pytest.raises(AdaptationNotApprovedError):
            service.adapt(project("robot"), record(["Push off with the hips."], status))


def test_prose_movement_is_never_turned_into_a_trajectory() -> None:
    plan = DestinationAdaptationService().adapt(
        project("robot"),
        record(["Push off with the hips.", "Swing the trailing leg forward."]),
    )

    assert plan.actionable_step_count == 0
    assert plan.blocked_step_count == 2
    assert all(
        step.readiness is AdaptationReadiness.NOT_REPRESENTABLE
        for step in plan.steps
    )
    assert all(step.proposed_action_kind is None for step in plan.steps)
    assert any("Joint-space trajectory" in item for item in plan.missing_evidence)
    assert any("simulator" in item for item in plan.missing_evidence)
    assert plan.requires_human_completion is True
    assert plan.approved_for_execution is False
    assert plan.cloud_calls_made == 0


def test_numeric_joint_evidence_is_recognised_without_being_trusted() -> None:
    plan = DestinationAdaptationService().adapt(
        project("robot"),
        record(["Rotate the hip to 35 degrees over 1.5 seconds."]),
    )

    step = plan.steps[0]
    assert step.readiness is AdaptationReadiness.NEEDS_HUMAN_DETAIL
    assert step.proposed_action_kind is AdaptationActionKind.MOTION_SEGMENT
    assert not any(item.startswith("Joint-space") for item in step.missing_evidence)
    assert any("ARP-1" in item for item in step.missing_evidence)
    assert plan.actionable_step_count == 0


def test_a_computer_step_naming_a_public_url_becomes_a_navigation() -> None:
    plan = DestinationAdaptationService().adapt(
        project("computer"),
        record(["Open https://example.com and read the summary."]),
    )

    step = plan.steps[0]
    assert step.readiness is AdaptationReadiness.ACTIONABLE
    assert step.proposed_action_kind is AdaptationActionKind.NAVIGATE
    assert step.proposed_target == "https://example.com"
    assert plan.actionable_step_count == 1
    assert plan.requires_human_completion is False


def test_a_vague_computer_step_names_what_is_missing() -> None:
    plan = DestinationAdaptationService().adapt(
        project("computer"),
        record(["Fill in the customer details."]),
    )

    step = plan.steps[0]
    assert step.readiness is AdaptationReadiness.NEEDS_HUMAN_DETAIL
    assert any("http(s) URL" in item for item in step.missing_evidence)
    assert any("CSS selector" in item for item in step.missing_evidence)


def test_spanish_adaptation_localizes_missing_evidence_and_block_reason() -> None:
    plan = DestinationAdaptationService().adapt(
        project("robot"),
        record(["Empuja el cuerpo hacia adelante."]),
        language="es",
    )

    assert any("Trayectoria articular" in item for item in plan.missing_evidence)
    assert any("simulador" in item for item in plan.missing_evidence)
    assert "no código para el robot" in (plan.execution_blocked_reason or "")


def test_execution_stays_blocked_for_every_destination() -> None:
    service = DestinationAdaptationService()

    robot = service.adapt(project("robot"), record(["Push off with the hips."]))
    computer = service.adapt(
        project("computer"),
        record(["Open https://example.com."]),
    )

    assert "not robot code" in robot.execution_blocked_reason
    assert "approval" in computer.execution_blocked_reason
    assert robot.approved_for_execution is False
    assert computer.approved_for_execution is False


def analysis(
    *,
    usable: bool,
    retarget_supported: bool = False,
    extraction_id: str = "vpr_test00000001",
) -> MotionAnalysisRecord:
    """Build a retained analysis covering 60s to 72s of the source."""
    samples = [
        ObservedJointAngle(
            timestamp_seconds=round(60 + index * 0.25, 3),
            joint_name="knee",
            side=side,
            angle_degrees=float(index),
            confidence=0.6,
            visibility=JointVisibility.CLEAR,
        )
        for index in range(48)
        for side in ("left", "right")
    ]
    audit = MotionEvidenceAudit(
        verdict=(
            MotionEvidenceVerdict.USABLE
            if usable
            else MotionEvidenceVerdict.NOT_EVIDENCE
        ),
        findings=(
            []
            if usable
            else [
                MotionAuditFinding(
                    code=MotionAuditCode.MIRRORED_SIDES,
                    message="Left and right carry the same angle.",
                    values={"identical": "48", "paired": "48"},
                )
            ]
        ),
        mirrored_frame_ratio=0.0 if usable else 1.0,
        distinct_confidence_values=4 if usable else 1,
        distinct_visibility_values=3 if usable else 1,
        acyclic_joints=[],
        checked_joint_count=2,
    )
    return MotionAnalysisRecord(
        analysis_id="mot_test00000001",
        project_id="prj_test00000001",
        extraction_id=extraction_id,
        source_url="https://youtu.be/-fD2TSL2s7I",
        requested_fps=4.0,
        window_start_seconds=60.0,
        window_end_seconds=72.0,
        subject_kind=MotionSubjectKind.HUMAN_BODY,
        kinematic_chain="bipedal_lower_limb",
        joint_names=["knee"],
        samples=samples,
        sample_count=len(samples),
        distinct_joint_count=2,
        observed_span_seconds=11.75,
        samples_per_second=8.17,
        mean_confidence=0.6,
        clear_sample_count=len(samples),
        audit=audit,
        retarget=MotionRetargetVerdict(
            retarget_supported=retarget_supported,
            destination_robot_model="APRENDIZ SimArm-6",
            observed_chain="bipedal_lower_limb",
            reason="Test verdict.",
            missing_evidence=[] if retarget_supported else ["A joint map."],
        ),
        provider="vertex_ai",
        requested_model="gemini-2.5-flash-lite",
        elapsed_seconds=44.3,
        created_at=datetime.now(timezone.utc),
    )


def timed_record(timestamps: list[list[str]]) -> ProjectVideoProcedureRecord:
    steps = [
        ProcedureStep(
            step=index + 1,
            action=f"Observed movement {index + 1}.",
            source_timestamps=stamps,
        )
        for index, stamps in enumerate(timestamps)
    ]
    return ProjectVideoProcedureRecord(
        extraction_id="vpr_test00000001",
        project_id="prj_test00000001",
        procedure_version=1,
        source_url="https://youtu.be/-fD2TSL2s7I",
        status=ProjectVideoProcedureStatus.APPROVED,
        procedure=Procedure(
            task="Walk",
            objective="Demonstrate walking mechanics.",
            steps=steps,
        ),
        created_at=datetime.now(timezone.utc),
    )


def test_samples_that_failed_the_audit_never_make_a_step_actionable() -> None:
    plan = DestinationAdaptationService().adapt(
        project("robot"),
        timed_record([["01:05"], ["01:08"]]),
        analysis(usable=False, retarget_supported=True),
    )

    assert plan.actionable_step_count == 0
    assert plan.motion_evidence_step_count == 0
    assert all(
        step.readiness is AdaptationReadiness.NOT_REPRESENTABLE
        for step in plan.steps
    )
    assert any("same angle" in item for item in plan.missing_evidence)


def test_a_step_inside_the_sampled_window_carries_its_samples() -> None:
    plan = DestinationAdaptationService().adapt(
        project("robot"),
        timed_record([["01:05"]]),
        analysis(usable=True, retarget_supported=True),
    )

    step = plan.steps[0]
    assert step.readiness is AdaptationReadiness.ACTIONABLE
    assert step.proposed_action_kind is AdaptationActionKind.MOTION_SEGMENT
    assert "observed joints" in (step.proposed_target or "")
    assert plan.motion_analysis_id == "mot_test00000001"
    assert plan.motion_evidence_step_count == 1
    assert plan.approved_for_execution is False


def test_a_step_outside_the_sampled_window_says_what_was_sampled() -> None:
    plan = DestinationAdaptationService().adapt(
        project("robot"),
        timed_record([["02:30"]]),
        analysis(usable=True, retarget_supported=True),
    )

    step = plan.steps[0]
    assert step.readiness is AdaptationReadiness.NOT_REPRESENTABLE
    assert any("60s to 72s" in item for item in step.missing_evidence)
    assert any("4 fps" in item for item in step.missing_evidence)
    assert plan.actionable_step_count == 0


def test_usable_samples_without_a_retarget_still_need_a_person() -> None:
    plan = DestinationAdaptationService().adapt(
        project("robot"),
        timed_record([["01:05"]]),
        analysis(usable=True, retarget_supported=False),
    )

    step = plan.steps[0]
    assert step.readiness is AdaptationReadiness.NEEDS_HUMAN_DETAIL
    assert plan.actionable_step_count == 0
    assert plan.requires_human_completion is True

    spanish_motion = analysis(usable=True, retarget_supported=False)
    spanish_motion = spanish_motion.model_copy(
        update={
            "retarget": spanish_motion.retarget.model_copy(
                update={
                    "missing_evidence": [
                        "Un simulador seleccionado, más validación de colisiones y dinámica.",
                    ]
                }
            )
        }
    )
    relocalized = DestinationAdaptationService().adapt(
        project("robot"),
        timed_record([["01:05"]]),
        spanish_motion,
        language="en",
    )
    assert any("selected simulator" in item for item in relocalized.missing_evidence)
    assert not any(
        "simulador seleccionado" in item
        for item in relocalized.missing_evidence
    )


def test_an_analysis_of_a_different_extraction_is_ignored() -> None:
    plan = DestinationAdaptationService().adapt(
        project("robot"),
        timed_record([["01:05"]]),
        analysis(usable=True, retarget_supported=True, extraction_id="vpr_other"),
    )

    assert plan.motion_analysis_id is None
    assert plan.steps[0].readiness is AdaptationReadiness.NOT_REPRESENTABLE
