# APRENDIZ Persistent Project Memory

Read this document before making significant architectural changes. It records the project's current truth. Preserve historical decisions in the Decision Log, but update the other sections when reality changes.

## Project Identity

**Name:** APRENDIZ

## Mission

Teach software agents and embodied systems such as robots procedural tasks from human demonstrations and instructional videos.

## Product Vision

Enable a non-programmer to explain what an agent should learn, choose whether it will execute on a computer or through a robot, provide or discover demonstrations, let APRENDIZ practice and validate the procedure in an isolated destination, see honest performance, and ultimately obtain a usable runnable agent.

The first hackathon domain is Peruvian accounting calculations such as IGV, net income, CTS, gratificaciones, and simple bank reconciliation. Robot movement learning is now an explicit embodied use case. Both domains provide measurable outcomes, and the architecture must remain generic rather than coupling procedural memory to accounting or one robot vendor.

## Core Principle

The MVP does not modify foundation-model weights. It is not fine-tuning, LoRA, or QLoRA.

Learning means automated procedural knowledge acquisition from unstructured video, with externally anchored self-evaluation. The product builds and improves versioned, structured procedural memory containing objectives, inputs, outputs, ordered steps, rules, conditions, exceptions, examples, sources, uncertainty, and evaluation evidence.

For physical procedures, memory must also retain coordinate or joint-space conventions, timestamps, safety envelopes, speed limits, tool or gripper state, simulator evidence, and the boundary between observed movement and approved hardware execution.

Never simplify the system to "video -> prompt".

## User Flow

1. The user assigns a task.
2. The user chooses an execution destination: computer or robot.
3. `TaskClarifierAgent` forms a task definition and destination contract: name, objective, expected inputs and outputs, constraints, tools, environment or robot model, success criteria, and known exceptions.
4. If information is incomplete or ambiguous, APRENDIZ asks contextual clarification questions, updates its understanding, and repeats until sufficiently clear.
5. The user chooses a YouTube URL, uploads a training video, or asks APRENDIZ to search for reference videos.
6. For automatic search, APRENDIZ shows candidate summaries, relevance, source lineage, contradictions, limitations, and estimated processing cost. Training starts only after user approval.
7. The system understands approved demonstrations and extracts structured procedural knowledge: objective, inputs, outputs, steps, rules, conditions, exceptions, examples, and expected results.
8. APRENDIZ creates a versioned Skill/Procedure independent from one operating system or robot vendor.
9. A destination adapter maps the procedure to computer actions or retargets observed human or animal behavior to a specific robot model and simulator.
10. It imitates demonstrated examples, practices progressively varied exercises, and evaluates results against trustworthy anchors in an isolated environment.
11. On failure, it analyzes the failure, reflects, updates procedural memory, and retries. Failures remain visible.
12. It performs generalization tests and then a final blind validation against a frozen unseen set that learning cannot modify.
13. After human approval, the user can export a one-click Docker agent package. Robot hardware execution remains behind a separate safety-approved adapter.

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
5. **Embodied safety:** learn and evaluate robot motion in simulation first. Replay accuracy never substitutes for collision checking, dynamics validation, risk assessment, or explicit human approval before hardware use.

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
- Google Gemini through the Google GenAI SDK; `gemini-3.5-flash-lite` is the general model, direct YouTube ingestion currently uses the verified `gemini-2.5-flash-lite` compatibility model, and provider calls default to disabled
- FastAPI and Uvicorn
- Pydantic, pydantic-settings, and python-dotenv
- httpx and python-multipart
- Google Cloud: planned Cloud Run, Firestore, Pub/Sub, and Cloud Storage

Prefer passing supported YouTube URLs directly to Gemini. Do not add a downloader or automatic video download by default. Uploaded files are the fallback source.

Do not add TensorFlow, PyTorch, Hugging Face Transformers, LangChain, or another major framework without a demonstrated architectural need.

## Current Priorities

