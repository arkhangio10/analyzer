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
- `app/services/`: provider boundaries for Gemini and future GCP services.
- `app/api/`: FastAPI routes for health, robot-motion training, evaluation, and visible processing sessions.
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

## Development status

The first responsive product interface and the simulation-only robot vertical slice are connected. Starting a processing session from the bilingual UI now creates backend state, polls five real lifecycle stages, exposes safety-checked procedural metrics, and reports a reference-replay evaluation. The response explicitly identifies `local_simulation`, reports zero cloud calls, and does not pretend to inspect the selected video. The guarded Gemini endpoint has successfully processed one approved public video and returned a typed procedure with token evidence. ADK orchestration, persistence, generalization, frozen validation, and per-user Docker-agent export are **not implemented**.

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

This slice is simulation-only and cannot send commands to physical hardware. Its evaluation measures imitation against instructor-provided joint trajectories; it does not yet validate collision avoidance, robot dynamics, generalization, or real-world safety.

## MVP milestones

1. Keep the connected local robot-motion session stable and inspectable.
2. Run an ADK hello agent behind the provider boundary.
3. Process one instructional video with Gemini 3.5 Flash Lite after credit coverage is verified.
4. Produce structured procedure JSON and instructor-grounded examples.
5. Execute and measure one genuinely unseen case.
6. Add persistence and per-agent Docker export only after the vertical slice works.

See `MEMORY.md` for persistent project context and `AGENTS.md` for contribution rules.
