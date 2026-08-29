"""Deterministic task clarification without a cloud-model call."""

from app.models.project import (
    ClarificationQuestion,
    ComputerExecutionContract,
    ExecutionDestination,
    ProjectClarificationRequest,
    RobotExecutionContract,
)
from app.models.task import TaskDefinition


class TaskClarifierAgent:
    """Create a task and ask at most one destination-critical question."""

    def clarify(
        self, request: ProjectClarificationRequest
    ) -> tuple[
        TaskDefinition,
        ComputerExecutionContract | RobotExecutionContract,
        list[ClarificationQuestion],
        list[str],
    ]:
        description = request.task_description.strip()
        task_name = self._task_name(description)
        questions: list[ClarificationQuestion] = []
        defaults: list[str] = []

        if request.destination is ExecutionDestination.COMPUTER:
            operating_system = (request.computer_os or "").strip() or "auto-detect"
            application = (request.computer_application or "").strip() or None
            contract: ComputerExecutionContract | RobotExecutionContract = (
                ComputerExecutionContract(
                    operating_system=operating_system,
                    application=application,
                    locale=request.language,
                )
            )
            if operating_system == "auto-detect":
                defaults.append("computer.operating_system=auto-detect")
            defaults.extend(
                [
                    "computer.allowed_actions=browser,keyboard,mouse,files",
                    "computer.sandbox_required=true",
                ]
            )
            if application is None:
                questions.append(self._computer_question(request.language))
            expected_outputs = [
                "A reproducible computer procedure",
                "A sandboxed execution plan",
            ]
            constraints = ["Run in a sandbox before any real execution"]
            tools = [application] if application else []
        else:
            robot_model = (request.robot_model or "").strip() or None
            robot_class = (request.robot_class or "").strip() or "unknown"
            contract = RobotExecutionContract(
                robot_model=robot_model,
                robot_class=robot_class,
            )
            defaults.extend(
                [
                    "robot.profile_standard=ARP-1",
                    "robot.simulator=auto-select",
                    "robot.simulation_only=true",
                    "robot.hardware_execution_approved=false",
                ]
            )
            if robot_class == "unknown":
                defaults.append("robot.robot_class=unknown")
            if robot_model is None:
                questions.append(self._robot_question(request.language))
            expected_outputs = [
                "A robot-specific motion procedure",
                "A simulation validation report",
            ]
            constraints = [
                "Do not execute on physical hardware without explicit approval"
            ]
            tools = [robot_model] if robot_model else []

        clear = not questions
        definition = TaskDefinition(
            task_name=task_name,
            objective=description,
            expected_inputs=["Approved demonstration sources"],
            expected_outputs=expected_outputs,
            constraints=constraints,
            tools_involved=tools,
            success_criteria=[
                "The learned procedure reproduces the requested behavior",
                "The procedure passes destination-specific safety checks",
            ],
            clarification_questions=[question.question for question in questions],
            is_sufficiently_clear=clear,
        )
        return definition, contract, questions, defaults

    @staticmethod
    def _task_name(description: str) -> str:
        compact = " ".join(description.split())
        return compact if len(compact) <= 80 else f"{compact[:77].rstrip()}..."

    @staticmethod
    def _computer_question(language: str) -> ClarificationQuestion:
        if language == "en":
            return ClarificationQuestion(
                id="computer_application",
                field="computer_application",
                question="Which application should perform this task?",
                reason="The application defines the controls and safe execution boundary.",
            )
        return ClarificationQuestion(
            id="computer_application",
            field="computer_application",
            question="¿En qué aplicación debe ejecutarse esta tarea?",
            reason="La aplicación define los controles y el límite seguro de ejecución.",
        )

    @staticmethod
    def _robot_question(language: str) -> ClarificationQuestion:
        if language == "en":
            return ClarificationQuestion(
                id="robot_model",
                field="robot_model",
                question="What is the robot's exact brand and model?",
                reason="The model is required to select its kinematics and simulator.",
            )
        return ClarificationQuestion(
            id="robot_model",
            field="robot_model",
            question="¿Cuál es la marca y el modelo exacto del robot?",
            reason="El modelo permite seleccionar su cinemática y simulador.",
        )
