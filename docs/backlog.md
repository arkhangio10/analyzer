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
audit twice: human walking on 2026-08-30 and quadrupedal locomotion on
2026-09-07, on different videos and different kinematic chains. More frames or
another prose extraction do not make them measurements. P3.2 is therefore the
blocker for this whole section, ahead of P3.1: a joint map onto a robot would
only connect hardware to numbers that are not observations.

| ID | Status | Work | Acceptance evidence |
| --- | --- | --- | --- |
| P3.1 | human_gate | Select the target robot or explicitly approve a generic fixture | Exact model, supported description, joint limits, and intended simulator scope are recorded. |
| P3.2 | ready | Benchmark a measurable pose or motion source | Built on 2026-09-09, narrowed to human demonstration by owner decision. A pose model runs locally over an uploaded file's frames (`POST .../uploads/{id}/pose-measurement`, zero cloud calls, `sent_to_provider` false) and joint angles are computed from its landmarks by `pose_landmark_geometry`. All four named failure classes fail closed: symmetry, uniform confidence and missing cycles through the existing `audit_motion_samples`, and impossible ranges through the new `human_range_audit`, which the 2026-08-30 run needed and did not have. `pose_benchmark` compares landmarks against a human-labelled case bound to the video's SHA-256, and returns `unvalidated` -- never a pass -- when no case exists. 76 tests. The model is now fetched and pinned (`pose_landmarker_lite`, 5,777,746 bytes, sha256 `59929e1d...d574a`) and five integration tests run it for real: it loads, a video decodes, the requested sampling rate is what is actually read, and **it returns nothing for three seconds of random noise** rather than inventing a body. **One human gate remains before this is `done`:** no labelled case has been authored, so the benchmark has never run against real ground truth, and no real person has been measured. |
| P3.3 | blocked | Select and integrate a simulator | MuJoCo, Gazebo, or another candidate is selected by asset support, headless execution, contacts, dynamics, licence, and CI evidence rather than installation convenience. |
| P3.4 | blocked | Add collision and kinematic checks | The first offending link, joint, and waypoint are retained; a pass never claims dynamics or stability. |
| P3.5 | blocked | Add dynamics and contact validation | Torque, acceleration, ground contact, balance, and stability evidence are explicit. |
| P3.6 | deferred | Define the hardware-adapter safety contract | Hardware commands remain impossible; the contract covers limits, authentication, emergency stop, dead-man behaviour, monitoring, and operator approval. |

## P4 - Delivery and optional cloud exposure

| ID | Status | Work | Acceptance evidence |
| --- | --- | --- | --- |
| P4.1 | done | Build the per-agent Docker export | Built ahead of the P2.6 gate by owner decision on 2026-09-08. Verified the same day on a real package: `start.sh` built the image from `requirements.lock` and started Compose; `/health` answered in 4 s; `/api/skill` served the baked procedure (v1, 6 steps) with every guarantee false; the container ran as UID 10001 on a read-only filesystem with no `.env` and both frozen cases present; secrets stay runtime-only. |
| P4.2 | deferred | Enable automatic YouTube discovery | The key is restricted to YouTube Data API, stays outside Git, and has quota and budget controls. |
| P4.3 | deferred | Replace the direct-YouTube compatibility model | A bounded approved regression proves the replacement before `gemini-2.5-flash-lite` is retired; there is no paid automatic fallback. |
| P4.4 | done | Deploy to Cloud Run | Every decision it was deferred on has been made and verified on 2026-09-09: project `analyzer-robotics-ark10`, region `us-central1`, public access, records durable in Cloud Storage (`/api/status` reports `durable_storage: true`), the spend token and ClickHouse password injected from Secret Manager, and spending capped in the application at 20.00 PEN rather than by a GCP budget, which only alerts. Serving revision `aprendiz-00013-sqt`. |
| P4.5 | deferred | Add authentication and per-user isolation | Begins only if a multi-user deployment is approved and its ownership model is defined. |

## Cross-cutting work

- Done: adaptation and retarget explanations use the requested Spanish or
  English language; changing the interface language refreshes adaptation text.
- Keep provider, browser, simulator, and hardware boundaries explicit.
- Preserve failures and uncertainty in every result.
- Never mutate frozen expected answers from a learning or retry path.
- Never add credentials, user media, private records, or authorship metadata to
  Git or exported images.
