"""Root workflow coordinator for APRENDIZ."""

from uuid import uuid4

from app.agents.task_clarifier import TaskClarifierAgent
from app.models.project import ProjectClarificationRequest, ProjectDraft


class RootAgent:
    """Coordinate project intake before learning and evaluation begin."""

    def __init__(self, task_clarifier: TaskClarifierAgent | None = None) -> None:
        self._task_clarifier = task_clarifier or TaskClarifierAgent()

    def prepare_project(self, request: ProjectClarificationRequest) -> ProjectDraft:
        """Build the first auditable project state without external calls."""
        task, contract, questions, defaults = self._task_clarifier.clarify(request)
        is_clear = not questions
        return ProjectDraft(
            project_id=f"prj_{uuid4().hex[:12]}",
            task_definition=task,
            destination_contract=contract,
            clarification_questions=questions,
            defaults_applied=defaults,
            is_sufficiently_clear=is_clear,
            next_action="choose_source" if is_clear else "collect_details",
        )
