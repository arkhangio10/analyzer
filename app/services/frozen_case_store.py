"""Read-only loader for the protected frozen evaluation set.

Frozen cases are the project's defence against circular self-grading, so this
module only ever reads them. Nothing in the learning loop may write here, and
every case must declare who authored its expected answer:

- `human`: a person decided the expected result, usually after watching the
  source. This is the only provenance that counts as external ground truth for
  video-derived procedures.
- `specification`: the expected result follows deterministically from a
  documented rule, such as a stated joint velocity limit, and can be checked by
  hand without trusting any model.
- `generated`: a model produced the expected answer. Kept only so such a case
  can be stored and reported honestly; it is never external validation.

A case with an unreadable file or an unknown provenance is skipped with a
warning rather than silently treated as valid.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError


logger = logging.getLogger(__name__)

CaseProvenance = Literal["human", "specification", "generated"]

EXTERNAL_PROVENANCE: frozenset[str] = frozenset({"human", "specification"})


class FrozenCase(BaseModel):
    """One protected case whose expected answer never leaves the server."""

    case_id: str = Field(min_length=1, max_length=120)
    skill_id: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=500)
    authored_by: CaseProvenance
    source: str | None = Field(default=None, max_length=500)
    expected: dict[str, Any] = Field(min_length=1)

    @property
    def is_external_ground_truth(self) -> bool:
        """Report whether this case can validate a model's own output."""
        return self.authored_by in EXTERNAL_PROVENANCE


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FROZEN_CASES_DIR = PROJECT_ROOT / "data" / "evaluations"


def resolve_frozen_cases_dir(configured: str | None) -> Path:
    """Return the protected set's location, independent of mutable data.

    The frozen set ships with the application so it cannot be replaced by
    whatever a deployment happens to mount at its writable data directory.
    """
    return Path(configured) if configured else DEFAULT_FROZEN_CASES_DIR


def load_frozen_cases(directory: Path | str) -> dict[str, FrozenCase]:
    """Load every readable frozen case, skipping anything malformed."""
    path = Path(directory)
    cases: dict[str, FrozenCase] = {}
    if not path.is_dir():
        logger.info("No frozen evaluation directory at %s", path)
        return cases
    for case_path in sorted(path.glob("*.json")):
        try:
            case = FrozenCase.model_validate_json(
                case_path.read_text(encoding="utf-8"),
            )
        except (OSError, ValidationError, json.JSONDecodeError) as error:
            logger.warning(
                "Skipping unusable frozen case %s: %s",
                case_path.name,
                error,
            )
            continue
        if case.case_id in cases:
            logger.warning(
                "Duplicate frozen case id %s in %s was skipped",
                case.case_id,
                case_path.name,
            )
            continue
        cases[case.case_id] = case
    return cases
