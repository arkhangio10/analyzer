"""Deterministic verdict on whether observed movement could drive a robot.

Watching a person walk produces angles for a bipedal lower limb. Sending those
angles to a six-axis arm is not a conversion, it is a category error. This
module refuses to paper over that: it checks the destination's imported profile
and the human-authored joint map, and when either is missing it says which one
and stops. It never proposes a mapping of its own.
"""

from __future__ import annotations

from typing import Literal

from app.models.motion_analysis import (
    MotionEvidenceAudit,
    MotionAuditCode,
    MotionRetargetVerdict,
    MotionSubjectKind,
    ObservedJointAngle,
)
from app.models.project import ExecutionDestination, ProjectDraft
from app.models.robot_profile import ARP1RobotProfile


_NO_PROFILE = (
    "A normalized ARP-1 profile imported for this exact robot model, so the "
    "destination's joints, axes, and limits are known."
)
_NO_MAP = (
    "A human-authored joint map from each observed joint to a named ARP-1 "
    "joint, including sign and zero convention."
)
_NO_SAMPLES = (
    "Timestamped joint-angle samples; this analysis returned none that could "
    "be used."
)
_NO_SIMULATOR = "A selected simulator, plus collision and dynamics validation."
_FAILED_AUDIT = (
    "Joint samples that survive the plausibility audit; this analysis returned "
    "values that arithmetic shows were not measured from the video."
)

Language = Literal["es", "en"]

_MISSING_ES = {
    _NO_PROFILE: "Un perfil ARP-1 normalizado para este modelo exacto de robot.",
    _NO_MAP: "Un mapa escrito por una persona entre articulaciones observadas y articulaciones ARP-1, incluyendo signo y convención cero.",
    _NO_SAMPLES: "Muestras de ángulos articulares con marca de tiempo; el análisis no devolvió ninguna utilizable.",
    _NO_SIMULATOR: "Un simulador seleccionado, más validación de colisiones y dinámica.",
    _FAILED_AUDIT: "Muestras articulares que superen la auditoría de plausibilidad.",
}


def _missing_text(value: str, language: Language) -> str:
    return _MISSING_ES[value] if language == "es" else value


def _first_audit_finding(audit: MotionEvidenceAudit, language: Language) -> str:
    if not audit.findings:
        return ""
    finding = audit.findings[0]
    if language == "en":
        return finding.message
    messages = {
        MotionAuditCode.NO_SAMPLES: "El análisis no devolvió muestras utilizables.",
        MotionAuditCode.MIRRORED_SIDES: "Los lados repiten los mismos ángulos.",
        MotionAuditCode.UNIFORM_CONFIDENCE: "La confianza es idéntica en todas las muestras.",
        MotionAuditCode.UNIFORM_VISIBILITY: "La visibilidad es idéntica en todas las muestras.",
        MotionAuditCode.ACYCLIC_ALL: "No aparecen los ciclos esperados del movimiento.",
        MotionAuditCode.ACYCLIC_SOME: "Algunas articulaciones no presentan ciclos plausibles.",
    }
    return messages[finding.code]


def observed_joint_key(sample: ObservedJointAngle) -> str:
    """Return the stable identity of one observed joint, such as 'left.knee'."""
    side = sample.side.strip().casefold() or "center"
    return f"{side}.{sample.joint_name.strip().casefold()}"


