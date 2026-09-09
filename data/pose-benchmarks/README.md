# Human-labelled pose benchmark cases

This directory holds the ground truth for local pose measurement, and nothing
in the learning loop may write to it. A case here says where a person decided
the joints actually are in specific frames of a specific video, and the
measurement is scored against that.

A case is a single JSON file. `authored_by` must be `"person"`; the loader
refuses any other value outright rather than carrying a flag somebody might
forget to read, because a case a model labelled cannot validate a model.

`source_sha256` is the SHA-256 of the video's bytes, which the upload record
already reports. Labels are positions in one particular file, and binding them
to its hash keeps them from silently floating onto a different one.

Coordinates are normalised to the image: `x` is a fraction of the width and
`y` a fraction of the height, both between 0 and 1. That is the space a person
labels in, so it is the space the comparison happens in.

```json
{
  "case_id": "walk-lateral-001",
  "description": "Six frames of one person walking, filmed side on.",
  "authored_by": "person",
  "labelled_by": "who marked these frames",
  "source_sha256": "<64 hex characters, from the upload record>",
  "source_description": "What the video shows, and how it was filmed.",
  "tolerance_normalised": 0.05,
  "timestamp_tolerance_seconds": 0.05,
  "minimum_landmark_pass_ratio": 0.8,
  "frames": [
    {
      "timestamp_seconds": 1.0,
      "landmarks": [
        {"name": "left_hip", "x": 0.51, "y": 0.48},
        {"name": "left_knee", "x": 0.49, "y": 0.68},
        {"name": "left_ankle", "x": 0.52, "y": 0.88}
      ]
    }
  ]
}
```

Landmark names are the ones in `app/services/mediapipe_pose_source.py`. Label
only joints you can actually see; a joint you guess at is worse than one you
leave out, because the measurement is then scored against your guess.

With no case for a video's bytes, a benchmark returns `unvalidated`. That is
not a passing grade and is never reported as one.
