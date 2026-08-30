# Controlled video experiment

The first cloud-backed experiment analyzes exactly one user-approved public
YouTube video and returns a typed `Procedure`. It is deliberately separate from
the local robot-motion simulation.

## Safety and cost gates

- Provider calls remain disabled unless `GOOGLE_GENAI_ENABLED=true`.
- Each request must include `acknowledge_cloud_cost: true`.
- The first endpoint accepts only public YouTube URLs.
- Video processing uses low media resolution and a configured output-token cap.
- The result reports provider, requested model, model version, elapsed time, and
  provider-reported token usage.
- API keys, ADC credentials, and raw provider responses are not returned or
  retained by the endpoint.

## Local Vertex AI configuration

Authenticate Application Default Credentials and configure a quota project:

```powershell
gcloud.cmd auth application-default login --project=<your-project-id>
gcloud.cmd services enable aiplatform.googleapis.com --project=<your-project-id>
```

Keep `.env` outside Git and configure:

```dotenv
GOOGLE_CLOUD_PROJECT=<your-project-id>
GOOGLE_CLOUD_LOCATION=global
GOOGLE_GENAI_ENABLED=true
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_GENAI_MODEL=gemini-3.5-flash-lite
GOOGLE_GENAI_YOUTUBE_MODEL=gemini-2.5-flash-lite
GOOGLE_GENAI_MAX_OUTPUT_TOKENS=4096
GOOGLE_GENAI_YOUTUBE_MAX_OUTPUT_TOKENS=8192
```

`GOOGLE_GENAI_YOUTUBE_MODEL` is intentionally separate from the general model.
The current compatibility model successfully ingested the approved 257-second
walking video after both Gemini 3.5 Flash variants returned internal errors for
that source. The service does not call a failing primary model first, so one
approved extraction still makes at most one provider call. Revalidate and
replace this compatibility model before its published retirement date.
The separate YouTube output limit accommodates structured timestamp evidence;
the extraction prompt also caps the result at 12 concise ordered steps.

## Request

```http
POST /api/experiments/video/extract
Content-Type: application/json

{
  "video_url": "https://www.youtube.com/watch?v=<video-id>",
  "task_hint": "Describe the procedure demonstrated by the instructor.",
  "output_language": "es",
  "acknowledge_cloud_cost": true
}
```

The low-level route remains synchronous. The project workflow wraps the same
provider boundary with in-process retention and human review:

```http
POST /api/projects/{project_id}/video-procedures/extract
Content-Type: application/json

{
  "video_url": "https://www.youtube.com/watch?v=<video-id>",
  "task_hint": "Extract only observable actions.",
  "output_language": "en",
  "acknowledge_cloud_cost": true,
  "acknowledge_source_approved": true
}
```

Successful records remain `awaiting_review` until the user approves or rejects
them. Provider failures remain retrievable with a sanitized category and no raw
provider response. Safe failure evidence includes the HTTP status, provider
status label, and attempted model when available; raw error details remain
excluded. This storage is process-local; durable persistence,
background processing, and uploaded-video ingestion remain later milestones.
