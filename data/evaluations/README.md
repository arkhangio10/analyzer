# Frozen evaluation set

These cases are the project's protection against circular self-grading. The
learning loop may read them through `EvaluatorAgent`; nothing may write here.

One JSON file per case:

```json
{
  "case_id": "unique-id",
  "skill_id": "what is being evaluated",
  "description": "why this case is a fair test, and how the answer was decided",
  "authored_by": "human | specification | generated",
  "source": "optional pointer to the evidence behind the expected answer",
  "expected": { "field": "value" }
}
```

`authored_by` decides whether a pass counts as external validation:

- **human** — a person decided the expected result, usually after watching the
  source themselves. This is the only provenance that validates a procedure
  extracted from video. **APRENDIZ cannot author these for you**: a model that
  writes its own answer key proves nothing.
- **specification** — the expected result follows deterministically from a
  documented rule, such as a stated joint velocity limit, and any reviewer can
  recompute it by hand. The two shipped cases are of this kind.
- **generated** — a model produced the expected answer. Stored and reported
  honestly, but `counts_as_external_validation` is false and it must never be
  presented as proof of learning.

## Writing a case for the walking video

Watch the approved source yourself, decide what a correct procedure must
contain, and record that judgement here with `authored_by: "human"` and a
`source` naming the video and timestamps. Do not copy the extracted procedure
into the expected answer: grading the model against its own output measures
nothing.
