# Demo script — 3 minutes

For you to record. Timings are generous; the whole thing runs under three
minutes at a normal speaking pace.

The one rule: **do not claim anything the screen is not showing.** The entire
point of the project is that a verdict is checkable, so a demo that asserts
more than it demonstrates undercuts itself.

---

## 0:00 – 0:25 · The problem

> Video libraries are being labelled by AI at scale. A model watches a clip and
> writes metadata: what moved, how fast, which joints. That metadata gets
> stored, indexed, and trusted.
>
> Nobody checks it. The model that produced the label is also the only witness
> that the label is true.
>
> APRENDIZ is a QC agent for that problem. It asks one question about every
> asset: was this metadata actually observed, or was it just asserted?

**On screen:** the `/qc` console, empty, with the header line visible.

---

## 0:25 – 0:55 · The library

> Here is a project's library. Each row is one analysis: a verdict, the source,
> how many samples came back, how many joints.
>
> These verdict counts are not computed by the application. They come from
> ClickHouse, which is holding the samples — one twelve-second clip at four
> frames a second is already a couple of hundred timestamped readings, and a
> library is millions. That is a columnar workload, so it lives in a columnar
> database.

**On screen:** type the project id, open the library. Point at the verdict
table and the note above it saying where the numbers came from.

*If ClickHouse is unreachable when you record, read the note the console shows
instead — it says the library-scale view is missing and lists what the local
store holds. Do not skip past it. An honest degradation is worth showing.*

---

## 0:55 – 1:40 · The counts, not the verdict

> Open one asset. This one is labelled `not_evidence`.
>
> The console does not just show me that word. It shows the numbers the word
> came from: left and right were identical in every paired reading. All the
> samples reported the same confidence and the same visibility. Every joint
> traced a single rise and fall — no cycles, in what is supposed to be walking.
>
> And here are the samples themselves, plotted. You can see the curves are
> drawn, not observed.
>
> That is the difference between being told a verdict and being able to check
> one.

**On screen:** click Inspect. Scroll the counts table slowly. Let the chart sit
on screen for a beat — the shape is the argument.

---

## 1:40 – 2:20 · Prove it

> Now the part that matters. This button recomputes the verdict from the stored
> samples and compares it to what the record claims.
>
> Six agents run in order, built on Google's Agent Development Kit: ingest,
> extraction, an approval gate, motion, audit, report. It costs nothing — no
> stage calls a model. It only reads what is already stored.
>
> The audit recomputed the same verdict the record claims. And where ClickHouse
> is configured, the database answers the same questions independently, in SQL,
> over the same samples. Two implementations of one rule, agreeing.
>
> That agreement is asserted by a test in the repository, not just here. If the
> SQL and the Python ever disagree, the build fails.

**On screen:** press the button. Let the stage list render. Point at the
headline.

---

## 2:20 – 2:50 · The gate

> One more thing. This asset was approved by a person. If it had not been, the
> pipeline stops here — at the gate — and nothing downstream runs.
>
> Not "runs and reports blocked". Does not run. That distinction cost me a
> design change: the framework's own sequential agent does not actually stop
> when a step escalates, so the composition is written by hand and a test pins
> the framework behaviour that forced it.

**On screen:** either an unapproved asset showing the gate stage blocked with
no audit stage after it, or the test in `test_qc_pipeline.py`.

---

## 2:50 – 3:00 · Close

> Metadata that survives recomputation was observed. Metadata that does not is
> reported as unproven — not quietly passed along.
>
> That is the whole product.

---

## Do not say

- That any of this validates physical safety. It does not, and the code says so
  in several places.
- That video has been turned into a robot trajectory. It has not; the honest
  finding is the opposite, and it is in the README.
- That the pipeline "analyses" video live. It reads stored analyses. Producing
  a new one costs a cloud call, which the pipeline deliberately never spends.
