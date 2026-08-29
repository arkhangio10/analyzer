# Product flow

APRENDIZ is a domain-independent procedural-learning system. A task can target execution on a computer or an embodied robot. Video evidence describes the task; a separate execution contract defines how that task can be performed safely on the selected destination.

```mermaid
flowchart TD
    U[User describes the task] --> TARGET{Execution destination}
    TARGET -->|Computer| PC[OS, application, version, permissions and tools]
    TARGET -->|Robot| ROBOT[Robot type, model, joints, sensors, tools and simulator]

    PC --> SOURCE{Choose evidence source}
    ROBOT --> SOURCE

    SOURCE -->|YouTube URL| URL[Provided instructional video]
    SOURCE -->|Upload| UPLOAD[User-provided video]
    SOURCE -->|Automatic search| SEARCH[Search YouTube references]

    SEARCH --> DISCOVER[Rank candidate videos]
    DISCOVER --> SUMMARIES[Show summary, source, relevance and limitations]
    SUMMARIES --> APPROVE{User approves sources}
    APPROVE -->|Adjust selection| DISCOVER
    APPROVE -->|Approved| EVIDENCE[Approved evidence set]
    URL --> EVIDENCE
    UPLOAD --> EVIDENCE

    EVIDENCE --> UNDERSTAND[Multimodal understanding]
    UNDERSTAND --> RECONCILE[Compare sources and expose contradictions]
    RECONCILE --> PROCEDURE[Versioned procedural memory]

    PROCEDURE --> DEST{Adapt to destination}

    DEST -->|Computer| ACTIONS[Map steps to UI, keyboard, API or file actions]
    ACTIONS --> SANDBOX[Practice in an isolated computer environment]

    DEST -->|Robot| RETARGET[Retarget observed human or animal movement]
    RETARGET --> MOTION[Generate robot-specific motion plan]
    MOTION --> SIM[Collision, dynamics and limit checks in simulator]

    SANDBOX --> EVALUATE[Evaluate against instructor and protected cases]
    SIM --> EVALUATE
    EVALUATE --> PASS{Meets acceptance criteria?}
    PASS -->|No| CORRECT[Expose failures and revise procedural memory]
    CORRECT --> DEST
    PASS -->|Yes| HUMAN{Human approval}
    HUMAN -->|Rejected| CORRECT
    HUMAN -->|Approved| PACKAGE[Package agent, procedure and evidence]
    PACKAGE --> DOCKER[Runnable Docker delivery]
```

## Destination contracts

### Computer execution

- Operating system, application, version, resolution, locale, permissions, and available tools.
- Allowed action primitives such as mouse, keyboard, browser automation, APIs, and file operations.
- Isolated practice environment, reversible actions, secret handling, and frozen evaluation cases.

### Robot execution

- Robot category and exact model: arm, mobile base, humanoid, quadruped, or another supported embodiment.
- Kinematic model or URDF, joint map, limits, actuators, sensors, end effectors, workspace, payload, and simulator.
- Motion retargeting from a human or animal reference into robot-feasible trajectories.
- Collision checking, dynamics validation, safety envelopes, simulation evidence, and explicit human approval before any hardware adapter can run.

A human or animal video cannot by itself produce universally safe robot code. It supplies behavioral evidence. The target robot contract and simulator determine whether the behavior can be translated into executable, robot-specific motion.

## Reference discovery rules

- Search results are candidates, not training data, until the user approves them.
- Show source URL, creator/channel, concise summary, relevance, contradictions, limitations, and estimated processing cost.
- Do not automatically download YouTube videos. Pass supported approved URLs to the provider or ask for a user-supplied file.
- Preserve source attribution and evidence lineage inside procedural memory.
- Keep an approved training set separate from frozen evaluation sources.

