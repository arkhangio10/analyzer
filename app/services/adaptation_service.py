"""Deterministic adaptation of a reviewed procedure to a destination.

This service answers one question honestly: how much of an approved procedure
could a destination actually run, and what is missing for the rest? It makes no
provider call, executes nothing, and never fabricates the evidence a step lacks.

Three rules keep it truthful:

- A procedure that a person has not approved cannot be adapted at all.
- A step is only `actionable` when the source itself supplies what the adapter
  needs. Prose describing a movement is not a trajectory, and prose describing
  a website is not an approved host, so those come back blocked with the exact
  missing evidence named.
- When a motion analysis exists, a robot step is judged against the samples
  that actually cover its timestamps, not against the words it is written in.
  A step outside the analysed window is reported as unsampled, with the window
  that was analysed, rather than being credited with evidence it never had.
"""

from __future__ import annotations

import re
from typing import Literal
from uuid import uuid4

from app.models.adaptation import (
    AdaptationActionKind,
    AdaptationReadiness,
    AdaptedStep,
    DestinationAdaptationPlan,
)
from app.models.motion_analysis import (
    MotionAnalysisRecord,
    MotionAuditCode,
    MotionAuditFinding,
    ObservedJointAngle,
)
from app.models.procedure import Procedure, ProcedureStep
from app.models.project import ExecutionDestination, ProjectDraft
from app.models.project_video_procedure import (
    ProjectVideoProcedureRecord,
    ProjectVideoProcedureStatus,
)


class AdaptationNotApprovedError(ValueError):
    """Raised when a procedure has not passed human review."""


_PUBLIC_URL = re.compile(r"https?://[^\s\"'<>()]+", re.IGNORECASE)
_JOINT_EVIDENCE = re.compile(
    r"(-?\d+(?:\.\d+)?)\s*(?:°|deg|degrees|grados)",
    re.IGNORECASE,
)
_TIMING_EVIDENCE = re.compile(
    r"(-?\d+(?:\.\d+)?)\s*(?:s|sec|secs|seconds|segundos)\b",
    re.IGNORECASE,
)
_CLOCK_TIMESTAMP = re.compile(r"(?:(\d{1,2}):)?(\d{1,3}):(\d{2})(?:\.(\d{1,3}))?")

_JOINT_SPACE = "Joint-space trajectory: target angles per joint for each step."
_TIMING = "Timing: a timestamp or duration for every waypoint."
_PROFILE = "A normalized ARP-1 robot profile imported for this exact robot model."
_SIMULATOR = "A selected simulator, plus collision and dynamics validation."

_ROBOT_MISSING = (_JOINT_SPACE, _TIMING, _PROFILE, _SIMULATOR)
_COMPUTER_MISSING_TARGET = (
    "An exact public host to approve, written as an http(s) URL."
)
_COMPUTER_MISSING_SELECTOR = (
    "The CSS selector of the field or control the step refers to."
)

_ROBOT_BLOCKED_REASON = (
    "Reviewed video steps are a description of observed movement, not robot "
    "code. Motion execution stays blocked until a joint-space trajectory, an "
    "ARP-1 profile, and a validated simulator exist for this robot."
)
_COMPUTER_BLOCKED_REASON = (
    "Every action still needs an explicit human approval of the exact steps "
    "and the exact public host before the container browser may run it."
)

_SAMPLE_TOLERANCE_SECONDS = 1.0

Language = Literal["es", "en"]

_ES = {
    _JOINT_SPACE: "Trayectoria articular: ángulos objetivo por articulación para cada paso.",
    _TIMING: "Temporización: una marca de tiempo o duración para cada punto de paso.",
    _PROFILE: "Un perfil ARP-1 normalizado para este modelo exacto de robot.",
    _SIMULATOR: "Un simulador seleccionado, más validación de colisiones y dinámica.",
    _COMPUTER_MISSING_TARGET: "Un host público exacto para aprobar, escrito como URL http(s).",
    _COMPUTER_MISSING_SELECTOR: "El selector CSS del campo o control al que se refiere el paso.",
}

