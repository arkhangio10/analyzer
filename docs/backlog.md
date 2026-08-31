# APRENDIZ execution backlog

This is the ordered implementation backlog. It records gates and acceptance
evidence so a task cannot be called complete because code exists alone.

Status values are `done`, `ready`, `human_gate`, `blocked`, and `deferred`.
Provider calls remain disabled by default. A source approval and cost
acknowledgement authorize one bounded call only.

## P0 - Reproducible baseline

| ID | Status | Work | Acceptance evidence |
| --- | --- | --- | --- |
| P0.1 | done | Verify the host suites | 175 unit tests and 19 browser tests pass in separate processes. |
| P0.2 | done | Verify the hardened Compose runtime | Image builds; UID/GID is 10001; root is read-only; frozen cases ship in the image; `durable_storage` is true; a project survives a container restart. |
| P0.3 | done | Run checks continuously | GitHub Actions run `33354722460` passed the Python and hardened-container jobs with every provider integration disabled. |
| P0.4 | done | Integrate `motion-evidence` | `main` was advanced without rewriting history and includes the reviewed work through commit `6479644`. |

## P1 - External evidence for the walking procedure

| ID | Status | Work | Acceptance evidence |
| --- | --- | --- | --- |
| P1.1 | human_gate | Write three to five expected outcomes for the approved walking procedure | Each frozen case is authored by a person, lives outside writable runtime data, and reports `counts_as_external_validation=true`. |
| P1.2 | human_gate | Name and approve a second walking-video URL | The source is distinct from `-fD2TSL2s7I`; approval does not imply a later source or call. |
| P1.3 | blocked | Extract and reconcile the second source | After P1.2 and a fresh cost acknowledgement, exactly one call is retained and reconciliation reports `is_cross_source=true` or explains why it cannot. |
| P1.4 | blocked | Measure the reviewed result against frozen cases | The score exposes passes, failures, answer provenance, and external-validation status without returning protected answers. |

Automatic YouTube search is optional. A direct approved URL unblocks P1.2, so
creating an API key is not on the critical path.

## P2 - Narrow computer learning loop

| ID | Status | Work | Acceptance evidence |
| --- | --- | --- | --- |
| P2.1 | human_gate | Choose one measurable computer task and controlled destination | The task has known inputs, outputs, allowed actions, and a human or specification answer key. |
| P2.2 | blocked | Convert an approved procedure into an inert browser-practice draft | Every action and exact host are visible; the draft cannot execute and never implies approval. |
| P2.3 | blocked | Generate progressive variations | Variations are admitted only when an external evaluator exists; model-authored answers never count as proof. |
| P2.4 | blocked | Add bounded reflection, correction, and retry | A failure creates a new procedure version, preserves the old version, shows a diff, limits retries, and requires renewed human approval. |
| P2.5 | done | Persist remaining workflow evidence | Robot sessions and evaluations, computer practices, sandbox executions, and browser executions reload from schema-versioned records; typed values, URL queries, and file contents do not reach those evidence files. |
| P2.6 | blocked | Prove one unseen case end to end | The protected expected result is external to the learning loop and the complete execution evidence is retained. |

## P3 - Robot evidence and simulation

The current dense Gemini joint samples failed their deterministic plausibility
audit. More frames or another prose extraction do not make them measurements.

| ID | Status | Work | Acceptance evidence |
| --- | --- | --- | --- |
| P3.1 | human_gate | Select the target robot or explicitly approve a generic fixture | Exact model, supported description, joint limits, and intended simulator scope are recorded. |
| P3.2 | blocked | Benchmark a measurable pose or motion source | Estimates are compared with human-labelled landmarks; fabricated symmetry, uniform confidence, impossible ranges, and missing cycles fail closed. |
| P3.3 | blocked | Select and integrate a simulator | MuJoCo, Gazebo, or another candidate is selected by asset support, headless execution, contacts, dynamics, licence, and CI evidence rather than installation convenience. |
| P3.4 | blocked | Add collision and kinematic checks | The first offending link, joint, and waypoint are retained; a pass never claims dynamics or stability. |
| P3.5 | blocked | Add dynamics and contact validation | Torque, acceleration, ground contact, balance, and stability evidence are explicit. |
| P3.6 | deferred | Define the hardware-adapter safety contract | Hardware commands remain impossible; the contract covers limits, authentication, emergency stop, dead-man behaviour, monitoring, and operator approval. |

## P4 - Delivery and optional cloud exposure

| ID | Status | Work | Acceptance evidence |
| --- | --- | --- | --- |
| P4.1 | blocked | Build the per-agent Docker export | Begins only after P2.6 or an equivalent validated slice; secrets stay runtime-only; the package has a launcher, health check, procedure version, evaluation evidence, and reproducible build. |
| P4.2 | deferred | Enable automatic YouTube discovery | The key is restricted to YouTube Data API, stays outside Git, and has quota and budget controls. |
| P4.3 | deferred | Replace the direct-YouTube compatibility model | A bounded approved regression proves the replacement before `gemini-2.5-flash-lite` is retired; there is no paid automatic fallback. |
| P4.4 | deferred | Deploy to Cloud Run | Requires explicit project, region, public/private access, persistent storage, secrets, and budget decisions. |
| P4.5 | deferred | Add authentication and per-user isolation | Begins only if a multi-user deployment is approved and its ownership model is defined. |

## Cross-cutting work

- Done: adaptation and retarget explanations use the requested Spanish or
  English language; changing the interface language refreshes adaptation text.
- Keep provider, browser, simulator, and hardware boundaries explicit.
- Preserve failures and uncertainty in every result.
- Never mutate frozen expected answers from a learning or retry path.
- Never add credentials, user media, private records, or authorship metadata to
  Git or exported images.
