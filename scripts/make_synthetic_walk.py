"""Write a walking clip you can upload, to exercise the flow without a camera.

    python scripts/make_synthetic_walk.py [destination.mp4]

The figure is drawn, not filmed. That makes this useful for one thing and
useless for another, and the difference matters:

- Useful: it exercises the whole measured-pose path for real. Upload it, run a
  measurement, and the observed-motion panel fills with angles that a real
  detector produced from real pixels and that survive both audits.
- Useless: it cannot tell you whether the measurement is *accurate*. The
  angles it recovers disagree with the angles the figure was drawn at by
  double digits, and a fixture whose answer key is written by the same hand
  that drew the question validates nothing.

For that, `data/pose-benchmarks/` needs a case built from a real video of a
real person, with landmarks a person placed by hand.
"""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from tests.support.synthetic_walk import write_walk  # noqa: E402


def main() -> int:
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else PROJECT_ROOT / "synthetic-walk.mp4"
    destination.parent.mkdir(parents=True, exist_ok=True)

    try:
        import cv2  # noqa: F401
    except ImportError:
        print("OpenCV is not installed. Install the 'pose' extra first:")
        print('  pip install -e ".[pose]"')
        return 1

    frames = write_walk(destination, seconds=6.0, fps=30.0)
    if not destination.is_file() or destination.stat().st_size == 0:
        print("This OpenCV build could not write an mp4.")
        return 1

    print(f"Wrote {destination} ({destination.stat().st_size} bytes)")
    print(f"  {len(frames)} frames, 6.0 s at 30 fps, one gait cycle per second")
    print("\nThis exercises the path. It does not validate it: the angles it")
    print("recovers are wrong by double digits, and its answer key is its own.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
