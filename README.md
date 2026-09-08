# APRENDIZ

**Prove which AI-generated video metadata was actually observed, and refuse to
pass on the rest.**

A model asked to describe a video will answer. It will answer confidently when
it measured something and just as confidently when it did not, and downstream
systems cannot tell the two apart. APRENDIZ extracts structured metadata from an
approved video with Gemini on Vertex AI, then audits what came back with
arithmetic and reports a verdict a reader can recompute.

On the first real run against a public walking video, the audit rejected its own
model's output:

| Check | What arrived |
|---|---|
| Left and right independent? | identical in **98 of 98** paired readings |
| Confidence estimated per sample? | one value, `0.7`, across all **196** |
| Visibility judged per frame? | one value, `partial`, across all 196 |
| Gait cyclic? | one rise and fall where ~10 cycles belong |

Two limbs of a walking body do not move identically, and 12 seconds of walking
is not one arc. Higher frame rate bought density, not evidence. The samples were
drawn, not measured, and the system said so instead of forwarding them.

That refusal is the product.

## What is actually real here

Claims in this README are limited to what runs and is tested.

- Gemini on Vertex AI analysing video at a pinned frame rate with bounded
  windows, structured output, and a pre-flight budget guard that refuses an
  over-dense request **before** it is billed.
- A deterministic plausibility audit whose findings carry recomputable counts.
- A human approval gate: nothing is adapted or executed without it.
- A per-agent Docker export: an approved procedure and its evidence become a
  self-contained, reproducible package whose agent is this application with
  the skill baked in and provider calls disabled. Verified on 2026-09-08 by
  building and running a real package with Docker alone.
- Typed contracts that make the guarantees permanent rather than promised in
  prose: `physically_measured` is always false, `approved_for_execution` is
  always false, uploaded video's `sent_to_provider` is always false.
- 187 unit tests, plus 19 browser tests driving real Chrome against a live
  server.

Not real yet, and labelled as such throughout: simulation, hardware execution,
and extraction from uploaded files.

## Running it

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --reload --port 8080
```

Provider calls are **disabled by default**. Set `GOOGLE_GENAI_ENABLED=true` only
for a call you intend to pay for.

```bash
pytest                 # unit suite
pytest tests/browser   # real Chrome against a live server
```

The browser suite is a separate command on purpose: Playwright's synchronous API
holds an event loop open, which breaks `asyncio.run` in anything that follows.

## Deploying

`deploy/deploy.sh` creates the bucket, the service account, the secret and the
Cloud Run service, and `deploy/README.md` explains what each permission is for
and which ones are deliberately withheld. None of it has been run yet: the
scripts are written and syntax-checked, no Google Cloud resource has been
created, and the container has not been built.

One thing that surprised us is worth repeating here. On Cloud Run a writable
container filesystem accepts records and loses them at the next revision, while
reporting itself durable. `/api/status` now separates the two: `durable_storage`
means a store accepted the write, and `records_survive_restart` means the write
outlives the container. Without `GCS_BUCKET` the second is false, and the
service says so at startup.

## Licence

Apache-2.0. See `LICENSE`.

## Objective and workflow

The critical vertical slice is:

```text
Task -> Clarification -> Video -> Procedure -> Examples
     -> Practice -> Evaluation -> Execution on an unseen case