_ES_TO_EN = {
    "Un perfil ARP-1 normalizado para este modelo exacto de robot.": _PROFILE,
    "Un mapa escrito por una persona entre articulaciones observadas y articulaciones ARP-1, incluyendo signo y convención cero.": "A human-authored joint map from each observed joint to a named ARP-1 joint.",
    "Muestras de ángulos articulares con marca de tiempo; el análisis no devolvió ninguna utilizable.": "Timestamped joint-angle samples; this analysis returned none that could be used.",
    "Un simulador seleccionado, más validación de colisiones y dinámica.": _SIMULATOR,
    "Muestras articulares que superen la auditoría de plausibilidad.": "Joint samples that survive the plausibility audit.",
}


def _text(value: str, language: Language) -> str:
    """Translate deterministic evidence vocabulary without changing evidence."""
    if language == "en":
        return _ES_TO_EN.get(value, value)
    direct = _ES.get(value)
    if direct:
        return direct
    if "normalized ARP-1 profile" in value:
        return _ES[_PROFILE]
    if "human-authored joint map" in value:
        return (
            "Un mapa de articulaciones escrito por una persona desde cada "
            "articulación observada hasta una articulación ARP-1 identificada."
        )
    if "selected simulator" in value:
        return _ES[_SIMULATOR]
    if "Timestamped joint-angle samples" in value:
        return "Muestras de ángulos articulares con marca de tiempo."
    if "plausibility audit" in value:
        return "Muestras articulares que superen la auditoría de plausibilidad."
    return value


def _audit_text(finding: MotionAuditFinding, language: Language) -> str:
    if language == "en":
        return finding.message
    messages = {
        MotionAuditCode.NO_SAMPLES: "El análisis no devolvió muestras articulares utilizables.",
        MotionAuditCode.MIRRORED_SIDES: "Los lados izquierdo y derecho repiten los mismos ángulos.",
        MotionAuditCode.UNIFORM_CONFIDENCE: "Todas las muestras usan exactamente la misma confianza.",
        MotionAuditCode.UNIFORM_VISIBILITY: "Todas las muestras usan exactamente la misma visibilidad.",
        MotionAuditCode.ACYCLIC_ALL: "Ninguna articulación muestra los ciclos esperados del movimiento.",
        MotionAuditCode.ACYCLIC_SOME: "Algunas articulaciones no muestran ciclos plausibles.",
    }
    return messages[finding.code]


def parse_clock_timestamp(value: str) -> float | None:
    """Convert an MM:SS or HH:MM:SS source timestamp into seconds."""
    match = _CLOCK_TIMESTAMP.search(value or "")
    if not match:
        return None
    hours, minutes, seconds, millis = match.groups()
    total = int(minutes) * 60 + int(seconds)
    if hours:
        total += int(hours) * 3600
    if millis:
        total += int(millis.ljust(3, "0")) / 1000
    return float(total)


def _step_window(step: ProcedureStep) -> tuple[float, float] | None:
    """Return the seconds a step covers, or None when it names no time."""
    seconds = [
        parsed
        for parsed in (parse_clock_timestamp(item) for item in step.source_timestamps)
        if parsed is not None
    ]
    if not seconds:
        return None
    start, end = min(seconds), max(seconds)
    if start == end:
        return start - _SAMPLE_TOLERANCE_SECONDS, end + _SAMPLE_TOLERANCE_SECONDS
    return start, end


def _samples_in_window(
    samples: list[ObservedJointAngle],
    window: tuple[float, float],
) -> list[ObservedJointAngle]:
    start, end = window
    return [
        sample for sample in samples if start <= sample.timestamp_seconds <= end
    ]


