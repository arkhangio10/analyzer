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
GOOGLE_GENAI_MAX_OUTPUT_TOKENS=4096
```

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

The route is synchronous for this narrow experiment. Background processing,
uploads, discovery, and persistence remain later milestones.