```

APRENDIZ will use instructor examples, cross-video checks, and a frozen human evaluation set to avoid circular self-evaluation.

Before collecting evidence, APRENDIZ asks whether the learned procedure will execute on a computer or through a robot. Users can provide a YouTube URL, upload a video, or request automatic reference discovery. Discovered videos remain candidates until the user reviews their summaries and explicitly approves them. See `docs/product_flow.md` for the complete reviewed flow.

## Current architecture

- `app/agents/`: the QC pipeline as ADK agents, plus boundaries that still raise rather than fabricate a result.
- `app/models/`: initial Pydantic contracts for tasks, procedures, skills, training examples, and evaluations.
- `app/services/`: deterministic workflow services plus provider boundaries for Gemini and future GCP services.
- `app/api/`: FastAPI routes for projects, reviewed practice, execution, evaluation, and visible processing sessions.
- `data/`: local development placeholders for skills, examples, and evaluations.
- `tests/frozen_eval/`: protected unseen cases for final validation.
- `docs/`: architecture and learning-model notes.

### The QC console

`/qc` is a separate surface from the product workspace. It opens a project's
library, lists what has been analysed, and for one asset shows the audit's
counts -- not only its verdict -- next to an SVG chart of the retained samples.
A button recomputes the verdict from those samples and reports each pipeline
stage. It reads only: pressing it repeatedly costs nothing.

Two ways of overstating are ruled out by the contract rather than by the copy.
An absent ClickHouse does not produce an empty library, which would read as a
clean one: the view sets `evidence_available` false, says which part is
missing, and still lists what the local record store holds. And the detail view
carries the counts the verdict was reached from, because the claim is that the
verdict is recomputable and a reader cannot check a verdict.

The robot controls, the setup wizard and the bilingual toggle stay on the
product surface; a browser test asserts they do not appear here.

### The QC pipeline

`app/agents/qc_pipeline.py` runs six ADK agents in order: ingest, extraction,
approval gate, motion, audit, report. It is deterministic and initiates no
provider call, so a run costs nothing; a test asserts as much by failing if the
motion service is ever asked to analyse.

The audit stage is the one that matters. It recomputes the verdict from the
stored samples and compares it to the verdict the stored record claims, and
where ClickHouse is configured it asks the database the same questions
independently. `proven` is true only when the recomputation agrees, so metadata
its own samples contradict is reported as unproven rather than passed along.

The composition is written by hand rather than taken from ADK's
`SequentialAgent`, for a measured reason: a sub-agent that sets `escalate` does
not stop a `SequentialAgent` -- every later sub-agent still runs. A gate built
on it would read as enforced and would not be. `tests/unit/test_qc_pipeline.py`
pins that ADK behaviour, so a future version that changes it will say so.

The gate is checked in the stage base class, so a stage added later inherits it,
and a test walks the pipeline asserting every stage that requires approval does
nothing without it. This is the second line, not the first:
`MotionAnalysisService` already refuses an unapproved procedure at the point the
cloud call would be spent, which is the check that guards the money.

Technology: Python 3.12, Google ADK, Google GenAI/Gemini, FastAPI, Uvicorn, Pydantic, and selected Google Cloud services.

## Local setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

On macOS/Linux, activate with `source .venv/bin/activate` and copy with `cp .env.example .env`.

The editable install registers the `app` package and the `dev` extra (`pytest`), so tests run from any working directory.

Fill only the variables required by the experiment. Never commit `.env`. The main variables are `GOOGLE_API_KEY`, Google Cloud project/location options, optional Firestore and Storage identifiers, `APP_ENV`, and `LOG_LEVEL`.

Run the current skeleton:

```bash
uvicorn app.main:app --reload
```

Then visit `/` for the APRENDIZ interface, `/api/status` for project status, `/health` for process health, or `/docs` for the OpenAPI UI. Run tests with `pytest`.

### Where your work is stored

Project drafts, video procedures, robot-motion sessions and evaluations,
computer practices, sandbox executions, and browser executions are written as
versioned JSON records under `DATA_DIR/records/` (`data/records/` by default).
Browser and file evidence contains hashes, counts, statuses, and redacted
targets rather than typed values or file contents. A pending browser draft that
required redaction reloads blocked and must be created and approved again.
`GET /api/status` reports both `durable_storage` and
`workflow_evidence_durable`; when a record directory cannot be written the
application keeps working in memory and reports that limitation. Under Docker
the records live in the `aprendiz-data` named volume mounted at `/data`, which
survives `docker compose down` and is removed by `docker compose down -v`.

`GET /api/projects` lists retained projects and `GET /api/projects/{project_id}/video-procedures` lists their extractions; the training workspace shows the same list as saved work you can reopen after a reload.

`POST /api/projects/{project_id}/video-procedures/{extraction_id}/adapt` proposes what a destination could run from an approved procedure. It refuses anything a person has not approved, marks each step actionable, needing human detail, or not representable, and names the missing evidence. A plan is a proposal: `approved_for_execution` is always false, and running anything still needs the destination's own approval gate.

The protected evaluation set lives in `data/evaluations/`, ships with the application, and is version-controlled so the answers a model is graded against can be reviewed. Each case declares `authored_by`, and results report whether a pass counts as external validation. See `data/evaluations/README.md` before adding a case.

These files contain user task descriptions and workflow evidence. They are
excluded from Git and must never be committed.

In the interface, `Run local simulation` processes the built-in trajectory and animates it in the source monitor. The animation can be paused, scrubbed, and jumped waypoint by waypoint; it does not autoplay when the browser requests reduced motion. In the training workspace, `Use an example` fills a complete robot setup in one click, the numbered tabs jump back to any visited step, and Enter advances the single-line setup fields.

While a bounded Vertex extraction runs, the status card shows an activity meter, the elapsed time, and a note that one call is in progress; the button carries a busy state. Every review outcome ends with a stated next action: an approved robot procedure offers local motion validation, an approved computer procedure offers the isolated browser rehearsal, and a rejected or failed extraction offers a retry that clears the cost acknowledgement first. Workspace panels scroll their own content, so no control is cut off on short screens.

Cloud model calls are disabled by default. `GOOGLE_GENAI_ENABLED=false` and `GOOGLE_GENAI_USE_VERTEXAI=false` keep the current local simulation from generating provider usage. The general provider model is configured as `gemini-3.5-flash-lite`. Direct YouTube ingestion uses the separately configurable `GOOGLE_GENAI_YOUTUBE_MODEL`, currently `gemini-2.5-flash-lite`, because that exact Vertex path was verified against the walking-video source while the 3.5 models returned internal provider errors.

The controlled first-video route is `POST /api/experiments/video/extract`.
It accepts one approved public YouTube URL, requires explicit cloud-cost
acknowledgement, uses low media resolution and a bounded output, and returns
provider-reported token usage with a typed procedure. The first approved video
experiment completed successfully; its evidence is recorded in
`docs/experiments/2026-08-28-dog-running.md`. See
`docs/video_experiment.md` for local Vertex AI setup and the request contract.
The YouTube-specific model is a compatibility choice, not an automatic retry:
one approved extraction still makes at most one cloud call.

## Run with Docker

With Docker Desktop or Docker Engine installed:

```bash
docker compose up --build
```

Open `http://localhost:8080`. The image does not copy `.env`, local runtimes, test data, user uploads, or credentials. Stop it with `docker compose down`.