def _adapt_robot_step(
    order: int,
    step: ProcedureStep,
    language: Language,
) -> AdaptedStep:
    """Judge one robot step by the words it is written in, with no analysis."""
    action = step.action
    has_angles = bool(_JOINT_EVIDENCE.search(action))
    has_timing = bool(_TIMING_EVIDENCE.search(action))
    missing = [
        item
        for item in _ROBOT_MISSING
        if not (
            (has_angles and item == _JOINT_SPACE)
            or (has_timing and item == _TIMING)
        )
    ]
    readiness = (
        AdaptationReadiness.NEEDS_HUMAN_DETAIL
        if has_angles or has_timing
        else AdaptationReadiness.NOT_REPRESENTABLE
    )
    return AdaptedStep(
        order=order,
        source_step_order=step.step,
        source_action=action,
        source_timestamps=list(step.source_timestamps),
        readiness=readiness,
        proposed_action_kind=(
            AdaptationActionKind.MOTION_SEGMENT if has_angles else None
        ),
        missing_evidence=[_text(item, language) for item in missing],
    )


def _adapt_robot_step_with_motion(
    order: int,
    step: ProcedureStep,
    analysis: MotionAnalysisRecord,
    language: Language,
) -> AdaptedStep:
    """Judge one robot step against the samples that actually cover it."""
    window = _step_window(step)
    covered = _samples_in_window(analysis.samples, window) if window else []
    missing: list[str] = []

    if not analysis.audit.is_usable:
        # Dense samples that failed the plausibility audit are worse than no
        # samples: they look like evidence. They never advance a step.
        covered = []
        missing.extend(
            _audit_text(item, language) for item in analysis.audit.findings[:2]
        )

    if window is None:
        missing.append(
            "This step carries no source timestamp, so no sample can be matched to it."
            if language == "en"
            else "Este paso no tiene marca de tiempo de origen; no se puede asociar ninguna muestra."
        )
        missing.append(_text(_JOINT_SPACE, language))
        missing.append(_text(_TIMING, language))
    elif not covered:
        if analysis.audit.is_usable:
            missing.append(
                (
                    "No joint samples cover this step. The analysis sampled "
                    f"{analysis.window_start_seconds:g}s to "
                    f"{analysis.window_end_seconds:g}s at "
                    f"{analysis.requested_fps:g} fps; this step sits at "
                    f"{window[0]:g}s to {window[1]:g}s."
                )
                if language == "en"
                else (
                    "Ninguna muestra articular cubre este paso. El análisis muestreó "
                    f"de {analysis.window_start_seconds:g}s a "
                    f"{analysis.window_end_seconds:g}s a "
                    f"{analysis.requested_fps:g} fps; el paso está entre "
                    f"{window[0]:g}s y {window[1]:g}s."
                )
            )
        missing.append(_text(_JOINT_SPACE, language))
    if not analysis.retarget.retarget_supported:
        for item in analysis.retarget.missing_evidence:
            translated = _text(item, language)
            if translated not in missing:
                missing.append(translated)
    profile_text = _text(_PROFILE, language)
    simulator_text = _text(_SIMULATOR, language)
    if profile_text not in missing and not analysis.retarget.retarget_supported:
        missing.append(profile_text)
    if simulator_text not in missing:
        missing.append(simulator_text)

    if covered and analysis.retarget.retarget_supported:
        readiness = AdaptationReadiness.ACTIONABLE
    elif covered:
        readiness = AdaptationReadiness.NEEDS_HUMAN_DETAIL
    else:
        readiness = AdaptationReadiness.NOT_REPRESENTABLE

    joints = sorted({f"{item.side}.{item.joint_name}" for item in covered})
    return AdaptedStep(
        order=order,
        source_step_order=step.step,
        source_action=step.action,
        source_timestamps=list(step.source_timestamps),
        readiness=readiness,
        proposed_action_kind=(
            AdaptationActionKind.MOTION_SEGMENT if covered else None
        ),
        proposed_target=(
            (
                f"{len(covered)} samples across {len(joints)} observed joints"
                if language == "en"
                else f"{len(covered)} muestras en {len(joints)} articulaciones observadas"
            )
            if covered
            else None
        ),
        missing_evidence=missing[:12],
    )


