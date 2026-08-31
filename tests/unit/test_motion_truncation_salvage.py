"""Tests for recovering a paid motion response that ran out of room."""

from app.models.motion_analysis import ObservedMotionReport
from app.services.gemini_service import GeminiService


COMPLETE_PREFIX = (
    '{\n  "subject_kind": "human_body",\n'
    '  "kinematic_chain": "bipedal_lower_limb",\n'
    '  "phases": [\n'
    '    {"name": "stance", "start_seconds": 0.0, "end_seconds": 1.0,'
    ' "description": "Weight on one leg."}\n'
    '  ],\n'
    '  "samples": [\n'
    '    {"t": 60.0, "j": "left.hip", "a": 10.0, "c": 0.7, "v": "clear"},\n'
    '    {"t": 60.25, "j": "left.hip", "a": 12.0, "c": 0.7, "v": "clear"},\n'
    '    {"t": 60.5, "j": "left.hip"'
)


def test_a_response_cut_mid_sample_keeps_every_complete_row() -> None:
    report = GeminiService._salvage_motion_report(COMPLETE_PREFIX)

    assert isinstance(report, ObservedMotionReport)
    assert report.subject_kind == "human_body"
    assert report.kinematic_chain == "bipedal_lower_limb"
    assert len(report.samples) == 2
    assert report.samples[0].j == "left.hip"
    assert len(report.phases) == 1


def test_the_salvage_admits_itself_in_the_uncertainties() -> None:
    report = GeminiService._salvage_motion_report(COMPLETE_PREFIX)

    assert report is not None
    assert len(report.uncertainties) == 1
    note = report.uncertainties[0]
    assert "output limit" in note
    assert "after 2 samples" in note
    assert "nothing was reconstructed" in note


def test_a_response_cut_before_any_sample_is_not_salvaged() -> None:
    assert GeminiService._salvage_motion_report('{"subject_kind": "hum') is None
    assert GeminiService._salvage_motion_report('{"samples": [') is None


def test_a_string_containing_braces_does_not_confuse_the_scanner() -> None:
    text = (
        '{"samples": [{"t": 1.0, "j": "left.knee", "a": 1.0, "c": 0.5,'
        ' "v": "clear {not a brace}"}, {"t": 2.0, "j": "left'
    )

    items = GeminiService._complete_objects(text, "samples")

    assert len(items) == 1
    assert items[0]["v"] == "clear {not a brace}"