If port 8080 is already used by another local service, choose a different host
port without changing the container contract:

```powershell
$env:APP_PORT = "8081"
docker compose up --build
```

The corresponding address is then `http://localhost:8081`.

The test suites intentionally run separately:

```powershell
python -m pytest
python -m pytest tests/browser
```

The first command runs deterministic unit and API coverage. The second starts a
temporary local server and drives an installed Chrome through the real
workspace. The GitHub Actions workflow runs both suites with all provider calls
disabled, then independently builds and checks the hardened Compose runtime.

The Compose runtime has been verified on Docker Desktop with WSL 2. It runs as
the unprivileged `aprendiz` user, keeps the image filesystem read-only, mounts
bounded temporary storage for runtime data, drops Linux capabilities, enables
`no-new-privileges`, limits process creation, and exposes an application health
check. These controls establish the `application_container` execution boundary;
they do not authorize robot hardware control or unrestricted host access.

## Development status

The responsive product interface now connects both destination paths to real backend behavior. Robot projects start the simulation-only motion session. Computer projects can create a user-reviewed browser plan, show its exact public-domain allowlist, require explicit action and network approval, execute it in containerized Chromium, and display redacted action and network evidence. Approved YouTube sources can now be extracted through a project-bound Vertex call, retained as a versioned procedure awaiting human review, and explicitly approved or rejected without automatic execution. Failed provider attempts are also retained with a safe failure category. Workflow evidence is durable under the configured data directory, and adaptation and retarget explanations follow the requested Spanish or English language. Automatic procedure-to-action mapping and generalization are **not implemented**. Per-agent Docker export is implemented and verified; see *Exporting an agent* below.

## Exporting an agent

Once a procedure has been approved through the review gate, the project can be
packaged:

```text
POST /api/projects/{project_id}/agent-packages      {"language": "es" | "en"}
GET  /api/projects/{project_id}/agent-packages/{package_id}/download   -> zip
```

