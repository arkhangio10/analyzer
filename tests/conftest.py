"""Keep the suite from writing workflow records into the repository.

The application persists projects and extractions under its configured data
directory. Tests import the real service graph, so without this redirect every
run would leave records in `data/records/`. The variable is set before any test
module imports the application, because the service graph reads it at import
time.
"""

import os
import shutil
import tempfile
from pathlib import Path


_TEST_DATA_DIR = Path(tempfile.mkdtemp(prefix="aprendiz-tests-"))
os.environ["DATA_DIR"] = str(_TEST_DATA_DIR)


def pytest_sessionfinish(session, exitstatus) -> None:  # noqa: ANN001, ARG001
    """Remove the temporary data directory created for this run."""
    shutil.rmtree(_TEST_DATA_DIR, ignore_errors=True)
