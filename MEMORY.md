# APRENDIZ Persistent Project Memory

Read this document before making significant architectural changes. It records the project's current truth. Preserve historical decisions in the Decision Log, but update the other sections when reality changes.

## Project Identity

**Name:** APRENDIZ

## Mission

Teach AI agents procedural tasks from human demonstrations and instructional videos.

## Product Vision

Enable a non-programmer to explain what an agent should learn, provide demonstrations, let APRENDIZ practice and validate the procedure, see honest performance, and ultimately obtain a usable runnable agent.

The first hackathon domain is Peruvian accounting calculations such as IGV, net income, CTS, gratificaciones, and simple bank reconciliation. This narrow domain gives objective numerical outcomes, but the architecture must remain generic.

## Core Principle

The MVP does not modify foundation-model weights. It is not fine-tuning, LoRA, or QLoRA.

Learning means automated procedural knowledge acquisition from unstructured video, with externally anchored self-evaluation. The product builds and improves versioned, structured procedural memory containing objectives, inputs, outputs, ordered steps, rules, conditions, exceptions, examples, sources, uncertainty, and evaluation evidence.

Never simplify the system to "video -> prompt".

## User Flow

1. The user assigns a task.
2. `TaskClarifierAgent` forms a task definition: name, objective, expected inputs and outputs, constraints, tools, success criteria, and known exceptions.
3. If information is incomplete or ambiguous, APRENDIZ asks contextual clarification questions, updates its understanding, and repeats until sufficiently clear.
4. The user chooses YouTube instructional videos or uploaded training videos.
5. The system understands demonstrations and extracts structured procedural knowledge: objective, inputs, outputs, steps, rules, conditions, exceptions, examples, and expected results.
6. APRENDIZ creates a versioned Skill/Procedure.
7. It imitates demonstrated examples, practices progressively varied exercises, and evaluates results against trustworthy anchors.
8. On failure, it analyzes the failure, reflects, updates procedural memory, and retries. Failures remain visible.
9. It performs generalization tests and then a final blind validation against a frozen unseen set that learning cannot modify.
10. The user sees measured performance and, in a later milestone, can export a runnable agent package.

Critical vertical slice:

```text
TASK -> CLARIFICATION -> VIDEO -> PROCEDURE -> EXAMPLES
     -> PRACTICE -> EVALUATION -> EXECUTION ON UNSEEN CASE
```

## Learning Philosophy

- **Observe:** video becomes an interpreted demonstration.
- **Understand:** the demonstration becomes a structured procedure.
- **Imitate:** execute instructor examples or near-identical cases.
- **Practice:** solve variations with increasing difficulty.
- **Feedback:** compare actual and expected outcomes.
- **Reflect:** identify why a failure occurred.
- **Correct:** update procedural knowledge, not model weights.
- **Repeat:** retry with the corrected procedure.
- **Generalize:** solve new cases requiring the same underlying procedure.
- **Validate:** measure performance on protected unseen cases.

Future learning levels are: Level 0 Observation, Level 1 Imitation, Level 2 Variation, Level 3 Generalization, Level 4 Edge Cases, and Level 5 Blind Validation.

## Evaluation Philosophy

Avoid circular self-evaluation. A model must not merely create its own test, answer it, and declare success.

1. **Instructor ground truth:** solved examples from tutorials provide expected answers external to APRENDIZ.
2. **Cross-video validation:** a procedure extracted from one video should be tested with examples from another; contradictions must appear as uncertainty.
3. **Frozen human evaluation set:** manually maintained unseen cases are immutable to the learning loop and provide final validation.
4. **Transparent uncertainty:** report disagreement, missing evidence, and failures honestly; never manufacture confidence.

## Planned Agents

- **RootAgent:** coordinate the complete workflow and state transitions.
- **TaskClarifierAgent:** determine whether the task contract is clear and ask useful questions when it is not.
- **VideoInstructorAgent:** understand what a human demonstrates in a YouTube URL or uploaded video.
- **ProcedureExtractorAgent:** produce structured procedural knowledge from understood demonstrations.
- **PracticeAgent:** create exercises and task variations with progressive difficulty.
- **EvaluatorAgent:** compare executions with instructor, cross-video, or frozen expected outcomes.
- **ReconcilerAgent:** compare multiple sources and surface contradiction, consensus, and uncertainty.
- **ExecutorAgent:** apply a validated stored procedure to a new task.

The files for these responsibilities currently define boundaries only. They do not implement agent behavior.

## Technology

- Python 3.12
- Google ADK
- Google Gemini through the Google GenAI SDK
- FastAPI and Uvicorn
- Pydantic, pydantic-settings, and python-dotenv
- httpx and python-multipart
- Google Cloud: planned Cloud Run, Firestore, Pub/Sub, and Cloud Storage

