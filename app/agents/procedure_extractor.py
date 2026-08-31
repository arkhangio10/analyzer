"""Procedure extraction agent boundary."""

from app.models.procedure import Procedure


class ProcedureExtractorAgent:
    """Convert understood demonstrations into structured procedural memory.

    Not implemented. Today `GeminiService` returns a structured `Procedure`
    directly from the video, and `RobotMotionTrainingService` extracts an
    observation-level procedure from structured waypoints. This boundary is
    kept for the step that will turn a separately understood demonstration into
    procedural memory.
    """

    def extract(self, understanding: object) -> Procedure:
        """Raise until extraction is separate from provider understanding."""
        raise NotImplementedError(
            "Procedure extraction from a separate understanding step is not "
            "implemented."
        )
