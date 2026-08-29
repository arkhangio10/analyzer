"""APRENDIZ Robot Profile v1 contracts."""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field

from app.models.robot_motion import JointLimit


class RobotDescriptionFormat(StrEnum):
    """External description formats mapped into ARP-1."""

    URDF = "urdf"


class RobotJointProfile(BaseModel):
    """One kinematic relationship imported from the source description."""

    name: str
    joint_type: str
    parent_link: str
    child_link: str
    axis: tuple[float, float, float]
    lower_limit: float | None = None
    upper_limit: float | None = None
    velocity_limit: float | None = None
    effort_limit: float | None = None
    position_unit: Literal["radian", "meter", "not_applicable"]
    velocity_unit: Literal[
        "radian_per_second",
        "meter_per_second",
        "not_applicable",
    ]


class RobotLinkProfile(BaseModel):
    """One rigid link and the simulation evidence available for it."""

    name: str
    mass_kg: float | None = Field(default=None, gt=0)
    has_visual_geometry: bool
    has_collision_geometry: bool


class SimulatorRecommendation(BaseModel):
    """Non-binding simulator choice derived from the robot class."""

    primary: Literal["gazebo", "mujoco"]
    alternatives: list[str]
    reason: str
    availability: Literal["not_checked"] = "not_checked"


class ARP1RobotProfile(BaseModel):
    """Internal normalized robot contract; ARP-1 is APRENDIZ-specific."""

    standard: Literal["ARP-1"] = "ARP-1"
    version: Literal["1.0"] = "1.0"
    robot_name: str
    robot_model: str
    robot_class: str
    source_format: RobotDescriptionFormat
    source_name: str
    links: list[RobotLinkProfile]
    joints: list[RobotJointProfile]
    actuated_joint_count: int = Field(ge=0)
    root_links: list[str]
    simulator: SimulatorRecommendation
    simulation_only: Literal[True] = True
    hardware_execution_approved: Literal[False] = False
    valid_for_kinematic_simulation: bool
    validation_errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class URDFImportRequest(BaseModel):
    """Bounded URDF document supplied for ARP-1 normalization."""

    robot_model: str = Field(min_length=1, max_length=160)
    robot_class: str = Field(default="unknown", min_length=1, max_length=80)
    source_name: str = Field(default="robot.urdf", min_length=1, max_length=200)
    urdf_xml: str = Field(min_length=20, max_length=524_288)


class ARP1MotionContract(BaseModel):
    """Compatibility layer for the current degree-based motion trainer."""

    standard: Literal["ARP-1"] = "ARP-1"
    robot_model: str
    joint_names: list[str]
    joint_limits: list[JointLimit]
    ready_for_motion_training: bool
    blockers: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    simulation_only: Literal[True] = True
