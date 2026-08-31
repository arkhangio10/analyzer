"""Project intake service for the MVP workflow."""

from app.agents.root_agent import RootAgent
from app.models.project import ProjectClarificationRequest, ProjectDraft
from app.services.record_store import JsonRecordStore


class ProjectNotFoundError(LookupError):
    """Raised when a project identifier is unknown."""


class ProjectService:
    """Create and retrieve project drafts, reloading any stored on disk."""

    def __init__(
        self,
        root_agent: RootAgent | None = None,
        store: JsonRecordStore | None = None,
    ) -> None:
        self._root_agent = root_agent or RootAgent()
        self._store = store
        self._projects: dict[str, ProjectDraft] = (
            store.load_all(ProjectDraft) if store else {}
        )

    @property
    def is_durable(self) -> bool:
        """Report whether created projects survive a restart."""
        return bool(self._store and self._store.is_durable)

    def create(self, request: ProjectClarificationRequest) -> ProjectDraft:
        project = self._root_agent.prepare_project(request)
        self._projects[project.project_id] = project
        if self._store:
            self._store.save(project.project_id, project)
        return project

    def list_projects(self) -> list[ProjectDraft]:
        """Return every retained project draft."""
        return list(self._projects.values())

    def get(self, project_id: str) -> ProjectDraft:
        try:
            return self._projects[project_id]
        except KeyError as error:
            raise ProjectNotFoundError(project_id) from error
