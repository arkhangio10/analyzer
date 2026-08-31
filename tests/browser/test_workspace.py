"""Browser coverage for the behaviour that was previously only checked by eye.

Every assertion here is about something a person would notice: text that does
not translate, a control stranded outside its panel, a claim the interface must
never make, or a script error that leaves the page half-rendered.
"""

from __future__ import annotations

import pytest

from tests.browser.conftest import PROJECT_ID


VIEWPORTS = [(1920, 1080), (1440, 900), (1366, 768), (1280, 620), (1024, 600)]


def text_of(page, selector: str) -> str:
    node = page.query_selector(selector)
    return (node.inner_text().strip() if node else "").replace("\n", " ")


def test_the_landing_page_renders_without_script_errors(page) -> None:
    assert page.title()
    assert page.query_selector("#motion-canvas") is not None
    assert page.errors == []


def test_saved_work_reopens_the_project_it_names(workspace) -> None:
    assert "Walk with aligned posture" in text_of(workspace, "#procedure-task")
    assert workspace.query_selector("#procedure-steps li") is not None
    assert workspace.errors == []


def test_the_language_switch_relabels_the_whole_workspace(workspace) -> None:
    workspace.query_selector("[data-language='en']").evaluate("node => node.click()")
    workspace.wait_for_timeout(700)
    english = {
        "history": text_of(workspace, "#history-label"),
        "motion": text_of(workspace, "#motion-evidence-label"),
        "upload": text_of(workspace, "#upload-note"),
    }

    workspace.query_selector("[data-language='es']").evaluate("node => node.click()")
    workspace.wait_for_timeout(700)
    spanish = {
        "history": text_of(workspace, "#history-label"),
        "motion": text_of(workspace, "#motion-evidence-label"),
        "upload": text_of(workspace, "#upload-note"),
    }

    assert english["history"] == "VERSION HISTORY"
    assert spanish["history"] == "HISTORIAL DE VERSIONES"
    assert english["motion"] == "MOTION EVIDENCE"
    assert spanish["motion"] == "EVIDENCIA DE MOVIMIENTO"
    assert english["upload"] != spanish["upload"]
    assert workspace.errors == []


def test_the_motion_panel_reports_the_audit_verdict_and_its_findings(workspace) -> None:
    verdict = workspace.query_selector("#motion-verdict")

    assert verdict.get_attribute("data-verdict") == "not_evidence"
    assert verdict.inner_text().strip()
    findings = workspace.query_selector_all("#motion-findings li")
    assert len(findings) == 2
    assert "24" in text_of(workspace, "#motion-stats")
    assert text_of(workspace, "#motion-estimate")
    assert workspace.errors == []


def test_the_interface_never_claims_the_samples_were_measured(workspace) -> None:
    body = workspace.inner_text("body").casefold()

    assert "physically measured" not in body
    assert "estimated by a vision model" in body or "modelo de visi" in body
    assert text_of(workspace, "#motion-retarget")


def test_the_cost_acknowledgement_gates_the_paid_button(workspace) -> None:
    button = workspace.query_selector("#run-motion-analysis")
    assert button.is_disabled() is True

    workspace.check("#motion-cost-approval")
    workspace.wait_for_timeout(200)
    enabled = workspace.query_selector("#run-motion-analysis").is_disabled()

    workspace.uncheck("#motion-cost-approval")
    workspace.wait_for_timeout(200)
    disabled_again = workspace.query_selector("#run-motion-analysis").is_disabled()

    assert enabled is False
    assert disabled_again is True


def test_version_history_lists_both_versions_and_diffs_them(workspace) -> None:
    versions = workspace.query_selector_all("#history-versions li")
    summary = text_of(workspace, "#history-diff-summary")
    changes = workspace.query_selector_all("#history-changes li")

    assert len(versions) == 2
    assert summary
    assert len(changes) >= 1
    assert workspace.errors == []


def test_reconciliation_warns_that_one_video_is_not_confirmation(workspace) -> None:
    banner = workspace.query_selector("#reconciliation-independence")

    assert banner is not None
    assert banner.get_attribute("data-cross") == "false"
    assert "repeating itself" in banner.inner_text() or "repiti" in banner.inner_text()
    assert "1" in text_of(workspace, "#reconciliation-summary")


def test_choosing_a_local_video_does_not_discard_the_open_project(
    setup_view,
) -> None:
    """Selecting the upload option must not throw away the reopened project."""
    assert setup_view.query_selector("#upload-note").inner_text().strip()
    assert "proyecto" not in text_of(setup_view, "#upload-error")


def test_a_video_can_be_kept_on_this_machine_from_the_interface(
    setup_view,
    tmp_path,
) -> None:
    workspace = setup_view
    clip = tmp_path / "demo.mp4"
    clip.write_bytes(b"browser upload bytes")

    workspace.set_input_files("#video-file", str(clip))
    workspace.wait_for_timeout(300)
    assert workspace.query_selector("#store-video-file").is_disabled() is False

    workspace.click("#store-video-file")
    workspace.wait_for_selector("#upload-list li", state="visible", timeout=15000)

    entry = text_of(workspace, "#upload-list li")
    assert "demo.mp4" in entry
    assert "20 B" in entry
    assert text_of(workspace, "#upload-error") == ""
    assert workspace.errors == []


def test_a_file_that_is_not_video_is_refused_in_the_interface(
    setup_view,
    tmp_path,
) -> None:
    workspace = setup_view
    notes = tmp_path / "notes.txt"
    notes.write_text("not a video", encoding="utf-8")

    workspace.set_input_files("#video-file", str(notes))
    workspace.wait_for_timeout(300)
    workspace.click("#store-video-file")
    workspace.wait_for_timeout(1500)

    error = text_of(workspace, "#upload-error")
    assert "video" in error.casefold()
    assert workspace.query_selector_all("#upload-list li") == []


@pytest.mark.parametrize("width,height", VIEWPORTS)
def test_no_panel_scrolls_the_page_sideways(page, width: int, height: int) -> None:
    page.set_viewport_size({"width": width, "height": height})
    page.wait_for_timeout(400)

    overflow = page.evaluate(
        "() => document.documentElement.scrollWidth"
        " > document.documentElement.clientWidth"
    )

    assert overflow is False
    assert page.errors == []


def test_every_control_stays_inside_the_panel_that_owns_it(workspace) -> None:
    stranded = workspace.evaluate(
        """() => {
            const ids = [
              '#approve-video-procedure', '#reject-video-procedure',
              '#run-motion-analysis', '#store-video-file',
            ];
            const bad = [];
            for (const id of ids) {
              const el = document.querySelector(id);
              if (!el || el.offsetParent === null) continue;
              const panel = el.closest('.workspace-panel, section, article, fieldset');
              if (!panel) continue;
              const a = el.getBoundingClientRect();
              const b = panel.getBoundingClientRect();
              if (a.right > b.right + 2 || a.left < b.left - 2) bad.push(id);
            }
            return bad;
        }"""
    )

    assert stranded == []


def test_the_status_endpoint_reports_durable_storage(page, live_server: str) -> None:
    response = page.request.get(f"{live_server}/api/status")

    assert response.ok
    assert response.json()["durable_storage"] is True


def test_the_seeded_project_is_the_one_under_test(page, live_server: str) -> None:
    response = page.request.get(f"{live_server}/api/projects")

    assert response.ok
    assert [item["project_id"] for item in response.json()] == [PROJECT_ID]