1. Environment works. **Done** — see Current Status.
2. Structured robot-motion demonstration becomes a safety-checked procedure. **Done** — observation-level, simulation-only.
3. Candidate robot replay can be evaluated against instructor ground truth. **Done** — imitation-level only.
4. Connect the bilingual product UI to the real training-session API. **Done** — local simulation session with backend-owned progress.
5. Process one user-approved instructional video with Gemini 3.5 Flash Lite through the guarded experiment endpoint. **Done** — see Current Status.
6. Add destination selection, typed computer/robot contracts, and an explicitly approved container-browser practice. **Done** — automatic video-to-action mapping remains pending.
7. Add automatic YouTube reference discovery, summaries, cost preview, and explicit user approval. **Done** — discovery remains disabled until configured.
8. Integrate approved video extraction, instructor examples, and structured procedure JSON into the project workflow. **In progress** — the project-bound extraction and review gate are implemented, and the corrected provider path now returns a typed walking procedure; a retained project/UI run and human review remain to be completed.
9. Execute and measure an unseen case with trustworthy expected results.
10. Add robot simulator or hardware adapters only after selecting a target platform and defining its safety contract.

The first experiment should take exactly one instructional video and test whether Gemini reliably returns `task`, `objective`, `inputs`, `outputs`, `steps`, `rules`, `exceptions`, and `examples` as structured JSON.

## Non-goals for MVP

- No foundation-model fine-tuning or weight updates.
- No LoRA or QLoRA.
- No unnecessary ML frameworks.
- No automatic downloading of YouTube videos.
- No premature React frontend.
- No complex multi-user authorization.
- No production-scale infrastructure yet.
- No commands to physical robots, autonomous hardware execution, or claims of physical safety in the current slice.

## Development Principles

- Keep components modular and portable.
- Prefer typed Pydantic schemas and structured agent outputs.
- Keep deterministic business logic independent from APIs.
- Keep model and provider calls behind service boundaries.
- Add tests for deterministic logic.
- Never hide evaluation failures or uncertainty.
- Never store secrets in Git.
- Never add AI authorship, AI co-author trailers, generator signatures, badges, or "generated by" attribution to project artifacts or Git history. Preserve configured repository identity and do not fabricate human authorship.
- Avoid unnecessary dependencies and abstraction hierarchies.
- Prefer a working narrow vertical slice over many incomplete features.
- Protect frozen evaluation data from mutation by training flows.
- Record important architectural changes here and setup changes in `README.md`.

## Downloadable Agent Vision

The final product deliverable is a versioned Docker agent package. It may contain `agent.py`, `skill.json`, prompts, frozen evaluations, dependency metadata, health checks, an environment template, Docker configuration, a small cross-platform launcher, and usage documentation. A user who already has Docker installed should not need to install Python or project dependencies: starting the package should launch the agent and make its local interface available with minimal interaction.

Never bake credentials, API keys, `.env` contents, user uploads, or private training data into the Docker image. Supply secrets and user-specific configuration at runtime. The export system is not part of repository initialization and is not implemented.

## Product UI Direction

Use the Be The Buzz fluid-box reference as visual inspiration, not as a design to copy. Adapt these principles to APRENDIZ:

- oversized, expressive typography with concise supporting copy;
- modular content blocks that fluidly reposition across the learning journey;
- a high-contrast palette with restrained gradients and a clear action color;
- purposeful transitions that explain state changes, progress, evaluation, and correction;
- responsive layouts, keyboard navigation, strong focus states, and reduced-motion support;
- honest visibility of uncertainty, contradictions, failures, and frozen-validation results.

Do not let animation obscure controls, hide system status, delay core actions, or become required to understand the workflow.

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

### 2026-08-28 — Deliver exported agents as one-click Docker packages

- **Decision:** The final user deliverable will be a versioned Docker agent package with a minimal launcher and runtime-injected configuration.
- **Reason:** Users should be able to run their trained agent without installing Python or manually resolving dependencies.
- **Alternatives:** Deliver a loose source directory, require a manual Python environment, or host every generated agent centrally.
- **Impact:** Exported agents need a stable runtime contract, health checks, external secret handling, portable storage choices, and reproducible image builds.

### 2026-08-28 — Adopt a fluid modular UI direction

- **Decision:** Use the Be The Buzz fluid-box interaction as inspiration for APRENDIZ's future web experience while preserving accessibility and clarity.
- **Reason:** The moving modular composition fits the product's observe-understand-practice-evaluate workflow and can make state transitions tangible.
- **Alternatives:** A conventional dashboard or a static form wizard.
- **Impact:** UI components should support responsive repositioning, explicit workflow states, restrained motion, and reduced-motion fallbacks.

### 2026-08-28 — Add simulation-first robot-motion procedural learning

