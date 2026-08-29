"""Tests for URDF-to-ARP-1 normalization."""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


VALID_URDF = """
<robot name="sample_quadruped">
  <link name="base">
    <inertial><mass value="8.5"/></inertial>
    <visual><geometry><box size="1 1 1"/></geometry></visual>
    <collision><geometry><box size="1 1 1"/></geometry></collision>
  </link>
  <link name="upper_leg">
    <inertial><mass value="1.2"/></inertial>
    <collision><geometry><cylinder radius="0.05" length="0.3"/></geometry></collision>
  </link>
  <link name="foot">
    <inertial><mass value="0.3"/></inertial>
    <collision><geometry><sphere radius="0.04"/></geometry></collision>
  </link>
  <joint name="hip" type="revolute">
    <parent link="base"/><child link="upper_leg"/>
    <axis xyz="0 1 0"/>
    <limit lower="-1.2" upper="1.2" effort="40" velocity="3.0"/>
  </joint>
  <joint name="foot_mount" type="fixed">
    <parent link="upper_leg"/><child link="foot"/>
  </joint>
</robot>
"""


def test_valid_urdf_becomes_simulation_first_arp1_profile() -> None:
    response = client.post(
        "/api/robots/profiles/arp-1/import/urdf",
        json={
            "robot_model": "Sample Dog v1",
            "robot_class": "quadruped",
            "source_name": "sample.urdf",
            "urdf_xml": VALID_URDF,
        },
    )

    assert response.status_code == 200
    profile = response.json()
    assert profile["standard"] == "ARP-1"
    assert profile["version"] == "1.0"
    assert profile["source_format"] == "urdf"
    assert profile["root_links"] == ["base"]
    assert profile["actuated_joint_count"] == 1
    assert profile["joints"][0]["position_unit"] == "radian"
    assert profile["simulator"]["primary"] == "mujoco"
    assert profile["simulator"]["availability"] == "not_checked"
    assert profile["simulation_only"] is True
    assert profile["hardware_execution_approved"] is False
    assert profile["valid_for_kinematic_simulation"] is True

    contract_response = client.post(
        "/api/robots/profiles/arp-1/motion-contract",
        json=profile,
    )
    assert contract_response.status_code == 200
    contract = contract_response.json()
    assert contract["ready_for_motion_training"] is True
    assert contract["joint_names"] == ["hip"]
    assert round(contract["joint_limits"][0]["minimum_degrees"], 3) == -68.755
    assert round(contract["joint_limits"][0]["maximum_degrees"], 3) == 68.755
    assert contract["simulation_only"] is True


def test_missing_joint_limits_remain_visible_and_block_simulation_readiness() -> None:
    urdf = """
    <robot name="arm">
      <link name="base"/><link name="tool"/>
      <joint name="shoulder" type="revolute">
        <parent link="base"/><child link="tool"/>
      </joint>
    </robot>
    """
    response = client.post(
        "/api/robots/profiles/arp-1/import/urdf",
        json={
            "robot_model": "Unknown Arm",
            "robot_class": "arm",
            "urdf_xml": urdf,
        },
    )

    assert response.status_code == 200
    profile = response.json()
    assert profile["valid_for_kinematic_simulation"] is False
    assert any("lower and upper limits" in item for item in profile["validation_errors"])
    assert any("velocity limit" in item for item in profile["validation_errors"])
    assert any("collision geometry" in item for item in profile["warnings"])
    assert profile["simulator"]["primary"] == "gazebo"

    contract = client.post(
        "/api/robots/profiles/arp-1/motion-contract",
        json=profile,
    ).json()
    assert contract["ready_for_motion_training"] is False
    assert contract["joint_limits"] == []


def test_missing_link_reference_is_rejected_in_profile_evidence() -> None:
    urdf = """
    <robot name="broken">
      <link name="base"/>
      <joint name="orphan" type="fixed">
        <parent link="base"/><child link="missing"/>
      </joint>
    </robot>
    """
    response = client.post(
        "/api/robots/profiles/arp-1/import/urdf",
        json={"robot_model": "Broken", "urdf_xml": urdf},
    )

    assert response.status_code == 200
    profile = response.json()
    assert profile["valid_for_kinematic_simulation"] is False
    assert any("missing child link" in item for item in profile["validation_errors"])


def test_urdf_document_type_is_not_accepted() -> None:
    urdf = """<!DOCTYPE robot [<!ENTITY secret SYSTEM "file:///secret">]>
    <robot name="unsafe"><link name="&secret;"/></robot>"""
    response = client.post(
        "/api/robots/profiles/arp-1/import/urdf",
        json={"robot_model": "Unsafe", "urdf_xml": urdf},
    )

    assert response.status_code == 422
    assert "entity declarations" in response.json()["detail"]