Prefer passing supported YouTube URLs directly to Gemini. Do not add a downloader or automatic video download by default. Uploaded files are the fallback source.

Do not add TensorFlow, PyTorch, Hugging Face Transformers, LangChain, or another major framework without a demonstrated architectural need.

## Current Priorities

1. Environment works. **Done** — see Current Status.
2. ADK hello agent works.
3. Gemini can process one instructional video.
4. Video can become structured procedure JSON.
5. Instructor examples can be extracted.
6. Executor can use the procedure on an unseen case.
7. Accuracy can be measured.
8. Only then should the product UI become sophisticated.

The first experiment should take exactly one instructional video and test whether Gemini reliably returns `task`, `objective`, `inputs`, `outputs`, `steps`, `rules`, `exceptions`, and `examples` as structured JSON.

## Non-goals for MVP

- No foundation-model fine-tuning or weight updates.
- No LoRA or QLoRA.
- No unnecessary ML frameworks.
- No automatic downloading of YouTube videos.
- No premature React frontend.
- No complex multi-user authorization.
- No production-scale infrastructure yet.

## Development Principles

- Keep components modular and portable.
- Prefer typed Pydantic schemas and structured agent outputs.
- Keep deterministic business logic independent from APIs.
- Keep model and provider calls behind service boundaries.
- Add tests for deterministic logic.
- Never hide evaluation failures or uncertainty.
- Never store secrets in Git.
- Avoid unnecessary dependencies and abstraction hierarchies.
- Prefer a working narrow vertical slice over many incomplete features.
- Protect frozen evaluation data from mutation by training flows.
- Record important architectural changes here and setup changes in `README.md`.

## Downloadable Agent Vision

A future export may contain `agent.py`, `skill.json`, prompts, frozen evaluations, dependency metadata, an environment template, and usage documentation. The export system is not part of repository initialization and is not implemented.

## Decision Log

### 2026-08-27 — Initialize a modular Python skeleton

- **Decision:** Establish a FastAPI entry point, typed procedural contracts, explicit agent modules, and provider service boundaries without implementing the learning pipeline.
- **Reason:** Preserve the product intent while enabling a small, measurable first experiment.
- **Alternatives:** Build end-to-end agents immediately; start with a frontend; use a monolithic script.
- **Impact:** Subsequent work should prove one-video structured extraction before adding breadth.

### 2026-08-27 — Treat learning as procedural memory acquisition

- **Decision:** The MVP improves external structured memory and does not modify model weights.
- **Reason:** This matches the intended human-inspired loop and permits inspectable, versioned corrections.
- **Alternatives:** Fine-tuning, LoRA/QLoRA, or calling a large prompt the entire learned skill.
- **Impact:** Schemas, evidence, evaluation, and memory versioning are central architectural concerns.

### 2026-08-27 — Anchor evaluation externally

- **Decision:** Prioritize instructor examples, cross-video cases, and a protected frozen human set.
- **Reason:** Prevent circular self-grading and provide credible hackathon metrics.
- **Alternatives:** Model-generated tests graded solely by the same model.
- **Impact:** Every future evaluation result should retain its expected-output source and expose failures.

## Current Status

The target path did not exist when initialization began, so there was no prior repository content inside it to preserve.

Currently present:

- documented mission, architecture, learning loop, evaluation strategy, priorities, and agent instructions;
- minimal FastAPI application with `/` and `/health`;
- initial Pydantic contracts for task definitions, procedures, skills, training examples, and evaluation results;
- agent and service module boundaries with no fabricated behavior;
- dependency/configuration manifests, secret-safe environment template, ignore rules, and smoke tests;
- placeholder directories for local data, frozen evaluations, scripts, and exports;
- a verified local environment: `.venv` on Python 3.12.10 with every declared dependency installed and the project installed editable with the `dev` extra.

Verified on 2026-08-27: `pip check` reports no broken requirements; `google.adk`, `google.genai`, and the Google Cloud clients import successfully; both smoke tests pass; and Uvicorn serves `/`, `/health`, and `/docs` with HTTP 200. `.env` exists locally from `.env.example` with empty credential values, so no provider call has been made yet.

Not yet built:

- Google ADK hello agent and workflow orchestration;
- Gemini credentials or provider calls;
- video ingestion and understanding;
- structured extraction, reconciliation, practice, reflection, retry, or execution logic;
- Firestore, Pub/Sub, Cloud Storage, Cloud Run, export packaging, or frontend integration.

Update this status only after verifying new functionality.
