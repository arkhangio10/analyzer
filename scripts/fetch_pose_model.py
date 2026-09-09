"""Fetch the pose model once, against a pinned checksum.

The model is a build input, not a runtime dependency. Downloading it during a
measurement would put a network call in the middle of something that is
otherwise entirely local, and would let two containers measure the same video
with two different sets of weights. So it is fetched here, verified, and
written to disk; `mediapipe_pose_source` reports its absence rather than
reaching for it.

Run it directly:

    python scripts/fetch_pose_model.py

The expected digest is empty until somebody runs this once, records the digest
the download actually produced, and commits it. Until then the script refuses
to install anything: an unpinned model is a different measurement every time,
and the whole point of this path is that it is reproducible.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESTINATION = PROJECT_ROOT / "models" / "pose_landmarker_lite.task"

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
    "pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
)

# Fill this in with the digest printed on the first successful run, then commit
# it. An empty value means the model has never been pinned and the script will
# not install one.
EXPECTED_SHA256 = ""

MAX_BYTES = 64 * 1024 * 1024


def download(url: str, into: Path) -> str:
    """Download to a temporary file and return its SHA-256."""
    digest = hashlib.sha256()
    with urllib.request.urlopen(url, timeout=120) as response:  # noqa: S310
        total = 0
        with open(into, "wb") as handle:
            while chunk := response.read(1024 * 256):
                total += len(chunk)
                if total > MAX_BYTES:
                    raise RuntimeError(
                        f"The download exceeded {MAX_BYTES} bytes and was stopped."
                    )
                digest.update(chunk)
                handle.write(chunk)
    return digest.hexdigest()


def main() -> int:
    destination = DEFAULT_DESTINATION
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as work:
        staged = Path(work) / destination.name
        print(f"Downloading {MODEL_URL}")
        actual = download(MODEL_URL, staged)
        size = staged.stat().st_size
        print(f"  {size} bytes")
        print(f"  sha256 {actual}")

        if not EXPECTED_SHA256:
            print(
                "\nEXPECTED_SHA256 is empty, so nothing was installed. If the "
                "digest above is the one you intend to pin, put it in this "
                "script, commit it, and run this again."
            )
            return 2
        if actual != EXPECTED_SHA256:
            print(
                f"\nDigest mismatch.\n  expected {EXPECTED_SHA256}\n  actual   {actual}"
                "\nNothing was installed."
            )
            return 1

        shutil.move(str(staged), str(destination))

    print(f"\nInstalled {destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
