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

## Compatibility correction

Further bounded diagnosis established that the 257-second duration was not the
cause. Gemini 3.5 Flash returned `500 INTERNAL` for both the canonical and exact
share URL, and the experimental Vertex Interactions route was unavailable to
the project. A minimal Gemini 2.5 Flash Lite request then accessed the exact
same video successfully:

- elapsed time: 10.682 seconds;
- prompt tokens: 23,446;
- candidate tokens: 43;
- total tokens: 23,489;
- returned duration: 257 seconds.

Direct YouTube extraction now uses a separate
`GOOGLE_GENAI_YOUTUBE_MODEL=gemini-2.5-flash-lite` compatibility setting rather
than first making a failing 3.5 call. The general model remains Gemini 3.5 Flash
Lite. Failed provider records now retain only the safe HTTP status, provider
status label, and attempted model.

The first full structured response reached the prior 4,096-token output limit
and produced incomplete JSON. The YouTube-specific output limit was therefore
raised to 8,192 tokens, the prompt was bounded to 12 concise procedural steps,
and incomplete JSON is now converted into a sanitized response failure rather
than escaping as a validation exception.

The corrected full extraction completed successfully:

- model: `gemini-2.5-flash-lite`;
- elapsed time: 12.559 seconds;
- prompt tokens: 23,653;
- candidate tokens: 1,565;
- total tokens: 25,218;
- structured procedure: 12 evidence-backed steps;
- cloud calls for the successful extraction: 1;
- raw response retained: false;
- execution actions: none.

The generated draft remains evidence for human review, not medical advice or a
robot motion program. A final prompt correction excludes promotional website or
subscription calls to action from future procedures without making another
provider call.

The temporary project targeted a robot but intentionally omitted an exact robot
model. It remained insufficiently clear, so no simulator or motion adapter was
selected. No walking instructions, robot trajectory, or safety claim should be
inferred from this failed extraction.
