# Walking-video extraction attempt — 2026-08-30

## Approved source

- Source: `https://youtu.be/-fD2TSL2s7I?si=bxzyu9PWSIBk5xKx`
- Public metadata title: `Physical Therapist Shows How To Walk Correctly`
- Channel: `Rehab and Revive`
- User explicitly approved Vertex AI credit usage.

## Guardrails

- Model: `gemini-3.5-flash-lite`
- Provider: Vertex AI through Application Default Credentials
- Location: `global`
- Media resolution: low
- Maximum output tokens: 4,096
- Automatic function calling: disabled
- Raw provider response retention: disabled
- Provider enabled only in a temporary local process

## Result

Three bounded attempts were made: the original share URL through the experiment
route, its canonical `youtube.com/watch` URL through the experiment route, and
the original source through the new project-bound workflow after deterministic
canonicalization was added. Vertex returned no structured procedure or token
usage metadata for any attempt.

The integrated attempt retained this evidence:

- extraction status: `extraction_failed`
- safe failure category: `provider_unavailable`
- attempted cloud calls recorded by the workflow: `1`
- structured procedure: none
- automatic execution: none
- raw response retained: false

The first two low-level failures occurred before the project-bound record
existed and therefore have no usage record. The Cloud Billing report is the
only reliable way to determine whether failed provider requests produced a
billable charge.

The temporary project targeted a robot but intentionally omitted an exact robot
model. It remained insufficiently clear, so no simulator or motion adapter was
selected. No walking instructions, robot trajectory, or safety claim should be
inferred from this failed extraction.
