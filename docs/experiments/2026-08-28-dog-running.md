# Dog-running video experiment

## Approved source

- URL: `https://www.youtube.com/watch?v=mRWajW_99Cw`
- Public title: “Lobo” the Siberian Husky goes off script in the 24 inch
  class of agility competition
- Requested task: analyze how the dog runs

## Execution evidence

- Provider: Vertex AI
- Requested and returned model: `gemini-3.5-flash-lite`
- Media resolution: low
- Cloud calls: 1
- Prompt tokens: 12,452
- Candidate tokens: 1,249
- Total tokens: 13,701
- Provider elapsed time: 12.094 seconds
- Raw provider response retained: no

## Extracted behavior

The structured procedure identified eight observable stages: preparation,
initial jump, straight-line acceleration, turning, slalom, ramp traversal,
tunnel traversal, and deceleration at the finish. Each step retains one or more
source timestamps and concise evidence.

The clearest running evidence is the straight acceleration around `00:36–00:38`.
Direction and balance adaptation are visible around `00:51–00:54`, and lateral
trunk control is visible during the slalom around `00:57–01:03`.

## Quality boundary

This pass is sufficient for a high-level agility procedure, but not for a
robot-ready gait. Low-resolution video understanding does not establish exact
foot-contact order, stance and swing durations, joint angles, stride length,
cadence, ground-reaction forces, or center-of-mass dynamics. A later targeted
motion-analysis pass must sample selected running clips at a higher frame rate
and then retarget the measured gait through a specific ARP-1 robot profile.

## Precision-pass attempt

A second approved request targeted `00:33-00:54` at 8 fps and medium media
resolution. Vertex AI rejected the combined direct-YouTube clipping and custom
frame-rate request before returning structured output (`502` at the application
boundary). No automatic retry was made, and no token-usage metadata was
returned. Billing reports must be used to determine whether the rejected
request produced any billable usage.

The next precision pass requires a user-supplied short video file or a Cloud
Storage object so the custom frame rate can be applied to uploaded media without
automatically downloading YouTube content.
