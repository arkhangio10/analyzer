# Architecture

APRENDIZ is organized around a domain-independent learning flow with explicit destination contracts, data contracts, and provider boundaries. The complete reviewed product flow is maintained in `docs/product_flow.md`.

```text
User task
  -> Task clarification
  -> Execution destination: computer or robot
  -> Training source (YouTube URL or uploaded video)
     or automatic reference search -> summaries -> user approval
  -> Video understanding
  -> Structured procedure and instructor examples
  -> Reconciliation across sources
  -> Destination adaptation
     -> computer action primitives and sandbox
     -> robot retargeting and simulator
  -> Practice and execution in the isolated destination
  -> Externally anchored evaluation
  -> Procedural-memory revision
  -> Frozen unseen validation
  -> Versioned Docker agent export
```

For embodied procedures, the current deterministic slice adds a safety gate before procedural extraction:

```text
Structured robot-motion demonstration
  -> Joint topology and timestamp validation
  -> Position and velocity safety checks
  -> Inspectable movement procedure
  -> Candidate replay evaluation against instructor ground truth
```

This flow analyzes simulation data only. Hardware adapters, collision checking, robot dynamics, and physical actuation are outside the current boundary.

The product interface uses a provider-neutral processing-session contract:

```text
POST local processing session
  -> backend validates a built-in six-joint demonstration
  -> frontend polls backend-owned progress
  -> completed session exposes procedure and replay evidence
  -> execution_mode=local_simulation, cloud_calls_made=0
```

The current service computes the deterministic result immediately and reveals it after monotonic stage progression. This is a narrow orchestration slice, not a claim that raw video is being processed. A future Gemini-backed source can replace the built-in trajectory behind the same typed session response.

The first provider-backed experiment is exposed separately at
`POST /api/experiments/video/extract`. It accepts one explicitly approved public
YouTube URL, requires cost acknowledgement, requests a typed `Procedure`, uses
low media resolution and a bounded output, and returns provider usage metadata.
It does not yet create a durable training session or feed the visible five-stage
processing console.

## Layers

- `api`: transport only; it should not contain learning logic.
- `agents`: workflow responsibilities and decisions.
- `models`: versionable contracts shared by all layers.
- `services`: Gemini and GCP provider integration.
- `data`: local development artifacts, not a production persistence design.

The RootAgent will coordinate the workflow. Provider-specific objects and robot-vendor details should not leak into core procedural models. Destination adapters translate generic procedure steps into computer actions or robot-specific motion only after their environment contract is known. Cloud services remain optional until the one-video vertical slice demonstrates value.

## Product and export boundary

The product UI presents the learning flow as a sequence of fluid, repositionable content blocks and provides a guided task/source/review form. It supports Spanish and English. Its processing console now calls the local backend, polls session state, and renders returned procedure and evaluation metrics. The selected link or filename remains reference metadata; the UI states that it is not yet analyzed. Motion is an enhancement, not a dependency: the workflow remains understandable on mobile, by keyboard, and with reduced motion enabled.

The final delivery artifact will be a versioned Docker agent package rather than a loose Python project. It should contain the runnable agent, its validated procedural memory, dependency metadata, health checks, and usage documentation. A small launcher may wrap Docker Compose so the user can start the agent and open its local interface with minimal interaction. Secrets, API keys, and user data stay outside the image and are injected only at runtime.

## Initial experiment boundary

Input: one supported instructional video reference.

Output: validated structured JSON containing task, objective, inputs, outputs, steps, rules, exceptions, and instructor-grounded examples.

The repository performs the deterministic robot-motion experiment, but it does not yet perform this one-video Gemini experiment.
