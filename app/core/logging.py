"""Small logging setup shared by application entry points."""

import logging


def configure_logging(level: str = "INFO") -> None:
    """Configure standard-library logging for local development."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
