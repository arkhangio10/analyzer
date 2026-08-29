# Architecture

APRENDIZ is organized around a narrow learning flow with explicit data contracts and provider boundaries.

```text
User task
  -> Task clarification
  -> Training source (YouTube URL or uploaded video)
  -> Video understanding
  -> Structured procedure and instructor examples
  -> Reconciliation across sources
  -> Practice and execution
  -> Externally anchored evaluation
  -> Procedural-memory revision
  -> Frozen unseen validation
```

## Layers

- `api`: transport only; it should not contain learning logic.
- `agents`: workflow responsibilities and decisions.
- `models`: versionable contracts shared by all layers.
- `services`: Gemini and GCP provider integration.
- `data`: local development artifacts, not a production persistence design.

The RootAgent will coordinate the workflow. Provider-specific objects should not leak into core procedural models. Cloud services remain optional until the one-video vertical slice demonstrates value.

## Initial experiment boundary

Input: one supported instructional video reference.

Output: validated structured JSON containing task, objective, inputs, outputs, steps, rules, exceptions, and instructor-grounded examples.

This repository currently provides boundaries only; it does not yet perform that experiment.
