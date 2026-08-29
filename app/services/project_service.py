"""In-memory project intake service for the MVP workflow."""

from app.agents.root_agent import RootAgent
from app.models.project import ProjectClarificationRequest, ProjectDraft


class ProjectNotFoundError(LookupError):
    """Raised when a project identifier is unknown."""


class ProjectService:
    """Create and retrieve project drafts during the local MVP session."""

    def __init__(self, root_agent: RootAgent | None = None) -> None:
        self._root_agent = root_agent or RootAgent()
        self._projects: dict[str, ProjectDraft] = {}

    def create(self, request: ProjectClarificationRequest) -> ProjectDraft:
        project = self._root_agent.prepare_project(request)
        self._projects[project.project_id] = project
        return project

    def get(self, project_id: str) -> ProjectDraft:
        try:
            return self._projects[project_id]
        except KeyError as error:
            raise ProjectNotFoundError(project_id) from error