The zip unpacks to one directory. A person who has Docker, and nothing else,
runs `./start.sh` (Linux, macOS) or `.\start.ps1` (Windows): the launcher
copies `.env.example` to `.env` if it is missing, builds the image from
`requirements.lock`, starts Compose, and opens `http://localhost:8080`. The
agent page is served at `/`, the full skill at `/api/skill`, a status at
`/api/agent`, and `/health` answers when it is ready.

What the package contains: `skill/skill.json` (the approved procedure, the
adaptation plan, motion evidence and retarget verdict for a robot destination,
approved rehearsals for a computer destination, lineage, and guarantees),
`manifest.json` with the SHA-256 of every file, `app/` (this application),
`evaluations/` (the frozen cases, copied byte for byte), a `Dockerfile` and
`compose.yaml` that mirror the application image, `requirements.lock`,
`.env.example`, `agent.py`, and the two launchers.

What it refuses to contain: uploaded video, `.env` contents, credentials, and
any workflow record other than the one being exported. What the agent is not
is written as `Literal[False]` fields on the skill — `approved_for_execution`,
`physically_measured`, `hardware_execution_approved`, `model_weights_updated`,
`uploads_included`, `secrets_included`, `provider_calls_at_runtime` — so a
package that claims more fails validation instead of being served.

A package is reproducible: the same records and the same `created_at` produce
the same bytes and the same package id. A download after a restart rebuilds it
from its own extraction and checks the manifest digests; if the application
changed underneath it, the download says so and a new package can be built.

## Product experience and delivery direction

The web experience uses a bold, modular visual language inspired by the fluid-box interactions of the Be The Buzz reference: oversized typography, high-contrast content blocks, restrained gradients, and purposeful motion. The implementation is responsive, keyboard accessible, dependency-free, compatible with reduced-motion preferences, and fully switchable between Spanish and English for international demonstrations. It adapts the interaction principles rather than reproducing the reference site.

The repository application now has a Dockerfile and Compose configuration for local one-command startup. The final user-facing export target remains a separate, self-contained Docker package for each trained agent. Runtime credentials and user-specific configuration must be supplied outside the image and must never be baked into an image or committed to Git.

## Robot-motion backend vertical slice

APRENDIZ can now acquire an observation-level procedure from a structured robot-motion demonstration. The backend validates timestamps, joint topology, position limits, and maximum joint velocities before creating procedural memory. A rejected demonstration remains visible and cannot be evaluated.

Current endpoints:

- `POST /api/processing/robot-motion`: create the backend-driven local session used by the UI. The response carries a `motion_preview` describing each joint's drawing role and schematic link proportion plus the validated waypoints, so the interface can animate the demonstration. It reports `physics_simulated: false` and `collision_checked: false`; it is a drawing of stored angles, not a simulator.
- `GET /api/processing/robot-motion/{session_id}`: poll progress and receive final procedure/evaluation evidence.
- `POST /api/training/robot-motion`: validate a simulated demonstration and extract an inspectable procedure.
- `GET /api/training/robot-motion/{session_id}`: retrieve the training outcome.
- `POST /api/training/robot-motion/{session_id}/evaluate`: compare candidate replay data with the instructor demonstration.

Project and source-intake endpoints:

