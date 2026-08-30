# APRENDIZ

APRENDIZ teaches software agents and simulated robots procedural tasks from human demonstrations and instructional videos.

The MVP acquires structured procedural knowledge; it does **not** update foundation-model weights. Its first domain is objectively verifiable Peruvian accounting calculations, while the architecture remains domain-independent.

## Objective and workflow

The critical vertical slice is:

```text
Task -> Clarification -> Video -> Procedure -> Examples
     -> Practice -> Evaluation -> Execution on an unseen case
```

APRENDIZ will use instructor examples, cross-video checks, and a frozen human evaluation set to avoid circular self-evaluation.

Before collecting evidence, APRENDIZ asks whether the learned procedure will execute on a computer or through a robot. Users can provide a YouTube URL, upload a video, or request automatic reference discovery. Discovered videos remain candidates until the user reviews their summaries and explicitly approves them. See `docs/product_flow.md` for the complete reviewed flow.

## Current architecture

- `app/agents/`: planned workflow responsibilities; no learning pipeline yet.
- `app/models/`: initial Pydantic contracts for tasks, procedures, skills, training examples, and evaluations.
- `app/services/`: deterministic workflow services plus provider boundaries for Gemini and future GCP services.
- `app/api/`: FastAPI routes for projects, reviewed practice, execution, evaluation, and visible processing sessions.
- `data/`: local development placeholders for skills, examples, and evaluations.
- `tests/frozen_eval/`: protected unseen cases for final validation.
- `docs/`: architecture and learning-model notes.

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

Cloud model calls are disabled by default. `GOOGLE_GENAI_ENABLED=false` and `GOOGLE_GENAI_USE_VERTEXAI=false` keep the current local simulation from generating provider usage. The selected future provider model is configured as `gemini-3.5-flash-lite`.

The controlled first-video route is `POST /api/experiments/video/extract`.
It accepts one approved public YouTube URL, requires explicit cloud-cost
acknowledgement, uses low media resolution and a bounded output, and returns
provider-reported token usage with a typed procedure. The first approved video
experiment completed successfully; its evidence is recorded in
`docs/experiments/2026-08-28-dog-running.md`. See
`docs/video_experiment.md` for local Vertex AI setup and the request contract.

## Run with Docker

With Docker Desktop or Docker Engine installed:

```bash
docker compose up --build
```

Open `http://localhost:8080`. The image does not copy `.env`, local runtimes, test data, user uploads, or credentials. Stop it with `docker compose down`.

The Compose runtime has been verified on Docker Desktop with WSL 2. It runs as
the unprivileged `aprendiz` user, keeps the image filesystem read-only, mounts
bounded temporary storage for runtime data, drops Linux capabilities, enables
`no-new-privileges`, limits process creation, and exposes an application health
check. These controls establish the `application_container` execution boundary;
they do not authorize robot hardware control or unrestricted host access.

## Development status

The responsive product interface now connects both destination paths to real backend behavior. Robot projects start the simulation-only motion session. Computer projects can create a user-reviewed browser plan, show its exact public-domain allowlist, require explicit action and network approval, execute it in containerized Chromium, and display redacted action and network evidence. Approved YouTube sources can now be extracted through a project-bound Vertex call, retained as a versioned procedure awaiting human review, and explicitly approved or rejected without automatic execution. Failed provider attempts are also retained with a safe failure category. Storage remains in-process rather than durable. Automatic procedure-to-action mapping, generalization, durable persistence, and per-user Docker-agent export are **not implemented**.

## Product experience and delivery direction

The web experience uses a bold, modular visual language inspired by the fluid-box interactions of the Be The Buzz reference: oversized typography, high-contrast content blocks, restrained gradients, and purposeful motion. The implementation is responsive, keyboard accessible, dependency-free, compatible with reduced-motion preferences, and fully switchable between Spanish and English for international demonstrations. It adapts the interaction principles rather than reproducing the reference site.

The repository application now has a Dockerfile and Compose configuration for local one-command startup. The final user-facing export target remains a separate, self-contained Docker package for each trained agent. Runtime credentials and user-specific configuration must be supplied outside the image and must never be baked into an image or committed to Git.

## Robot-motion backend vertical slice

APRENDIZ can now acquire an observation-level procedure from a structured robot-motion demonstration. The backend validates timestamps, joint topology, position limits, and maximum joint velocities before creating procedural memory. A rejected demonstration remains visible and cannot be evaluated.

Current endpoints:

- `POST /api/processing/robot-motion`: create the backend-driven local session used by the UI.
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
