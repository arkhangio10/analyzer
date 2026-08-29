# APRENDIZ

APRENDIZ teaches AI agents procedural tasks from human demonstrations and instructional videos.

The MVP acquires structured procedural knowledge; it does **not** update foundation-model weights. Its first domain is objectively verifiable Peruvian accounting calculations, while the architecture remains domain-independent.

## Objective and workflow

The critical vertical slice is:

```text
Task -> Clarification -> Video -> Procedure -> Examples
     -> Practice -> Evaluation -> Execution on an unseen case
```

APRENDIZ will use instructor examples, cross-video checks, and a frozen human evaluation set to avoid circular self-evaluation.

## Current architecture

- `app/agents/`: planned workflow responsibilities; no learning pipeline yet.
- `app/models/`: initial Pydantic contracts for tasks, procedures, skills, training examples, and evaluations.
- `app/services/`: provider boundaries for Gemini and future GCP services.
- `app/api/`: the minimal FastAPI routes.
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

Then visit `/` for project status, `/health` for process health, or `/docs` for the OpenAPI UI. Run tests with `pytest`.

## Development status

Repository initialization is complete: documentation, data contracts, service boundaries, and a minimal API exist. Video analysis, ADK orchestration, procedural extraction, practice, evaluation, persistence, export, and any product UI are **not implemented**.

## MVP milestones

1. Confirm the Python environment and run an ADK hello agent.
2. Process one instructional video with Gemini.
3. Produce structured procedure JSON and instructor-grounded examples.
4. Execute the procedure on a new case.
5. Measure accuracy with trustworthy expected results.
6. Add sophistication only after the vertical slice works.

See `MEMORY.md` for persistent project context and `AGENTS.md` for contribution rules.
