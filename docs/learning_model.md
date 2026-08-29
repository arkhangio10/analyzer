# Learning Model

APRENDIZ models learning as inspectable procedural knowledge acquisition:

```text
Observe -> Understand -> Imitate -> Practice -> Evaluate
        -> Reflect -> Correct -> Retry -> Generalize -> Validate
```

Corrections update structured procedural memory, never foundation-model weights in the MVP.

## Evidence and validation

- Instructor-solved examples are ground truth where available.
- Examples from one source can validate procedures extracted from another.
- Conflicting sources create explicit uncertainty.
- Frozen, human-authored cases remain invisible to and immutable by learning.
- Evaluation failures are reported and retained as evidence.

## Progressive levels

0. Observation: extract the demonstrated procedure.
1. Imitation: reproduce demonstrated or nearly identical cases.
2. Variation: change values or inputs while preserving the procedure.
3. Generalization: solve unseen cases with the same underlying procedure.
4. Edge Cases: handle exceptions, omissions, and conflicts.
5. Blind Validation: measure performance on protected unseen cases.

The first MVP domain is Peruvian accounting because outcomes are numerically verifiable. Domain-specific rules belong in learned skills and examples, not hard-coded into the generic orchestration architecture.