- **Decision:** Treat robot movement as an explicit procedural-learning use case and begin with structured joint-space demonstrations in simulation.
- **Reason:** Robot movement makes the product's observe-practice-evaluate model tangible while retaining objective limits and replay measurements.
- **Alternatives:** Couple immediately to one robot vendor, send commands directly to hardware, or postpone embodied procedures entirely.
- **Impact:** Motion learning requires typed waypoints, time, joint and velocity limits, instructor-grounded replay evaluation, explicit simulation scope, and a separate future hardware safety contract.

### 2026-08-28 — Connect the UI through a provider-neutral processing session

- **Decision:** Drive the visible five-stage UI from a typed, pollable backend session that currently uses a built-in safe robot trajectory and reports zero cloud calls.
- **Reason:** Replace the frontend-only animation with real backend state without pretending that raw-video understanding or Gemini orchestration already exists.
- **Alternatives:** Keep a timer-only demo, enable Gemini before confirming credit coverage, or couple the browser directly to provider APIs.
- **Impact:** Future video providers must preserve the session contract, expose their execution mode and failures, and keep provider calls behind service boundaries.

### 2026-08-28 — Containerize the repository application

- **Decision:** Add a secret-safe Dockerfile and Compose service for the current FastAPI application.
- **Reason:** Validate the one-command runtime shape early while the separate per-trained-agent exporter remains future work.
- **Alternatives:** Wait until export generation exists or require local Python for every demonstration.
- **Impact:** The repository app can run on port 8080 without embedding `.env`, uploads, local runtimes, or credentials; exported agent packages still need their own later contract.

### 2026-08-28 — Make execution destination explicit and add approved reference discovery

- **Decision:** Keep procedural learning domain-independent, ask whether execution targets a computer or robot, and add automatic YouTube reference discovery with summaries and explicit user approval.
- **Reason:** The same instructional evidence can describe digital work, physical craftsmanship, or animal motion, but execution requires different environment and safety contracts.
- **Alternatives:** Treat the product as robot-only, assume one computer environment, or train automatically from unreviewed search results.
- **Impact:** Task clarification must collect a computer environment contract or robot embodiment contract. Search candidates are not training evidence until approved. Human or animal movement must be retargeted through a specific robot model and simulator before code can be produced.

### 2026-08-28 — Add a guarded first-video provider experiment

- **Decision:** Expose one synchronous Vertex AI extraction endpoint for a user-approved public YouTube video, with provider calls disabled by default, explicit cost acknowledgement, low media resolution, an output-token cap, typed procedural output, and usage reporting.
- **Reason:** Verify the uncertain video-to-procedure path without coupling provider behavior to the deterministic local simulation or silently incurring cloud cost.
- **Alternatives:** Enable Gemini throughout the existing UI immediately, process unapproved sources, or defer the provider boundary until full orchestration exists.
- **Impact:** The experiment can now be exercised after local ADC configuration. It reports model and token evidence but does not yet persist results, run ADK orchestration, or enter the practice loop.

### 2026-08-28 — Execute computer file actions only in a managed sandbox

- **Decision:** Permit bounded file reads and writes only below a per-execution `.runtime/computer_sandboxes` directory; keep browser, mouse, and keyboard actions blocked until a container adapter exists.
- **Reason:** Provide measurable execution evidence without claiming OS isolation or allowing arbitrary shell access on a machine where Docker is not installed.
- **Alternatives:** Execute directly on the host, pretend validation is execution, or wait for every destination adapter before testing any action.
- **Impact:** File results expose only status, byte count, and SHA-256. Paths cannot be absolute or traverse upward, environment secrets are not resolved, and the local boundary must not be described as Docker-grade isolation.

### 2026-08-28 — Define ARP-1 as an internal normalized robot profile

- **Decision:** Normalize bounded URDF descriptions into APRENDIZ Robot Profile v1 and keep ARP-1 explicitly internal rather than presenting it as an industry standard.
- **Reason:** Users should provide one standard robot description without answering every kinematic question, while downstream training needs consistent typed links, joints, limits, units, and safety state.
- **Alternatives:** Ask users to enter every joint manually, couple directly to one vendor, or call one external format universal.
- **Impact:** The first adapter supports URDF, preserves radians and meters, rejects unsafe XML constructs, verifies tree/link/limit consistency, recommends a simulator without claiming availability, and maps only compatible revolute joints into the current degree-based trainer. SDF, MJCF, collision checking, dynamics, and simulator launch remain future adapters.

### 2026-08-29 — Verify a hardened application-container boundary

