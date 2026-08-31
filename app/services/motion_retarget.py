"""Deterministic verdict on whether observed movement could drive a robot.

Watching a person walk produces angles for a bipedal lower limb. Sending those
angles to a six-axis arm is not a conversion, it is a category error. This
module refuses to paper over that: it checks the destination's imported profile
and the human-authored joint map, and when either is missing it says which one
and stops. It never proposes a mapping of its own.
"""

from __future__ import annotations

from app.models.motion_analysis import (
    MotionEvidenceAudit,
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
                "This project's destination is a computer, so observed body "
                "motion has nothing to drive. The analysis is retained as "
                "evidence about the source only."
            ),
            missing_evidence=[],
        )

    robot_model = contract.robot_model or "an unnamed robot"
    observed = sorted({observed_joint_key(sample) for sample in samples})
    missing: list[str] = []

    if not observed:
        missing.append(_NO_SAMPLES)
    if not audit.is_usable:
        missing.append(_FAILED_AUDIT)
    if profile is None:
        missing.append(_NO_PROFILE)
    unmapped = [key for key in observed if not (joint_map or {}).get(key)]
    if unmapped:
        missing.append(_NO_MAP)
    missing.append(_NO_SIMULATOR)

    if not audit.is_usable:
        return MotionRetargetVerdict(
            retarget_supported=False,
            destination_robot_model=contract.robot_model,
            observed_chain=chain,
            reason=(
                "These samples did not survive the plausibility audit, so "
                "there is nothing here to retarget onto "
                f"{robot_model}. "
                + (audit.findings[0].message if audit.findings else "")
            )[:600],
            missing_evidence=missing[:12],
        )

    if missing == [_NO_SIMULATOR]:
        return MotionRetargetVerdict(
            retarget_supported=False,
            destination_robot_model=contract.robot_model,
            observed_chain=chain,
            reason=(
                f"Every observed joint has an authored mapping onto {robot_model}, "
                "so a trajectory could be built. Motion still stays blocked "
                "until a simulator validates it; nothing here is an approval "
                "to move a robot."
            ),
            missing_evidence=missing,
        )

    if subject_kind is MotionSubjectKind.HUMAN_BODY:
        reason = (
            f"The video shows a human {chain}, and {robot_model} is a different "
            "kinematic chain. Its joints have no inherent correspondence to a "
            "hip, knee, or ankle, so these angles are evidence about a person, "
            "not a trajectory for this robot."
        )
    elif subject_kind is MotionSubjectKind.UNCLEAR:
        reason = (
            "The analysis could not establish what kind of body is moving, so "
            "no correspondence with " + robot_model + " can be claimed."
        )
    else:
        reason = (
            f"The observed {chain} is not yet mapped onto {robot_model}. "
            "A correspondence has to be authored and reviewed by a person "
            "before any angle can be treated as a joint command."
        )

    return MotionRetargetVerdict(
        retarget_supported=False,
        destination_robot_model=contract.robot_model,
        observed_chain=chain,
        reason=reason,
        missing_evidence=missing[:12],
    )
