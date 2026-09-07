#!/usr/bin/env bash
#
# Deploy APRENDIZ to Cloud Run.
#
# Run this yourself. It creates billable resources -- a bucket, secrets, a
# service, an Artifact Registry repository -- and it is written to be read
# before it is run, not pasted blind. Every step is idempotent: running it
# twice changes nothing the second time.
#
# It never takes a secret as an argument, because arguments end up in shell
# history and in `ps`. Secret values are read from stdin and go straight to
# Secret Manager.
#
# What it deliberately does NOT grant: any Vertex AI or Generative AI role.
# Provider calls are disabled by default in this application, and a service
# account that cannot call a model cannot be made to spend money by a bug. If
# you later enable GOOGLE_GENAI_ENABLED, grant roles/aiplatform.user then, as a
# separate decision you make on purpose.

set -euo pipefail

PROJECT="${PROJECT:-analyzer-robotics-ark10}"
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-aprendiz}"
BUCKET="${BUCKET:-${PROJECT}-aprendiz-records}"
REPO="${REPO:-aprendiz}"
SA_NAME="${SA_NAME:-aprendiz-run}"
SA="${SA_NAME}@${PROJECT}.iam.gserviceaccount.com"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT}/${REPO}/${SERVICE}"

# Browser execution is off by default; leaving Chromium out of the image saves
# roughly a gigabyte and the cold start that comes with it.
INSTALL_BROWSER="${INSTALL_BROWSER:-false}"

say() { printf '\n=== %s ===\n' "$1"; }

say "Target"
cat <<SUMMARY
  project : ${PROJECT}
  region  : ${REGION}
  service : ${SERVICE}
  bucket  : gs://${BUCKET}
  account : ${SA}
  image   : ${IMAGE}
  chromium: ${INSTALL_BROWSER}
SUMMARY
read -r -p "Proceed? [y/N] " reply
[ "${reply}" = "y" ] || { echo "Nothing was done."; exit 1; }

# --- 1. APIs ---------------------------------------------------------------
say "Enabling APIs"
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com \
  --project "${PROJECT}"

# --- 2. Bucket -------------------------------------------------------------
say "Bucket"
if gcloud storage buckets describe "gs://${BUCKET}" --project "${PROJECT}" >/dev/null 2>&1; then
  echo "gs://${BUCKET} already exists."
else
  # Uniform access: permissions come from IAM only, so no object can be made
  # public by an ACL nobody remembers setting. Records and uploaded video are
  # private to this project and there is no reason for either to be readable.
  gcloud storage buckets create "gs://${BUCKET}" \
    --project "${PROJECT}" \
    --location "${REGION}" \
    --uniform-bucket-level-access \
    --public-access-prevention
fi

# --- 3. Service account ----------------------------------------------------
say "Service account"
if gcloud iam service-accounts describe "${SA}" --project "${PROJECT}" >/dev/null 2>&1; then
  echo "${SA} already exists."
else
  gcloud iam service-accounts create "${SA_NAME}" \
    --project "${PROJECT}" \
    --display-name "APRENDIZ Cloud Run runtime"
fi

# Scoped to this bucket, not to the project. objectAdmin rather than admin:
# the service reads, writes and deletes objects; it never needs to change the
# bucket's own configuration.
gcloud storage buckets add-iam-policy-binding "gs://${BUCKET}" \
  --project "${PROJECT}" \
  --member "serviceAccount:${SA}" \
  --role roles/storage.objectAdmin >/dev/null

# --- 4. Secrets ------------------------------------------------------------
say "Secrets"
put_secret() {
  local name="$1" prompt="$2"
  if gcloud secrets describe "${name}" --project "${PROJECT}" >/dev/null 2>&1; then
    echo "${name} exists. Add a new version? [y/N]"
    read -r answer
    [ "${answer}" = "y" ] || return 0
    printf '%s' "$(prompt_value "${prompt}")" \
      | gcloud secrets versions add "${name}" --project "${PROJECT}" --data-file=-
  else
    printf '%s' "$(prompt_value "${prompt}")" \
      | gcloud secrets create "${name}" --project "${PROJECT}" --data-file=-
  fi
  # Granted per secret, so this account can read this one and no other.
  gcloud secrets add-iam-policy-binding "${name}" \
    --project "${PROJECT}" \
    --member "serviceAccount:${SA}" \
    --role roles/secretmanager.secretAccessor >/dev/null
}

prompt_value() {
  local value
  read -r -s -p "$1: " value >&2
  echo >&2
  printf '%s' "${value}"
}

put_secret clickhouse-password "ClickHouse password"

# --- 5. Image --------------------------------------------------------------
say "Artifact Registry"
if gcloud artifacts repositories describe "${REPO}" \
     --project "${PROJECT}" --location "${REGION}" >/dev/null 2>&1; then
  echo "Repository ${REPO} already exists."
else
  gcloud artifacts repositories create "${REPO}" \
    --project "${PROJECT}" --location "${REGION}" \
    --repository-format docker \
    --description "APRENDIZ container images"
fi

say "Build"
# cloudbuild.yaml rather than --tag, because --tag cannot pass a build argument
# and the Chromium install is one.
gcloud builds submit \
  --project "${PROJECT}" \
  --config cloudbuild.yaml \
  --substitutions "_IMAGE=${IMAGE},_INSTALL_BROWSER=${INSTALL_BROWSER}" \
  .

# --- 6. Deploy -------------------------------------------------------------
say "Deploy"
# CLICKHOUSE_HOST is not a secret and is passed as configuration. The password
# is mounted from Secret Manager, so it is never in this command, in the
# service's environment configuration, or in a deployment log.
gcloud run deploy "${SERVICE}" \
  --project "${PROJECT}" \
  --region "${REGION}" \
  --image "${IMAGE}" \
  --service-account "${SA}" \
  --allow-unauthenticated \
  --port 8080 \
  --cpu 1 --memory 1Gi \
  --min-instances 0 --max-instances 3 \
  --set-env-vars "APP_ENV=production,LOG_LEVEL=INFO,GCS_BUCKET=${BUCKET},GOOGLE_GENAI_ENABLED=false,COMPUTER_BROWSER_ENABLED=false,CLICKHOUSE_ENABLED=true,CLICKHOUSE_HOST=${CLICKHOUSE_HOST:?set CLICKHOUSE_HOST},CLICKHOUSE_PORT=8443,CLICKHOUSE_USER=default,CLICKHOUSE_DATABASE=default,CLICKHOUSE_SECURE=true" \
  --set-secrets "CLICKHOUSE_PASSWORD=clickhouse-password:latest"

say "Done"
URL="$(gcloud run services describe "${SERVICE}" --project "${PROJECT}" \
        --region "${REGION}" --format 'value(status.url)')"
cat <<NEXT
  Service : ${URL}
  Console : ${URL}/qc
  Status  : ${URL}/api/status

Check that records_survive_restart is true in /api/status. If it is false the
bucket did not reach the service, and anything written will be lost at the next
revision.

ClickHouse Cloud restricts connections by IP. Cloud Run egress is not a fixed
address unless you route it through a static one, so either allow the region's
ranges, attach a VPC connector with Cloud NAT, or expect the evidence store to
report itself unavailable and the library view to say so.
NEXT