- **Decision:** Run acknowledged computer file actions in the Compose application container as an unprivileged user with a read-only root filesystem, bounded temporary runtime mounts, all Linux capabilities dropped, `no-new-privileges`, a process limit, and a health check.
- **Reason:** Docker Desktop and WSL 2 are now available, so the prior managed-directory boundary can be strengthened and measured without granting shell, host filesystem, browser, or hardware access.
- **Alternatives:** Continue treating the host directory as the only boundary, run the service as root, or enable browser automation before its network and evidence controls exist.
- **Impact:** Execution results distinguish `managed_local_directory` from `application_container`. The container can write only to its bounded runtime storage; its application root is read-only, it runs as UID/GID 10001, and the existing API still reports redacted file evidence and zero external host/cloud actions. Browser actions remain blocked pending their dedicated adapter.

### 2026-08-29 — Add a guarded container-browser vertical slice

- **Decision:** Add a separate Playwright/Chromium endpoint for explicitly acknowledged `navigate`, `click`, and `type_text` actions, enabled only inside the application container and constrained to exact approved public hosts.
- **Reason:** Computer-task learning needs measurable execution, while browser access must not become unrestricted network, credential, download, shell, or host access.
- **Alternatives:** Keep all UI actions validation-only, allow arbitrary destinations, expose screenshots/page bodies, resolve environment secrets, or merge browser and file execution into one ambiguous endpoint.
- **Impact:** Browser runs are limited to 25 actions and bounded timeouts. Private and unapproved destinations are rejected or intercepted, downloads, service workers, WebSockets, and WebRTC are disabled, sensitive fields and environment values are blocked, and evidence redacts typed values, page content, URL queries/fragments, and page titles. Chromium has been verified as UID/GID 10001 under the read-only `application_container` boundary with all capabilities dropped and `no-new-privileges` enabled.

### 2026-08-29 — Bind reviewed browser practice to computer projects

- **Decision:** Store a browser rehearsal as a project-bound draft, validate its exact public-host allowlist before execution, and require separate acknowledgements that the actions were reviewed and external network access is approved.
- **Reason:** Connect the computer project path to real execution without claiming that today’s video-reference intake already produces executable actions.
- **Alternatives:** Call the low-level executor directly from the UI, infer actions from task text, or silently execute immediately after project creation.
- **Impact:** The bilingual UI now previews navigation and optional non-sensitive text entry, makes approval visible, and reports backend-owned stages and redacted evidence. The workflow makes zero Gemini calls and the user must create a new draft to retry a completed or blocked rehearsal.

### 2026-08-30 — Retain project-bound video procedures behind human review

- **Decision:** Attach each explicitly approved YouTube extraction attempt to a project, retain either a typed versioned procedure or sanitized failure evidence in process memory, and require approve/reject review before later destination adaptation.
- **Reason:** Connect the proven provider experiment to the product workflow without silently executing model output or hiding failed paid attempts.
- **Alternatives:** Keep the experiment endpoint disconnected, execute extracted steps immediately, or discard provider failures.
- **Impact:** The bilingual UI now displays source, provider usage, timestamped evidence, rules, exceptions, examples, uncertainties, and review state. Share URLs are canonicalized only for the provider while original lineage is preserved. Approval records a decision only; automatic action mapping remains pending.

### 2026-08-30 — Separate the direct-YouTube compatibility model

- **Decision:** Keep `gemini-3.5-flash-lite` as the general model but route direct YouTube video extraction through the separately configurable `gemini-2.5-flash-lite` compatibility model.
- **Reason:** The approved 257-second walking video returned internal errors with Gemini 3.5 Flash Lite and Gemini 3.5 Flash through both short and canonical URLs, while one bounded Gemini 2.5 Flash Lite request successfully accessed the same video and reported token usage.
- **Alternatives:** Repeatedly retry the failing 3.5 request, adopt the unavailable experimental Interactions endpoint, or automatically download the YouTube video.
- **Impact:** Each approved extraction still makes at most one cloud call, failures retain only safe HTTP/provider/model diagnostics, automatic downloads remain prohibited, and the compatibility model must be replaced before its published retirement.

## Current Status

The target path did not exist when initialization began, so there was no prior repository content inside it to preserve.

Currently present:

