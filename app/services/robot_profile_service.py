"""Safe URDF-to-ARP-1 normalization."""

from __future__ import annotations

import math
import xml.etree.ElementTree as ET

from app.models.robot_profile import (
    ARP1RobotProfile,
    ARP1MotionContract,
    RobotDescriptionFormat,
    RobotJointProfile,
    RobotLinkProfile,
    SimulatorRecommendation,
    URDFImportRequest,
)
from app.models.robot_motion import JointLimit


class RobotDescriptionError(ValueError):
    """Raised when a robot description cannot be parsed safely."""


class RobotProfileService:
    """Normalize bounded URDF into the internal simulation-first profile."""

    _MOVABLE_JOINTS = {"revolute", "continuous", "prismatic"}

    def import_urdf(self, request: URDFImportRequest) -> ARP1RobotProfile:
        xml = request.urdf_xml.strip()
        upper = xml.upper()
        if "<!DOCTYPE" in upper or "<!ENTITY" in upper:
            raise RobotDescriptionError(
                "URDF document types and entity declarations are not accepted."
            )
        try:
            root = ET.fromstring(xml)
        except ET.ParseError as error:
            raise RobotDescriptionError("URDF XML is malformed.") from error
        if self._local_name(root.tag) != "robot":
            raise RobotDescriptionError("URDF root element must be <robot>.")

        errors: list[str] = []
        warnings: list[str] = []
        links = self._parse_links(root, errors, warnings)
        joints = self._parse_joints(root, errors, warnings)
        link_names = {link.name for link in links}
        child_links: set[str] = set()
        for joint in joints:
            if joint.parent_link not in link_names:
                errors.append(
                    f"Joint {joint.name} references missing parent link {joint.parent_link}."
                )
            if joint.child_link not in link_names:
                errors.append(
                    f"Joint {joint.name} references missing child link {joint.child_link}."
                )
            child_links.add(joint.child_link)
        root_links = sorted(link_names - child_links)
        if len(root_links) != 1:
            errors.append(
                f"URDF must describe one kinematic tree root; found {len(root_links)}."
            )
        if links and all(not link.has_collision_geometry for link in links):
            warnings.append(
                "No collision geometry was found; collision validation is unavailable."
            )
        if links and any(link.mass_kg is None for link in links):
            warnings.append(
                "One or more links lack inertial mass; dynamics validation is unavailable."
            )

        actuated = sum(joint.joint_type in self._MOVABLE_JOINTS for joint in joints)
        recommendation = self._recommend_simulator(request.robot_class)
        return ARP1RobotProfile(
            robot_name=root.attrib.get("name", request.robot_model),
            robot_model=request.robot_model,
            robot_class=request.robot_class,
            source_format=RobotDescriptionFormat.URDF,
            source_name=request.source_name,
            links=links,
            joints=joints,
            actuated_joint_count=actuated,
            root_links=root_links,
            simulator=recommendation,
            valid_for_kinematic_simulation=bool(links) and not errors,
            validation_errors=list(dict.fromkeys(errors)),
            warnings=list(dict.fromkeys(warnings)),
        )

    def to_motion_contract(self, profile: ARP1RobotProfile) -> ARP1MotionContract:
        """Map compatible revolute joints to the existing degree-based trainer."""
        blockers = list(profile.validation_errors)
        warnings = list(profile.warnings)
        joint_names: list[str] = []
        limits: list[JointLimit] = []
        for joint in profile.joints:
            if joint.joint_type == "fixed":
                continue
            if joint.joint_type != "revolute":
                blockers.append(
                    f"Joint {joint.name} type {joint.joint_type} is not supported by the current degree-based trainer."
                )
                continue
            if (
                joint.lower_limit is None
                or joint.upper_limit is None
                or joint.velocity_limit is None
            ):
                blockers.append(
                    f"Joint {joint.name} lacks limits required by motion training."
                )
                continue
            joint_names.append(joint.name)
            limits.append(
                JointLimit(
                    joint_index=len(limits),
                    minimum_degrees=math.degrees(joint.lower_limit),
                    maximum_degrees=math.degrees(joint.upper_limit),
                    maximum_velocity_degrees_per_second=math.degrees(
                        joint.velocity_limit
                    ),
                )
            )
        if not limits:
            blockers.append("No compatible revolute joints are available for training.")
        return ARP1MotionContract(
            robot_model=profile.robot_model,
            joint_names=joint_names,
            joint_limits=limits,
            ready_for_motion_training=not blockers,
            blockers=list(dict.fromkeys(blockers)),
            warnings=list(dict.fromkeys(warnings)),
        )

    def _parse_links(
        self,
        root: ET.Element,
        errors: list[str],
        warnings: list[str],
    ) -> list[RobotLinkProfile]:
        profiles: list[RobotLinkProfile] = []
        names: set[str] = set()
        for element in root.findall("link"):
            name = element.attrib.get("name", "").strip()
            if not name:
                errors.append("Every URDF link requires a name.")
                continue
            if name in names:
                errors.append(f"Duplicate link name: {name}.")
                continue
            names.add(name)
            mass: float | None = None
            mass_element = element.find("./inertial/mass")
            if mass_element is not None and "value" in mass_element.attrib:
                mass = self._number(
                    mass_element.attrib["value"],
                    f"Link {name} mass",
                    errors,
                )
                if mass is not None and mass <= 0:
                    errors.append(f"Link {name} mass must be positive.")
                    mass = None
            profiles.append(
                RobotLinkProfile(
                    name=name,
                    mass_kg=mass,
                    has_visual_geometry=element.find("visual/geometry") is not None,
                    has_collision_geometry=element.find("collision/geometry") is not None,
                )
            )
        if not profiles:
            errors.append("URDF contains no valid links.")
        return profiles

    def _parse_joints(
        self,
        root: ET.Element,
        errors: list[str],
        warnings: list[str],
    ) -> list[RobotJointProfile]:
        profiles: list[RobotJointProfile] = []
        names: set[str] = set()
        for element in root.findall("joint"):
            name = element.attrib.get("name", "").strip()
            joint_type = element.attrib.get("type", "unknown").strip().lower()
            if not name:
                errors.append("Every URDF joint requires a name.")
                continue
            if name in names:
                errors.append(f"Duplicate joint name: {name}.")
                continue
            names.add(name)
            parent = element.find("parent")
            child = element.find("child")
            parent_name = "" if parent is None else parent.attrib.get("link", "").strip()
            child_name = "" if child is None else child.attrib.get("link", "").strip()
            if not parent_name or not child_name:
                errors.append(f"Joint {name} requires parent and child links.")

            axis_element = element.find("axis")
            default_axis = "1 0 0"
            axis = self._vector3(
                default_axis if axis_element is None else axis_element.attrib.get("xyz", default_axis),
                f"Joint {name} axis",
                errors,
            )
            limit = element.find("limit")
            lower = self._attribute_number(limit, "lower", name, errors)
            upper = self._attribute_number(limit, "upper", name, errors)
            velocity = self._attribute_number(limit, "velocity", name, errors)
            effort = self._attribute_number(limit, "effort", name, errors)
            if joint_type in {"revolute", "prismatic"} and (
                lower is None or upper is None
            ):
                errors.append(f"Joint {name} requires lower and upper limits.")
            if joint_type in self._MOVABLE_JOINTS and velocity is None:
                errors.append(f"Joint {name} requires a velocity limit.")
            if lower is not None and upper is not None and lower >= upper:
                errors.append(f"Joint {name} lower limit must be below upper limit.")
            if joint_type not in {
                "fixed",
                "revolute",
                "continuous",
                "prismatic",
                "floating",
                "planar",
            }:
                warnings.append(f"Joint {name} uses unsupported type {joint_type}.")
            position_unit, velocity_unit = self._units(joint_type)
            profiles.append(
                RobotJointProfile(
                    name=name,
                    joint_type=joint_type,
                    parent_link=parent_name,
                    child_link=child_name,
                    axis=axis,
                    lower_limit=lower,
                    upper_limit=upper,
                    velocity_limit=velocity,
                    effort_limit=effort,
                    position_unit=position_unit,
                    velocity_unit=velocity_unit,
                )
            )
        return profiles

    @staticmethod
    def _attribute_number(
        element: ET.Element | None,
        attribute: str,
        joint_name: str,
        errors: list[str],
    ) -> float | None:
        if element is None or attribute not in element.attrib:
            return None
        return RobotProfileService._number(
            element.attrib[attribute],
            f"Joint {joint_name} {attribute}",
            errors,
        )

    @staticmethod
    def _number(value: str, label: str, errors: list[str]) -> float | None:
        try:
            number = float(value)
        except ValueError:
            errors.append(f"{label} must be numeric.")
            return None
        if not math.isfinite(number):
            errors.append(f"{label} must be finite.")
            return None
        return number

    @staticmethod
    def _vector3(
        value: str,
        label: str,
        errors: list[str],
    ) -> tuple[float, float, float]:
        parts = value.split()
        if len(parts) != 3:
            errors.append(f"{label} must contain three numbers.")
            return (1.0, 0.0, 0.0)
        numbers = [RobotProfileService._number(item, label, errors) for item in parts]
        if any(item is None for item in numbers):
            return (1.0, 0.0, 0.0)
        return (numbers[0], numbers[1], numbers[2])  # type: ignore[return-value]

    @staticmethod
    def _units(joint_type: str) -> tuple[str, str]:
        if joint_type == "prismatic":
            return "meter", "meter_per_second"
        if joint_type in {"revolute", "continuous"}:
            return "radian", "radian_per_second"
        return "not_applicable", "not_applicable"

    @staticmethod
    def _recommend_simulator(robot_class: str) -> SimulatorRecommendation:
        normalized = robot_class.casefold()
        if normalized in {"quadruped", "humanoid", "animal-inspired"}:
            return SimulatorRecommendation(
                primary="mujoco",
                alternatives=["gazebo"],
                reason="Dynamic articulated locomotion benefits from a dynamics-first simulator.",
            )
        return SimulatorRecommendation(
            primary="gazebo",
            alternatives=["mujoco"],
            reason="General ROS-compatible robot models start with a Gazebo-oriented workflow.",
        )

    @staticmethod
    def _local_name(tag: str) -> str:
        return tag.rsplit("}", 1)[-1]
