"""Validated procedure execution agent boundary."""


class ExecutorAgent:
    """Execute new tasks using validated stored procedural knowledge.

    Not implemented. Execution today happens only through explicitly approved,
    bounded adapters: file actions in a managed sandbox and browser actions in
    the container against an exact allowlisted host. Nothing maps a reviewed
    procedure onto those adapters yet, and no execution path may bypass the
    human approval those adapters require.
    """

    def execute(self, procedure: object, case: object) -> None:
        """Raise until a reviewed procedure can be mapped to approved actions."""
        raise NotImplementedError(
            "Executing a stored procedure is not implemented. Approved adapters "
            "must be called explicitly."
        )