- `POST /api/projects`: clarify a task and create a safe computer or robot destination contract.
- `GET /api/projects/{project_id}`: retrieve the local project draft.
- `POST /api/projects/{project_id}/computer-practices`: validate and store a user-reviewed browser plan without executing it.
- `GET /api/projects/{project_id}/computer-practices/{practice_id}`: retrieve the plan, approval state, and latest execution reference.
- `POST /api/projects/{project_id}/computer-practices/{practice_id}/execute`: execute the stored plan only after explicit action-review and network acknowledgements.
- `POST /api/projects/{project_id}/video-procedures/extract`: process one explicitly approved YouTube source and retain success or safe failure evidence under the project.
- `GET /api/projects/{project_id}/video-procedures/{extraction_id}`: retrieve the structured procedure, provider usage, failure category, and review state.
- `POST /api/projects/{project_id}/video-procedures/{extraction_id}/review`: approve or reject a successful procedure without executing it.
- `POST /api/projects/{project_id}/video-procedures/{extraction_id}/adapt`: report how much of an approved procedure a destination could run, naming the evidence each blocked step is missing; it executes nothing.
- `POST /api/projects/{project_id}/video-procedures/{extraction_id}/motion-analysis`: spend one acknowledged cloud call sampling the already approved source at an explicit frame rate, and return timestamped joint angles with a plausibility audit. A request whose density would overflow the response budget is refused before any call is made.
- `GET /api/projects/{project_id}/video-procedures/{extraction_id}/motion-analysis`: retrieve the retained analysis without spending anything.
- `GET /api/projects/{project_id}/video-procedures/history/versions`: list every retained procedure version and diff the two most recent.
- `GET /api/projects/{project_id}/video-procedures/history/diff/{from}/{to}`: report what changed between two versions without altering either.
- `GET /api/projects/{project_id}/video-procedures/history/reconciliation`: compare every approved procedure and report how many distinct videos actually backed them.
- `POST /api/projects/{project_id}/uploads`: keep one video on this machine. It is never sent to a provider, and the record says so.
- `GET /api/projects/{project_id}/uploads`: list what this machine holds, with each file's size and hash.
- `DELETE /api/projects/{project_id}/uploads/{upload_id}`: delete one upload from this machine.
- `POST /api/sources/search`: return bounded YouTube candidates; it never approves or analyzes them automatically.
- `POST /api/sources/search/{search_id}/approve`: record the user's explicit reference selection without starting video analysis.
- `POST /api/learning/reconcile`: compare two or more approved procedures and expose agreement, conflict, and uncertainty.
- `POST /api/learning/evaluate/frozen`: score a candidate against a server-side protected case without returning its expected answer.
- `POST /api/execution/computer/validate`: validate browser, text, and sandboxed file actions; arbitrary shell actions are not accepted.
- `POST /api/execution/computer/execute`: execute bounded read/write actions under `.runtime/computer_sandboxes`; browser actions remain blocked on this file-only endpoint.
- `GET /api/execution/computer/executions/{execution_id}`: retrieve redacted action evidence, hashes, and byte counts without returning file contents.
- `POST /api/execution/computer/browser/execute`: run up to 25 acknowledged Chromium actions against an exact list of approved public hosts inside the application container.
- `GET /api/execution/computer/browser/executions/{execution_id}`: retrieve redacted browser evidence without typed values, page content, URL queries, or fragments.
- `POST /api/robots/profiles/arp-1/import/urdf`: normalize a bounded URDF XML document into the internal APRENDIZ Robot Profile v1.
- `POST /api/robots/profiles/arp-1/motion-contract`: map compatible revolute joints from ARP-1 radians into the current degree-based motion trainer.

Motion analysis reads an approved video as movement rather than as
instruction, because a prose step can never become a trajectory. It pins an
explicit frame rate over a bounded window, and it treats what comes back as an
estimate under suspicion: `measurement_method` is permanently
`vision_model_estimate`, `physically_measured` is permanently false, and a
deterministic audit checks the numbers before anything downstream may use them.

The audit is arithmetic, not judgement. It counts how often left and right
carry the same angle, how many distinct confidence and visibility values were
reported, and whether a joint that swings tens of degrees ever reverses more
than once. Real bipedal gait is antiphase and cyclic, so any two of those
failing means the samples were drawn rather than measured. A failed audit can
never make an adapted step actionable, and the retarget verdict says so with
the counts a reader can recompute.

Running this against the approved 257-second walking video returned 196 samples
across 49 timestamps at a confirmed 4.0 fps, and the audit rejected all of them:
left and right were identical in 98 of 98 paired readings, all 196 samples
reported the same confidence and the same visibility, and every joint traced a
single rise and fall across the window. Higher frame rate produced denser
output, not better evidence. That result is the current honest answer to whether
video can become a robot trajectory today.

Uploaded video is never handed to a model. The contract makes that permanent
rather than promising it in prose: `sent_to_provider` is always false, and
`analysis_available` is always false, because extraction still accepts only a
public YouTube URL. An upload can therefore be kept and verified by its
SHA-256, but the interface never implies it can be turned into a procedure yet.

