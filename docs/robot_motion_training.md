# Robot-motion training vertical slice

The first embodied-learning backend accepts a structured joint-space demonstration. It proves that APRENDIZ can retain inspectable physical procedures without pretending to control hardware or update model weights.

## Training request

Send a `POST` request to `/api/training/robot-motion`:

```json
{
  "task_name": "Move a component between trays",
  "objective": "Learn a safe pick-and-place joint trajectory.",
  "robot_model": "SimArm-2",
  "demonstration_id": "demo-pick-place-001",
  "source": "instructor://robotics-lab/session-001",
  "waypoints": [
    {
      "timestamp_seconds": 0,
      "joint_positions_degrees": [0, 0],
      "gripper_percent": 100,
      "label": "home"
    },
    {
      "timestamp_seconds": 1,
      "joint_positions_degrees": [10, 5],
      "gripper_percent": 40,
      "label": "pick"
    },
    {
      "timestamp_seconds": 2,
      "joint_positions_degrees": [20, 10],
      "gripper_percent": 40,
      "label": "place"
    }
  ],
  "joint_limits": [
    {
      "joint_index": 0,
      "minimum_degrees": -90,
      "maximum_degrees": 90,
      "maximum_velocity_degrees_per_second": 20
    },
    {
      "joint_index": 1,
      "minimum_degrees": -45,
      "maximum_degrees": 45,
      "maximum_velocity_degrees_per_second": 10
    }
  ],
  "instructor_verified": true,
  "simulation_only": true
}
```

The response contains deterministic metrics, safety evidence, and a structured `Procedure`. `validation_scope` distinguishes an instructor-provided demonstration from an unverified observation.

## Replay evaluation

Send candidate waypoints to `POST /api/training/robot-motion/{session_id}/evaluate`. The backend reports mean and maximum joint error, duration error, safety failures, and a score. Expected values retain the instructor source so the result is not self-graded.

## Safety boundary

- `simulation_only` must be `true`.
- Every joint requires exactly one position and velocity limit.
- Timestamps must increase strictly.
- Unsafe demonstrations are rejected without a procedure.
- Rejected sessions cannot be evaluated.
- Passing replay evaluation is evidence of imitation only, not safe physical deployment.
