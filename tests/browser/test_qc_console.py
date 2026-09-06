"""A real browser against the QC console.

The console's claim is that a reader can check a verdict rather than trust it,
so these tests drive it the way a reader would: open the library, inspect an
asset, and press the button that recomputes the verdict from the stored
samples. What they assert is that the numbers and the chart are actually on the
page -- a console that renders a verdict and nothing else would pass a route
test and fail the only thing it exists for.

Script errors fail the test. The console draws its own SVG and loads no
third-party script, so there is nothing on the page whose errors are somebody
else's to fix. Failed-resource messages are filtered for one reason only: the
browser asks for /favicon.ico unprompted and the app does not serve one. Every
asset the console itself requests is asserted to load by the tests passing.
"""

from __future__ import annotations

import pytest

from tests.browser.conftest import PROJECT_ID, RESOURCE_NOISE


@pytest.fixture
def qc(browser, live_server: str):
    """The QC console, with the seeded project's library already open."""
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
    page.goto(f"{live_server}/qc", wait_until="networkidle")
    page.fill("#project-id", PROJECT_ID)
    page.click("#load-library")
    page.wait_for_selector("#library-panel", state="visible", timeout=20000)
    yield page
    context.close()


def test_the_library_lists_the_seeded_analysis(qc) -> None:
    rows = qc.query_selector_all("#analysis-table tbody tr")

    assert rows, "the library listed no analysis"
    assert qc.inner_text("#evidence-note").strip(), "the library did not say where it looked"
    assert qc.errors == []


def test_inspecting_an_asset_shows_the_counts_and_the_chart(qc) -> None:
    qc.click("#analysis-table tbody tr button")
    qc.wait_for_selector("#detail-panel", state="visible", timeout=20000)

    counts = qc.inner_text("#counts-table").casefold()
    for label in (
        "Samples returned",
        "Mirrored frame ratio",
        "Distinct confidence values",
        "Joints checked for cycles",
    ):
        assert label.casefold() in counts, label

    assert qc.query_selector("#series-chart path"), "no series was plotted"
    assert qc.inner_text("#series-caption").strip(), "the chart did not say what it plots"
    assert qc.inner_text("#detail-verdict").strip()
    assert qc.errors == []


def test_the_verdict_is_never_shown_without_the_findings_behind_it(qc) -> None:
    qc.click("#analysis-table tbody tr button")
    qc.wait_for_selector("#detail-panel", state="visible", timeout=20000)

    findings = qc.query_selector_all("#findings-list li")
    no_findings_visible = qc.is_visible("#no-findings")

    assert findings or no_findings_visible, (
        "the detail view showed a verdict with neither findings nor a statement "
        "that there were none"
    )
    assert qc.errors == []


def test_pressing_prove_recomputes_and_reports_each_stage(qc) -> None:
    qc.click("#analysis-table tbody tr button")
    qc.wait_for_selector("#detail-panel", state="visible", timeout=20000)

    qc.click("#prove-button")
    qc.wait_for_selector("#prove-result", state="visible", timeout=20000)

    headline = qc.inner_text("#prove-headline")
    assert headline.strip(), "proving reported nothing"

    stages = [item.strip() for item in qc.inner_text("#prove-stages").split("\n") if item.strip()]
    joined = " ".join(stages)
    for stage in ("ingest", "extraction", "approval_gate", "audit", "report"):
        assert stage in joined, stage

    assert qc.errors == []


def test_the_console_carries_no_robot_controls_or_language_toggle(qc) -> None:
    """The robot track and the bilingual toggle stay on the product surface."""
    body = qc.inner_text("body").casefold()

    assert "robot" not in body
    assert "espa" not in body
    assert qc.query_selector("#setup-wizard") is None
    assert qc.errors == []


def test_an_unknown_project_is_reported_rather_than_shown_empty(
    browser, live_server: str
) -> None:
    context = browser.new_context(viewport={"width": 1366, "height": 900})
    page = context.new_page()
    try:
        page.goto(f"{live_server}/qc", wait_until="networkidle")
        page.fill("#project-id", "prj_doesnotexist")
        page.click("#load-library")
        page.wait_for_selector("#library-error", state="visible", timeout=20000)

        assert "not found" in page.inner_text("#library-error").casefold()
        assert not page.is_visible("#library-panel")
    finally:
        context.close()


def test_the_seeded_extraction_is_the_one_the_console_proves(qc) -> None:
    """Guards the wiring: the row's extraction is what prove is called with."""
    qc.click("#analysis-table tbody tr button")
    qc.wait_for_selector("#detail-panel", state="visible", timeout=20000)

    expected = qc.evaluate(
        """async (projectId) => {
            const response = await fetch(`/api/qc/projects/${projectId}/library`);
            const view = await response.json();
            return view.analyses[0].extraction_id;
        }""",
        PROJECT_ID,
    )

    with qc.expect_request(
        lambda request: "/prove" in request.url and request.method == "POST"
    ) as caught:
        qc.click("#prove-button")

    assert expected in caught.value.url, (
        "the console proved a different extraction from the row it opened"
    )
    assert PROJECT_ID in caught.value.url
