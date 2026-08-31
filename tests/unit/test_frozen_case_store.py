"""Tests for the protected frozen evaluation set and its provenance rule."""

import json
from pathlib import Path

from app.agents.evaluator import EvaluatorAgent
from app.models.learning import FrozenEvaluationRequest
from app.services.frozen_case_store import (
    DEFAULT_FROZEN_CASES_DIR,
    load_frozen_cases,
    resolve_frozen_cases_dir,
)


def write_case(directory: Path, case_id: str, authored_by: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{case_id}.json").write_text(
        json.dumps(
            {
                "case_id": case_id,
                "skill_id": "skill-under-test",
                "description": "A protected case used only by the tests.",
                "authored_by": authored_by,
                "expected": {"outcome": "expected-value"},
            }
        ),
        encoding="utf-8",
    )


def test_shipped_cases_load_and_are_externally_authored() -> None:
    cases = load_frozen_cases(DEFAULT_FROZEN_CASES_DIR)

    assert cases, "the project ships at least one frozen case"
    assert all(case.is_external_ground_truth for case in cases.values())
    assert all(case.authored_by != "generated" for case in cases.values())


def test_frozen_set_is_independent_of_the_writable_data_directory() -> None:
    assert resolve_frozen_cases_dir(None) == DEFAULT_FROZEN_CASES_DIR
    assert resolve_frozen_cases_dir("/elsewhere") == Path("/elsewhere")


def test_malformed_and_duplicate_cases_are_skipped(tmp_path: Path) -> None:
    write_case(tmp_path, "good-case", "human")
    (tmp_path / "broken.json").write_text("{ not json", encoding="utf-8")
    (tmp_path / "unknown-provenance.json").write_text(
        json.dumps(
            {
                "case_id": "unknown-provenance",
                "skill_id": "s",
                "description": "d",
                "authored_by": "vibes",
                "expected": {"a": 1},
            }
        ),
        encoding="utf-8",
    )

    cases = load_frozen_cases(tmp_path)

    assert list(cases) == ["good-case"]


def test_a_generated_answer_key_never_counts_as_validation(tmp_path: Path) -> None:
    write_case(tmp_path, "self-graded", "generated")
    agent = EvaluatorAgent(load_frozen_cases(tmp_path))

    result = agent.evaluate_frozen(
        FrozenEvaluationRequest(
            evaluation_id="eval-x",
            skill_id="skill-under-test",
            case_id="self-graded",
            actual_output={"outcome": "expected-value"},
        )
    )

    assert result.passed is True
    assert result.counts_as_external_validation is False
    assert agent.external_case_count == 0
    assert agent.case_count == 1


def test_missing_directory_yields_no_cases(tmp_path: Path) -> None:
    assert load_frozen_cases(tmp_path / "absent") == {}
