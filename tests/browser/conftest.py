"""A real browser against a real server, seeded with real-shaped records.

Every interface check in this project used to be a person looking at a screen.
These fixtures make that repeatable: they seed a data directory, start the
application in its own process against it, and hand tests a Chrome page.

The server runs as a separate process, so records are written to disk before it
starts rather than injected into its memory. That is also closer to what a user
does, which is open work that was already saved.
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
CHROME_CANDIDATES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
    Path("/usr/bin/google-chrome"),
    Path("/usr/bin/chromium"),
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
)

PROJECT_ID = "prj_browsertest"
EXTRACTION_ID = "vpr_browsertest1"
SECOND_EXTRACTION_ID = "vpr_browsertest2"
SOURCE_URL = "https://youtu.be/-fD2TSL2s7I"
BASE_TIME = datetime(2026, 8, 30, 12, 0, tzinfo=timezone.utc)


def find_chrome() -> Path | None:
    """Return an installed Chrome, or None when the suite must be skipped."""
    for candidate in CHROME_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, default=str), encoding="utf-8")


def seed(data_dir: Path) -> None:
    """Write one project, two procedure versions, and a motion analysis."""
    from app.models.motion_analysis import (
        MotionAnalysisRecord,
        MotionEvidenceAudit,
        MotionAuditCode,
        MotionAuditFinding,
        MotionEvidenceVerdict,
        MotionRetargetVerdict,
        MotionSubjectKind,
        ObservedJointAngle,
    )
    from app.models.procedure import Procedure, ProcedureStep
    from app.models.project import ProjectDraft, RobotExecutionContract
    from app.models.project_video_procedure import (
        ProjectVideoProcedureRecord,
        ProjectVideoProcedureStatus,
    )
    from app.models.task import TaskDefinition
    from app.models.video_extraction import GeminiUsage

    records = data_dir / "records"

    project = ProjectDraft(
        project_id=PROJECT_ID,
        task_definition=TaskDefinition(
            task_name="Walk with aligned posture",
            objective="Demonstrate the instructed walking sequence.",
        ),
        destination_contract=RobotExecutionContract(
            robot_model="APRENDIZ SimArm-6",
            robot_class="humanoid",
        ),
        is_sufficiently_clear=True,
        next_action="choose_source",
    )
    _write(records / "projects" / f"{PROJECT_ID}.json", project.model_dump(mode="json"))

    def procedure(actions: list[str]) -> Procedure:
        return Procedure(
            task="Walk with aligned posture",
            objective="Demonstrate the instructed walking sequence.",
            steps=[
                ProcedureStep(
                    step=index + 1,
                    action=action,
                    source_timestamps=["01:05", "01:08"][index : index + 1],
                    evidence="The instructor demonstrates the movement.",
                )
                for index, action in enumerate(actions)
            ],
            uncertainties=["The camera does not show foot pressure."],
            rules=["Keep the torso upright."],
        )

    first = ProjectVideoProcedureRecord(
        extraction_id=EXTRACTION_ID,
        project_id=PROJECT_ID,
        procedure_version=1,
        source_url=SOURCE_URL,
        status=ProjectVideoProcedureStatus.APPROVED,
        procedure=procedure(
            ["Push off with the hips.", "Swing the trailing leg forward."]
        ),
        provider="vertex_ai",
        requested_model="gemini-2.5-flash-lite",
        elapsed_seconds=12.3,
        usage=GeminiUsage(total_tokens=24555),
        cloud_calls_made=1,
        created_at=BASE_TIME,
    )
    second = first.model_copy(
        update={
            "extraction_id": SECOND_EXTRACTION_ID,
            "procedure_version": 2,
            "procedure": procedure(
                ["Drive the knee forward.", "Swing the trailing leg forward."]
            ),
            "usage": GeminiUsage(total_tokens=23100),
            "created_at": BASE_TIME + timedelta(minutes=10),
        }
    )
    for record in (first, second):
        _write(
            records / "video-procedures" / f"{record.extraction_id}.json",
            record.model_dump(mode="json"),
        )

    samples = [
        ObservedJointAngle(
            timestamp_seconds=round(60 + index * 0.25, 3),
            joint_name="hip",
            side=side,
            angle_degrees=10.0 + index,
            confidence=0.7,
            visibility="partial",
        )
        for index in range(12)
        for side in ("left", "right")
    ]
    analysis = MotionAnalysisRecord(
        analysis_id="mot_browsertest1",
        project_id=PROJECT_ID,
        # The workspace opens the newest extraction, so the analysis is
        # attached to that one. Version 1 stays without an analysis, which
        # also exercises the "no analysis yet" path.
        extraction_id=SECOND_EXTRACTION_ID,
        source_url=SOURCE_URL,
        requested_fps=4.0,
        window_start_seconds=60.0,
        window_end_seconds=72.0,
        subject_kind=MotionSubjectKind.HUMAN_BODY,
        kinematic_chain="bipedal_lower_limb",
        joint_names=["hip"],
        samples=samples,
        uncertainties=["Clothing hides the knees."],
        sample_count=len(samples),
        distinct_joint_count=2,
        observed_span_seconds=2.75,
        samples_per_second=8.7,
        mean_confidence=0.7,
        clear_sample_count=0,
        audit=MotionEvidenceAudit(
            verdict=MotionEvidenceVerdict.NOT_EVIDENCE,
            findings=[
                MotionAuditFinding(
                    code=MotionAuditCode.MIRRORED_SIDES,
                    message="Left and right carry exactly the same angle.",
                    values={"identical": "12", "paired": "12"},
                ),
                MotionAuditFinding(
                    code=MotionAuditCode.UNIFORM_CONFIDENCE,
                    message="All samples report the identical confidence.",
                    values={"samples": "24", "confidence": "0.7"},
                ),
            ],
            mirrored_frame_ratio=1.0,
            distinct_confidence_values=1,
            distinct_visibility_values=1,
            acyclic_joints=[],
            checked_joint_count=2,
        ),
        retarget=MotionRetargetVerdict(
            retarget_supported=False,
            destination_robot_model="APRENDIZ SimArm-6",
            observed_chain="bipedal_lower_limb",
            reason="These samples did not survive the plausibility audit.",
            missing_evidence=["A human-authored joint map."],
        ),
        provider="vertex_ai",
        requested_model="gemini-2.5-flash-lite",
        elapsed_seconds=44.3,
        usage=GeminiUsage(total_tokens=24820),
        created_at=BASE_TIME + timedelta(minutes=20),
    )
    _write(
        records / "motion-analyses" / f"{analysis.analysis_id}.json",
        analysis.model_dump(mode="json"),
    )


@pytest.fixture(scope="session")
def chrome_path() -> Path:
    path = find_chrome()
    if path is None:
        pytest.skip("Chrome is not installed on this machine.")
    return path


@pytest.fixture(scope="session")
def live_server(chrome_path: Path) -> str:  # noqa: ARG001
    """Serve the application from its own process against a seeded data dir."""
    data_dir = Path(tempfile.mkdtemp(prefix="aprendiz-browser-"))
    seed(data_dir)
    port = free_port()
    environment = {**os.environ, "DATA_DIR": str(data_dir), "GOOGLE_GENAI_ENABLED": "false"}
    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
            "--log-level",
            "warning",
        ],
        cwd=str(REPO_ROOT),
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    base = f"http://127.0.0.1:{port}"
    try:
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("The application process exited during startup.")
            try:
                with urllib.request.urlopen(f"{base}/api/status", timeout=2):
                    break
            except (urllib.error.URLError, ConnectionError, OSError):
                time.sleep(0.3)
        else:
            raise RuntimeError("The application did not start in time.")
        yield base
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        shutil.rmtree(data_dir, ignore_errors=True)


@pytest.fixture(scope="session")
def browser(chrome_path: Path):
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as driver:
        instance = driver.chromium.launch(
            executable_path=str(chrome_path),
            headless=True,
        )
        yield instance
        instance.close()


def clear_uploads(base: str) -> None:
    """Delete every retained upload so each test starts from an empty list.

    The application process is shared across the session, so this runs before
    the page loads rather than after: the interface renders its list on open,
    and deleting afterwards would leave a stale row on screen.
    """
    try:
        with urllib.request.urlopen(
            f"{base}/api/projects/{PROJECT_ID}/uploads", timeout=5
        ) as response:
            uploads = json.load(response).get("uploads", [])
    except (urllib.error.URLError, OSError, ValueError):
        return
    for upload in uploads:
        request = urllib.request.Request(
            f"{base}/api/projects/{PROJECT_ID}/uploads/{upload['upload_id']}",
            method="DELETE",
        )
        try:
            urllib.request.urlopen(request, timeout=5).close()
        except (urllib.error.URLError, OSError):
            return


# Chrome logs every 4xx response as a console error. Some of those are correct
# behaviour: asking whether an extraction has a motion analysis is supposed to
# return 404 when it does not. Only a thrown exception or a console.error the
# application itself wrote is a defect, so resource noise is filtered out.
RESOURCE_NOISE = "failed to load resource"


@pytest.fixture
def page(browser, live_server: str):
    """A page collecting script errors, but not expected 404 response noise."""
    clear_uploads(live_server)
    context = browser.new_context(viewport={"width": 1366, "height": 900})
    page = context.new_page()
    page.errors = []
    page.on("pageerror", lambda exc: page.errors.append(str(exc)))
    page.on(
        "console",
        lambda message: (
            page.errors.append(message.text)
            if message.type == "error"
            and RESOURCE_NOISE not in message.text.casefold()
            else None
        ),
    )
    page.goto(f"{live_server}/#entrenar", wait_until="networkidle")
    yield page
    context.close()


@pytest.fixture
def workspace(page):
    """A page with the seeded project already opened in the workspace."""
    page.wait_for_selector("#recent-work button", state="visible", timeout=20000)
    card = page.query_selector("#recent-work button")
    box = card.bounding_box()
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    page.wait_for_selector("#procedure-review", state="visible", timeout=20000)
    page.wait_for_timeout(800)
    return page


@pytest.fixture
def setup_view(workspace):
    """The workspace on the source step, with the local-video option chosen.

    Reopening saved work lands on the review step, so this walks back to the
    source step the way a person would rather than forcing the panel visible.
    """
    workspace.query_selector("[data-workspace-target='setup']").evaluate(
        "node => node.click()"
    )
    workspace.wait_for_timeout(300)
    for _ in range(4):
        panel = workspace.query_selector('[data-source-panel="upload"]')
        if workspace.query_selector('[data-step="3"]:not([hidden])'):
            break
        back = workspace.query_selector('.form-step:not([hidden]) [data-back]')
        if back is None:
            break
        back.click()
        workspace.wait_for_timeout(300)
    workspace.wait_for_selector('[data-step="3"]', state="visible", timeout=10000)
    workspace.click("[data-source-option='upload']")
    workspace.wait_for_selector(
        '[data-source-panel="upload"]',
        state="visible",
        timeout=10000,
    )
    return workspace
