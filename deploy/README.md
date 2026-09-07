# Deploying APRENDIZ to Cloud Run

`deploy.sh` does the whole thing. Read it before running it: it creates billable
resources and it is short enough to read.

```bash
export CLICKHOUSE_HOST=<your-service>.<region>.gcp.clickhouse.cloud
bash deploy/deploy.sh
```

It asks for the ClickHouse password on stdin and writes it straight to Secret
Manager. The password is never an argument, so it does not reach shell history,
`ps`, or a build log.

## What it creates

| Resource | Name | Why |
|---|---|---|
| Bucket | `<project>-aprendiz-records` | Records and uploaded video. Cloud Run has no disk that survives a revision. |
| Service account | `aprendiz-run@…` | The service runs as this, not as the default compute account. |
| Secret | `clickhouse-password` | Mounted as an environment variable at runtime. |
| Artifact Registry repo | `aprendiz` | The container image. |
| Cloud Run service | `aprendiz` | The application. |

## The permissions it grants, and the ones it does not

- `roles/storage.objectAdmin` **on the bucket only**, not the project. The
  service reads, writes and deletes objects; it never changes the bucket's own
  configuration, so it does not get `admin`.
- `roles/secretmanager.secretAccessor` **per secret**. The account can read
  that secret and no other.
- **No Vertex AI or Generative AI role.** Provider calls are disabled by
  default in this application, and an account that cannot call a model cannot
  be made to spend money by a bug. Enabling `GOOGLE_GENAI_ENABLED` later means
  granting `roles/aiplatform.user` then, deliberately, as its own decision.

The bucket is created with uniform bucket-level access and public access
prevention, so no object can be exposed by an ACL nobody remembers setting.

## Two things to check after it finishes

**`records_survive_restart` in `/api/status` must be true.** If it is false the
bucket did not reach the service and everything written will be lost at the
next revision. The application says so rather than reporting a writable
container filesystem as durability — a directory that accepts writes is not the
same as records that outlive the container, and on Cloud Run those differ.

**ClickHouse Cloud restricts connections by IP.** Cloud Run egress is not a
fixed address unless you route it through one. Either allow the region's
ranges, attach a VPC connector with Cloud NAT and allow that address, or accept
that the evidence store reports itself unavailable — in which case the QC
console says the library-scale view is missing rather than showing an empty
library, which would read as a clean one.

## The image

Chromium is only reachable when `COMPUTER_BROWSER_ENABLED` is true, and it is
false by default. The deploy leaves it out (`INSTALL_BROWSER=false`), which
saves roughly a gigabyte of image and the cold start that comes with it. Set
`INSTALL_BROWSER=true` if you intend to enable browser execution; the local
`docker build` default still installs it, so nothing about the existing build
changed.

## Two things the first deployment taught us

**`.gcloudignore` follows gitignore rules, and `.dockerignore` does not.** A
file cannot be re-included once its parent directory is excluded, so `data`
followed by `!data/evaluations` silently dropped the frozen evaluation set and
the build failed at `COPY data/evaluations`. It is written as `data/*` now. A
local `docker build` would never have shown this, because Docker does not share
that rule. Check a context with `gcloud meta list-files-for-upload .` before
blaming the Dockerfile.

**`roles/storage.objectAdmin` does not grant `storage.buckets.get`.** The first
revision logged 403 on every request and degraded to memory with
`durable_storage: false`, because the record store checked availability with
`bucket.exists()`. The store reads and writes objects and never touches the
bucket's own configuration, so the fix was to probe with an object listing
rather than to widen the grant. A test now fails if anything reaches for
`exists()` again.

## Verified on 2026-09-06

Deployed to `https://aprendiz-963953909890.us-central1.run.app`.
`/api/status` reports `durable_storage`, `records_survive_restart` and
`workflow_evidence_durable` all true. A project created through the API landed
in the bucket at `records/projects/`, and was read back intact from a new
revision with an empty container — records survive a restart with no local
disk. ClickHouse is reachable from Cloud Run: the QC library reports
`evidence_available: true`, so the IP allowlist did not need changing. The
verification project was then removed.

The three-minute demo has not been recorded, and no motion analysis has been
run against the deployed service, because producing one costs a cloud call.