def _adapt_computer_step(
    order: int,
    step: ProcedureStep,
    language: Language,
) -> AdaptedStep:
    action = step.action
    url_match = _PUBLIC_URL.search(action)
    if url_match:
        return AdaptedStep(
            order=order,
            source_step_order=step.step,
            source_action=action,
            source_timestamps=list(step.source_timestamps),
            readiness=AdaptationReadiness.ACTIONABLE,
            proposed_action_kind=AdaptationActionKind.NAVIGATE,
            proposed_target=url_match.group(0),
            missing_evidence=[],
        )
    return AdaptedStep(
        order=order,
        source_step_order=step.step,
        source_action=action,
        source_timestamps=list(step.source_timestamps),
        readiness=AdaptationReadiness.NEEDS_HUMAN_DETAIL,
        proposed_action_kind=None,
        missing_evidence=[
            _text(_COMPUTER_MISSING_TARGET, language),
            _text(_COMPUTER_MISSING_SELECTOR, language),
        ],
    )


class DestinationAdaptationService:
    """Turn one approved procedure into an inspectable destination proposal."""

    def adapt(
        self,
        project: ProjectDraft,
        record: ProjectVideoProcedureRecord,
        motion_analysis: MotionAnalysisRecord | None = None,
        language: Language = "en",
    ) -> DestinationAdaptationPlan:
        """Build a plan, or refuse when human review has not approved it."""
        if record.status is not ProjectVideoProcedureStatus.APPROVED:
            raise AdaptationNotApprovedError(
                "Only a procedure approved by a person can be adapted."
            )
        procedure = record.procedure
        if procedure is None:
            raise AdaptationNotApprovedError(
                "The approved record carries no structured procedure."
            )

        destination = project.destination_contract.destination
        analysis = (
            motion_analysis
            if motion_analysis is not None
            and motion_analysis.extraction_id == record.extraction_id
            else None
        )
        steps = self._adapt_steps(destination, procedure, analysis, language)
        actionable = sum(
            1 for step in steps if step.readiness is AdaptationReadiness.ACTIONABLE
        )
        missing: list[str] = []
        for step in steps:
            for item in step.missing_evidence:
                if item not in missing:
                    missing.append(item)

        with_motion = sum(
            1
            for step in steps
            if step.proposed_action_kind is AdaptationActionKind.MOTION_SEGMENT
        )
        return DestinationAdaptationPlan(
            plan_id=f"adp_{uuid4().hex[:12]}",
            project_id=project.project_id,
            extraction_id=record.extraction_id,
            procedure_version=record.procedure_version or 1,
            destination=destination,
            steps=steps,
            actionable_step_count=actionable,
            blocked_step_count=len(steps) - actionable,
            missing_evidence=missing[:40],
            requires_human_completion=actionable < len(steps),
            execution_blocked_reason=(
                (
                    _ROBOT_BLOCKED_REASON
                    if language == "en"
                    else "Los pasos revisados describen movimiento observado, no código para el robot. La ejecución queda bloqueada hasta disponer de trayectoria articular, perfil ARP-1 y simulador validado."
                )
                if destination is ExecutionDestination.ROBOT
                else (
                    _COMPUTER_BLOCKED_REASON
                    if language == "en"
                    else "Cada acción requiere aprobación humana explícita de los pasos exactos y del host público exacto antes de ejecutarse en el navegador aislado."
                )
            ),
            motion_analysis_id=analysis.analysis_id if analysis else None,
            motion_evidence_step_count=with_motion if analysis else 0,
        )

    @staticmethod
    def _adapt_steps(
        destination: ExecutionDestination,
        procedure: Procedure,
        analysis: MotionAnalysisRecord | None,
        language: Language,
    ) -> list[AdaptedStep]:
        if destination is ExecutionDestination.ROBOT:
            if analysis is not None:
                return [
                    _adapt_robot_step_with_motion(index + 1, step, analysis, language)
                    for index, step in enumerate(procedure.steps)
                ]
            return [
                _adapt_robot_step(index + 1, step, language)
                for index, step in enumerate(procedure.steps)
            ]
        return [
            _adapt_computer_step(index + 1, step, language)
            for index, step in enumerate(procedure.steps)
        ]
