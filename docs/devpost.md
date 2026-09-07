# Devpost submission content

Copy into the form. Written to be read by someone who sees fifty of these.

---

## Tagline

Prove which AI-generated video metadata was actually observed, and which was
only asserted.

---

## Inspiration

Video libraries are being labelled by AI at scale, and the model that writes the
label is usually the only witness that the label is true. We wanted the boring,
unglamorous half of that pipeline: the part that checks.

The project started as something else — turning demonstration video into robot
motion — and the honest result of that attempt is what produced this one. When
we asked a vision model for joint angles, it returned confident, well-formed,
completely synthetic numbers: left and right identical in every paired reading,
one confidence value repeated across every sample, every joint tracing a single
smooth rise and fall. The metadata looked like data. It was not evidence. Once
you have written the audit that catches that, you have built a QC tool, and the
QC tool is the useful thing.

## What it does

APRENDIZ audits stored video metadata against the observations it claims to
come from.

- A **library view** shows every analysed asset with its verdict, counted by
  ClickHouse across the whole library rather than one asset at a time.
- An **asset view** shows the counts a verdict was reached from — mirrored-side
  ratio, distinct confidence and visibility values, joints checked for cycles —
  next to a chart of the retained samples. A reader can check the arithmetic
  instead of trusting a word.
- **Prove it** re-runs the audit over the stored samples and reports whether
  the recomputed verdict matches the stored one. It costs nothing, because no
  stage of it calls a model.

## How we built it

- **ClickHouse** holds the samples and answers the audit in SQL. One short clip
  is a couple of hundred timestamped readings; a library is millions. The four
  plausibility checks are window-function SQL — `countIf` for mirrored sides,
  `uniqExact` for uniform confidence, `lagInFrame` over time-ordered series for
  direction reversals.
- **Google ADK** runs the QC pipeline: six deterministic agents, real session
  state, no model call in any of them.
- **Cloud Run** hosts it; **Cloud Storage** holds records and uploads, because
  a stateless container has no disk that survives it; **Secret Manager** holds
  the ClickHouse password.
- **FastAPI + Pydantic** for the contracts, which carry the guarantees as types
  rather than as comments.

## The thing we are proudest of

**The audit is implemented twice and tested for agreement.** The Python
reference runs over one analysis; the SQL runs over a library. Both hand their
counts to one shared `verdict_from_counts`, and a differential test inserts the
same samples, asks both, and asserts they reach the same verdict. If they ever
disagree, the counting is wrong — and it caught a real bug: ClickHouse requires
`lagInFrame`'s default to carry the argument's exact type, `sign()` returns
`Int8`, and the literal `0` is `UInt8`, so the acyclic-joint query had never
run against a real server.

## Challenges

**A governance gate that did not gate.** The approval step sits between a paid
extraction and everything downstream. We built it on ADK's `escalate`, then
measured it: `escalate` does not stop a `SequentialAgent` — every later
sub-agent still runs; `LoopAgent` is what it terminates. A gate that reads as
enforced and is not is the worst failure available, so the composition is
written by hand, the check lives in the stage base class where a new stage
inherits it, and a test pins the framework behaviour that forced the choice.

**Durability that was not durable.** On Cloud Run a writable container
filesystem accepts records and loses them at the next revision, while reporting
itself perfectly durable. The application now distinguishes "a directory
accepted this write" from "this record outlives the container".

## What we learned

Most of the work in a trust tool is refusing to overstate. An absent database
must not render an empty library, because empty reads as clean. A verdict must
not appear without the counts behind it. A pipeline must report the stage it
stopped at rather than a summary that smooths it over. Each of those is a small
decision that a test now holds in place.

## What's next

Sampling new video from inside the console — currently the pipeline only reads
analyses that already exist, because producing one costs a cloud call and we
would not spend a user's money on a button press without asking.

## Try it

- Console: `<service-url>/qc`
- Repository: https://github.com/arkhangio10/analyzer
- Licence: Apache-2.0

## Built with

`python` `fastapi` `pydantic` `clickhouse` `google-adk` `google-cloud-run`
`google-cloud-storage` `secret-manager` `gemini` `playwright`
