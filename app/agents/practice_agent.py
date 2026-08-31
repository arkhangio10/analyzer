"""Practice generation agent boundary."""


class PracticeAgent:
    """Create exercises and variations with progressive difficulty.

    Not implemented. Practice currently exists only as a human-written,
    human-approved browser rehearsal. Generating exercises requires the
    destination adaptation contract first, because an exercise has to be
    expressed in terms a destination can actually run.
    """

    def build_exercises(self, procedure: object, difficulty: int) -> list[object]:
        """Raise until destination adaptation exists to express an exercise."""
        raise NotImplementedError(
            "Practice generation requires destination adaptation, which is not "
            "implemented."
        )