Where the file is kept is a separate claim, and it is one the code has to earn
rather than assert. `storage_location` reports `this_machine` for a mounted
directory and `your_bucket` for Cloud Storage in the operator's own project. It
used to be `stored_locally`, permanently true, which stopped being honest the
moment the target was a stateless container with no disk to keep anything on.
Both destinations share one implementation of what is accepted, how the stream
is capped, and what the record claims, so the guarantees cannot weaken on the
way to the cloud; only the bytes' destination differs.

Reconciliation reports something the reconciler cannot know by itself: how many
distinct videos actually backed the procedures being compared. Two readings of
the same source agreeing means the model repeated itself, so `is_cross_source`
stays false until a second, different source has been approved.

Tests run in two commands. `pytest` runs the unit suite. `pytest tests/browser`
drives a real Chrome against a live server seeded with realistic records, and
covers what used to be checked by eye: translation, panel overflow, the cost
acknowledgement gate, the audit verdict, version history, and the upload flow.
The browser suite is separate because Playwright's synchronous API holds an
event loop open, which breaks `asyncio.run` in any test that follows it.

The local filesystem sandbox requires explicit acknowledgement, rejects absolute
or traversing paths, limits seeded inputs to 256 KiB and individual writes to
64 KiB, never resolves environment secrets, and reports zero external host and
cloud actions. On the host it reports the `managed_local_directory` boundary;
under the verified Compose service it reports `application_container` and gains
the container controls described above.

The browser adapter is disabled for direct host execution and enabled by the
Compose service. Every run requires explicit network acknowledgement and an
exact hostname allowlist. It rejects private, loopback, link-local, and reserved
IP literals; resolves allowed hostnames only to public addresses; intercepts
browser requests; blocks unapproved destinations and redirects; limits each
action timeout; disables downloads, service workers, WebSockets, and WebRTC;
and never resolves
environment values or supports sensitive form fields. It returns URL paths,
status, request counts, and page-title hashes instead of page or typed content.
This is a bounded browser vertical slice, not authorization for arbitrary web or
desktop automation. Verification evidence is recorded in
`docs/experiments/2026-08-29-container-browser.md`.

The bilingual UI exposes the browser adapter through a separate rehearsal panel
only after a sufficiently clear computer project exists. It derives the exact
approved host from the user-entered target URL, previews every action, requires
a review checkbox, and renders execution stages, action totals, allowed and
blocked network requests, and cloud-call count. Sample values stay in the
reviewed plan but are not returned in browser execution evidence.

For a direct or approved YouTube source, the UI also exposes a separate Vertex
extraction panel. It requires a fresh cost acknowledgement, displays the exact
source, token count, elapsed time, cloud-call count, timestamped steps, rules,
exceptions, examples, and uncertainties, and records an approve/reject decision.
Approval changes review state only; it does not start destination execution.

ARP-1 is an internal APRENDIZ interoperability contract, not an external robot
standard. The initial importer supports URDF only, rejects DTD/entity
declarations, preserves source units, verifies one kinematic-tree root and link
references, and requires position and velocity limits for movable joints. It
recommends Gazebo or MuJoCo without claiming either simulator is installed.
Hardware execution always remains disabled.

Automatic discovery is disabled by default. Enable YouTube Data API v3 in the
Google Cloud project, create a restricted API key, and set
`YOUTUBE_SEARCH_ENABLED=true` plus `YOUTUBE_API_KEY` only in the untracked
`.env` file. The UI requests three results per search. Direct URLs and local
file selection remain available without this integration.

This slice is simulation-only and cannot send commands to physical hardware. Its evaluation measures imitation against instructor-provided joint trajectories; it does not yet validate collision avoidance, robot dynamics, generalization, or real-world safety.

## MVP milestones

1. Keep the connected local robot-motion session stable and inspectable.
2. Run an ADK hello agent behind the provider boundary.
3. Process one instructional video with Gemini 3.5 Flash Lite after credit coverage is verified.
4. Produce project-bound structured procedure JSON and instructor-grounded examples. The guarded workflow and review gate are implemented; successful extraction must still be verified for the current walking video.
5. Execute and measure one genuinely unseen case.
6. Add persistence and per-agent Docker export only after the vertical slice works.

See `MEMORY.md` for persistent project context and `AGENTS.md` for contribution rules.