def build_retarget_verdict(
    *,
    project: ProjectDraft,
    subject_kind: MotionSubjectKind,
    kinematic_chain: str,
    samples: list[ObservedJointAngle],
    audit: MotionEvidenceAudit,
    profile: ARP1RobotProfile | None = None,
    joint_map: dict[str, str] | None = None,
    language: Language = "en",
) -> MotionRetargetVerdict:
    """Decide whether observed joints could be mapped onto the destination."""
    contract = project.destination_contract
    chain = kinematic_chain or "unknown"

    if contract.destination is not ExecutionDestination.ROBOT:
        return MotionRetargetVerdict(
            retarget_supported=False,
            destination_robot_model=None,
            observed_chain=chain,
            reason=(
                (
                    "This project's destination is a computer, so observed body "
                    "motion has nothing to drive. The analysis is retained as "
                    "evidence about the source only."
                )
                if language == "en"
                else (
                    "El destino de este proyecto es una computadora; el movimiento "
                    "corporal observado no controla nada. El análisis se conserva "
                    "únicamente como evidencia de la fuente."
                )
            ),
            missing_evidence=[],
        )

    robot_model = contract.robot_model or "an unnamed robot"
    observed = sorted({observed_joint_key(sample) for sample in samples})
    missing: list[str] = []

    if not observed:
        missing.append(_missing_text(_NO_SAMPLES, language))
    if not audit.is_usable:
        missing.append(_missing_text(_FAILED_AUDIT, language))
    if profile is None:
        missing.append(_missing_text(_NO_PROFILE, language))
    unmapped = [key for key in observed if not (joint_map or {}).get(key)]
    if unmapped:
        missing.append(_missing_text(_NO_MAP, language))
    missing.append(_missing_text(_NO_SIMULATOR, language))

    if not audit.is_usable:
        return MotionRetargetVerdict(
            retarget_supported=False,
            destination_robot_model=contract.robot_model,
            observed_chain=chain,
            reason=(
                (
                    "These samples did not survive the plausibility audit, so "
                    "there is nothing here to retarget onto "
                    f"{robot_model}. "
                )
                if language == "en"
                else (
                    "Estas muestras no superaron la auditoría de plausibilidad; "
                    f"no existe evidencia que pueda adaptarse a {robot_model}. "
                )
            )
            + _first_audit_finding(audit, language),
            missing_evidence=missing[:12],
        )

    if missing == [_missing_text(_NO_SIMULATOR, language)]:
        return MotionRetargetVerdict(
            retarget_supported=False,
            destination_robot_model=contract.robot_model,
            observed_chain=chain,
            reason=(
                (
                    f"Every observed joint has an authored mapping onto {robot_model}, "
                    "so a trajectory could be built. Motion still stays blocked "
                    "until a simulator validates it; nothing here is an approval "
                    "to move a robot."
                )
                if language == "en"
                else (
                    f"Cada articulación observada tiene un mapeo revisado hacia {robot_model}; "
                    "podría construirse una trayectoria. El movimiento permanece bloqueado "
                    "hasta validarlo en un simulador; esto no autoriza mover el robot."
                )
            ),
            missing_evidence=missing,
        )

    if subject_kind is MotionSubjectKind.HUMAN_BODY:
        reason = (
            (
                f"The video shows a human {chain}, and {robot_model} is a different "
                "kinematic chain. Its joints have no inherent correspondence to a "
                "hip, knee, or ankle, so these angles are evidence about a person, "
                "not a trajectory for this robot."
            )
            if language == "en"
            else (
                f"El video muestra una cadena humana {chain}, mientras que {robot_model} "
                "tiene otra cinemática. Sus articulaciones no corresponden de forma "
                "inherente con cadera, rodilla o tobillo; estos ángulos describen a "
                "una persona, no una trayectoria para el robot."
            )
        )
    elif subject_kind is MotionSubjectKind.UNCLEAR:
        reason = (
            (
                "The analysis could not establish what kind of body is moving, so "
                "no correspondence with " + robot_model + " can be claimed."
            )
            if language == "en"
            else (
                "El análisis no pudo establecer qué clase de cuerpo se mueve; no "
                "puede afirmarse una correspondencia con " + robot_model + "."
            )
        )
    else:
        reason = (
            (
                f"The observed {chain} is not yet mapped onto {robot_model}. "
                "A correspondence has to be authored and reviewed by a person "
                "before any angle can be treated as a joint command."
            )
            if language == "en"
            else (
                f"La cadena observada {chain} aún no está mapeada hacia {robot_model}. "
                "Una persona debe definir y revisar la correspondencia antes de tratar "
                "cualquier ángulo como comando articular."
            )
        )

    return MotionRetargetVerdict(
        retarget_supported=False,
        destination_robot_model=contract.robot_model,
        observed_chain=chain,
        reason=reason,
        missing_evidence=missing[:12],
    )
