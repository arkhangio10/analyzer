"""Restart coverage for versioned, redacted workflow evidence."""

import asyncio
from pathlib import Path

from app.models.browser_execution import ComputerBrowserExecutionRequest
from app.models.computer_execution import (
    ComputerAction,
    ComputerActionKind,
    ComputerSandboxExecutionRequest,
)
from app.models.computer_practice import ComputerPracticeDraftRequest
from app.models.project import ProjectClarificationRequest
from app.models.robot_motion import (
    JointLimit,
    MotionWaypoint,
    RobotMotionEvaluationRequest,
    RobotMotionSessionRecord,
    RobotMotionTrainingRequest,
)
from app.services.browser_execution_service import BrowserExecutionService
from app.services.computer_execution_service import ComputerExecutionService
from app.services.computer_practice_service import ComputerPracticeService
from app.services.project_service import ProjectService
from app.services.record_store import JsonRecordStore
from app.services.robot_motion_training import RobotMotionTrainingService


def test_robot_session_and_evaluation_survive_restart(tmp_path: Path) -> None:
    directory = tmp_path / "robot-motion-sessions"
    service = RobotMotionTrainingService(store=JsonRecordStore(directory))
    request = RobotMotionTrainingRequest(
        task_name="Move a fixture",
        objective="Replay a bounded two-joint trajectory.",
        robot_model="SimArm-2",
        demonstration_id="demo-001",
        source="instructor://fixture/001",
        waypoints=[
            MotionWaypoint(timestamp_seconds=0, joint_positions_degrees=[0, 0]),
            MotionWaypoint(timestamp_seconds=1, joint_positions_degrees=[5, 5]),
        ],
        joint_limits=[
            JointLimit(
                joint_index=0,
                minimum_degrees=-20,
                maximum_degrees=20,
                maximum_velocity_degrees_per_second=10,
            ),
            JointLimit(
                joint_index=1,
                minimum_degrees=-20,
                maximum_degrees=20,
                maximum_velocity_degrees_per_second=10,
            ),
        ],
        instructor_verified=True,
    )
    trained = service.train(request)

    restarted = RobotMotionTrainingService(store=JsonRecordStore(directory))
    assert restarted.get_result(trained.session_id) == trained
    evaluation = restarted.evaluate(
        trained.session_id,
        RobotMotionEvaluationRequest(
            execution_id="execution-001",
            waypoints=request.waypoints,
        ),
    )
    assert evaluation.passed is True

    records = JsonRecordStore(directory).load_all(RobotMotionSessionRecord)
    record = records[trained.session_id]
    assert record.schema_version == 1
    assert record.evaluations == [evaluation]


def test_sandbox_execution_persists_only_redacted_evidence(tmp_path: Path) -> None:
    records = tmp_path / "computer-executions"
    service = ComputerExecutionService(
        sandbox_root=tmp_path / "sandboxes",
        store=JsonRecordStore(records),
    )
    result = service.execute(
        ComputerSandboxExecutionRequest(
            project_id="prj_test",
            application="Files",
            actions=[
                ComputerAction(
                    action_id="write",
                    kind=ComputerActionKind.WRITE_FILE,
                    target="result.txt",
                    value_template="private payload",
                )
            ],
            acknowledge_local_sandbox_write=True,
        )
    )

    stored_json = (records / f"{result.execution_id}.json").read_text("utf-8")
    assert '"schema_version": 1' in stored_json
    assert "private payload" not in stored_json
    restarted = ComputerExecutionService(
        sandbox_root=tmp_path / "sandboxes",
        store=JsonRecordStore(records),
    )
    assert restarted.get_execution(result.execution_id) == result


def test_browser_execution_survives_without_request_secrets(tmp_path: Path) -> None:
    records = tmp_path / "browser-executions"
    service = BrowserExecutionService(
        enabled=False,
        isolation_boundary="application_container",
        store=JsonRecordStore(records),
    )
    request = ComputerBrowserExecutionRequest(
        project_id="prj_test",
        application="Chromium",
        actions=[
            ComputerAction(
                action_id="open",
                kind=ComputerActionKind.NAVIGATE,
                target="https://example.com/form?token=private",
            ),
            ComputerAction(
                action_id="type",
                kind=ComputerActionKind.TYPE_TEXT,
                target="input[name='display-name']",
                value_template="Private name",
            ),
        ],
        approved_hosts=["example.com"],
        acknowledge_external_network=True,
    )
    result = asyncio.run(service.execute(request))

    stored_json = (records / f"{result.execution_id}.json").read_text("utf-8")
    assert '"schema_version": 1' in stored_json
    assert "token=private" not in stored_json
    assert "Private name" not in stored_json
    restarted = BrowserExecutionService(
        enabled=False,
        isolation_boundary="application_container",
        store=JsonRecordStore(records),
    )
    assert restarted.get_execution(result.execution_id) == result


def test_pending_practice_restarts_blocked_with_private_values_removed(
    tmp_path: Path,
) -> None:
    project_records = tmp_path / "projects"
    practice_records = tmp_path / "computer-practices"
    project_service = ProjectService(store=JsonRecordStore(project_records))
    project = project_service.create(
        ProjectClarificationRequest(
            task_description="Complete a bounded public form with reviewed data.",
            destination="computer",
            computer_application="Chromium",
            language="en",
        )
    )
    browser = BrowserExecutionService(enabled=False)
    service = ComputerPracticeService(
        project_service,
        browser,
        store=JsonRecordStore(practice_records),
    )
    practice = service.create(
        project.project_id,
        ComputerPracticeDraftRequest(
            procedure_name="Reviewed public form",
            approved_hosts=["example.com"],
            actions=[
                ComputerAction(
                    action_id="open",
                    kind=ComputerActionKind.NAVIGATE,
                    target="https://example.com/form?token=private",
                ),
                ComputerAction(
                    action_id="type",
                    kind=ComputerActionKind.TYPE_TEXT,
                    target="input[name='display-name']",
                    value_template="Private name",
                ),
            ],
        ),
    )

    stored_json = (practice_records / f"{practice.practice_id}.json").read_text(
        "utf-8"
    )
    assert '"schema_version": 1' in stored_json
    assert "token=private" not in stored_json
    assert "Private name" not in stored_json

    restarted_projects = ProjectService(store=JsonRecordStore(project_records))
    restarted = ComputerPracticeService(
        restarted_projects,
        BrowserExecutionService(enabled=False),
        store=JsonRecordStore(practice_records),
    )
    reloaded = restarted.get(project.project_id, practice.practice_id)
    assert reloaded.status == "blocked"
    assert reloaded.actions[0].target == "https://example.com/form"
    assert reloaded.actions[1].value_template is None
    assert any("redacted at rest" in item for item in reloaded.violations)
