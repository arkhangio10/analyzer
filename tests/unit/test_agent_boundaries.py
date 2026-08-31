"""Unimplemented agents must fail loudly instead of returning fiction."""

import pytest

from app.agents.executor import ExecutorAgent
from app.agents.practice_agent import PracticeAgent
from app.agents.procedure_extractor import ProcedureExtractorAgent
from app.agents.video_instructor import VideoInstructorAgent


def test_video_understanding_is_not_silently_faked() -> None:
    with pytest.raises(NotImplementedError, match="not implemented"):
        VideoInstructorAgent().understand("https://youtu.be/-fD2TSL2s7I")


def test_separate_procedure_extraction_is_not_silently_faked() -> None:
    with pytest.raises(NotImplementedError, match="not implemented"):
        ProcedureExtractorAgent().extract(object())


def test_practice_generation_reports_its_missing_dependency() -> None:
    with pytest.raises(NotImplementedError, match="destination adaptation"):
        PracticeAgent().build_exercises(object(), 1)


def test_execution_never_bypasses_the_approved_adapters() -> None:
    with pytest.raises(NotImplementedError, match="Approved adapters"):
        ExecutorAgent().execute(object(), object())