- documented mission, architecture, learning loop, evaluation strategy, priorities, and agent instructions;
- FastAPI application with the product interface at `/`, JSON status at `/api/status`, process health at `/health`, and OpenAPI documentation at `/docs`;
- an initial responsive bilingual Spanish/English frontend with a fluid modular visual system, guided task/source/review interaction, backend-driven processing progress, keyboard focus states, reduced-motion support, and social-preview metadata;
- initial Pydantic contracts for task definitions, procedures, skills, training examples, and evaluation results;
- typed robot-motion contracts, deterministic safety validation, movement procedure extraction, instructor-grounded replay evaluation, and in-memory training-session retrieval;
- agent and service module boundaries with no fabricated behavior;
- a provider-neutral visible-processing API whose local session reports `cloud_calls_made=0`, validates a built-in six-joint trajectory, extracts nine procedure steps, and returns replay evidence;
- destination-aware project intake, guarded YouTube candidate discovery with explicit approval, cross-source reconciliation, and protected frozen evaluation;
- validation-only computer plans plus explicitly acknowledged file reads and writes confined to per-execution managed local sandboxes with redacted evidence and an explicit host-directory or application-container isolation boundary;
- a container-only Playwright browser executor with exact approved-host policy, private-network blocking, bounded navigation/click/text actions, and redacted execution evidence;
- project-bound computer-practice drafts with explicit action/network approval and a bilingual UI that renders their real execution evidence;
- project-bound video extraction records with cost/source acknowledgement, safe failure categories, versioned structured procedures, and explicit human review;
- an internal ARP-1 robot profile with guarded URDF normalization, simulator recommendation, explicit readiness errors, and a revolute-joint bridge to the motion trainer;
- dependency/configuration manifests, secret-safe environment template, ignore rules, Dockerfile, Compose service, and smoke tests;
- placeholder directories for local data, frozen evaluations, scripts, and exports;
- a verified local environment: `.venv` on Python 3.12.10 with every declared dependency installed and the project installed editable with the `dev` extra.

Verified through 2026-08-30: all 70 tests pass; Uvicorn serves the UI and APIs; local robot-motion processing reaches 100% with safety and replay evidence; managed computer file actions remain inside a per-execution runtime directory and return redacted hashes; a representative quadruped URDF normalizes into a valid ARP-1 profile and degree-based motion contract. `.env` remains excluded from Git. Vertex AI is enabled for the configured project, local ADC and billing are active, and a prior minimal Gemini 3.5 Flash Lite connectivity probe returned `APRENDIZ_READY` using 16 total tokens. The guarded repository endpoint previously processed the approved dog-agility video with one call at low media resolution: 12,452 prompt tokens, 1,249 candidate tokens, 13,701 total tokens, 12.094 seconds, and eight evidence-backed procedure steps. On 2026-08-30, direct attempts to process the public 257-second walking video `-fD2TSL2s7I` through Gemini 3.5 Flash Lite and Gemini 3.5 Flash returned internal provider errors; the experimental Vertex Interactions route was unavailable. A bounded Gemini 2.5 Flash Lite request accessed the same URL successfully, so direct YouTube extraction now selects it through a separate compatibility setting without first calling a failing model. The corrected full structured extraction completed in 12.559 seconds with 23,653 prompt tokens, 1,565 candidate tokens, 25,218 total tokens, and 12 evidence-backed draft steps. The result remains subject to human review and is not medical advice or robot programming. Provider calls remain disabled by default. Billing impact for failed calls cannot be inferred without the Cloud Billing report. Docker Desktop was unavailable for this change's container rebuild, but the host suite passed and prior Docker verification remains valid: runtime UID/GID 10001, read-only root filesystem, and acknowledged file/browser execution inside `application_container`. Simulator execution remains unverified.

Not yet built:

- Google ADK hello agent and workflow orchestration;
- durable video-session persistence and uploaded-video ingestion;
- higher-frame-rate motion analysis for robot-ready gait extraction;
- durable video-procedure persistence, cross-source orchestration, reflection, retry, or general-purpose desktop execution logic;
- Firestore, Pub/Sub, Cloud Storage, Cloud Run, or per-trained-agent export packaging.

Product direction confirmed on 2026-08-28: the UI adapts the Be The Buzz fluid-box visual language, supports Spanish and English for international jurors, and visibly renders backend-owned processing stages without pretending that provider video processing is implemented. The repository application is containerized; the final per-agent export remains a one-click Docker package with runtime-injected secrets.

Backend progress verified on 2026-08-28: the simulation-only robot-motion vertical slice accepts structured instructor demonstrations, rejects unsafe joint positions and velocities, extracts an observation-level procedure, stores the session in memory, and evaluates candidate replay data against the instructor reference. It does not process raw video, control hardware, check collisions or dynamics, or prove generalization.

Update this status only after verifying new functionality.
