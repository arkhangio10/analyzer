"""ClickHouse schema and the plausibility audit expressed as SQL.

The audit in `motion_evidence_audit.py` answers one question about one analysis
in Python. The same four checks belong in the database when the question becomes
"which assets in this library carry metadata that was actually measured?", where
the input is millions of timestamped joint readings rather than a few hundred.

Nothing here executes. This module holds the DDL and the queries as text so they
can be reviewed, tested for injection safety, and run by `evidence_store.py`.
The Python implementation stays the reference: a differential test asserts that
these queries and that function reach the same verdict from the same samples,
and any disagreement is a bug in this file, not in the reference.

Every query is parameterised with ClickHouse's `{name:Type}` syntax. No
identifier is ever interpolated into a statement.
"""

from __future__ import annotations

from typing import Final


DATABASE_PLACEHOLDER: Final = "{database}"

# --- Tables ---------------------------------------------------------------
#
# Samples are append-only and never updated, so a plain MergeTree is correct and
# the sort key matches how the audit reads them: one joint's series in time
# order. Runs are keyed by analysis so a retried insert replaces rather than
# duplicates, which keeps a re-run from inflating the library counts.

CREATE_MOTION_SAMPLES: Final = """
CREATE TABLE IF NOT EXISTS motion_samples
(
    analysis_id       String,
    project_id        String,
    extraction_id     String,
    source_url        String,
    joint             LowCardinality(String),
    side              LowCardinality(String),
    timestamp_seconds Float64,
    angle_degrees     Float64,
    confidence        Float32,
    visibility        LowCardinality(String),
    captured_at       DateTime64(3, 'UTC')
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(captured_at)
ORDER BY (analysis_id, joint, side, timestamp_seconds)
"""

CREATE_ANALYSIS_RUNS: Final = """
CREATE TABLE IF NOT EXISTS analysis_runs
(
    analysis_id           String,
    project_id            String,
    extraction_id         String,
    source_url            String,
    requested_fps         Float32,
    window_start_seconds  Float32,
    window_end_seconds    Float32,
    subject_kind          LowCardinality(String),
    kinematic_chain       LowCardinality(String),
    sample_count          UInt32,
    distinct_joint_count  UInt16,
    observed_span_seconds Float32,
    samples_per_second    Float32,
    mean_confidence       Float32,
    clear_sample_count    UInt32,
    verdict               LowCardinality(String),
    retarget_supported    UInt8,
    provider              LowCardinality(String),
    requested_model       LowCardinality(String),
    model_version         String,
    elapsed_seconds       Float32,
    prompt_tokens         UInt32,
    candidate_tokens      UInt32,
    total_tokens          UInt32,
    cloud_calls_made      UInt8,
    created_at            DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(created_at)
ORDER BY analysis_id
"""

CREATE_AUDIT_FINDINGS: Final = """
CREATE TABLE IF NOT EXISTS audit_findings
(
    analysis_id String,
    code        LowCardinality(String),
    message     String,
    values      Map(String, String),
    created_at  DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(created_at)
ORDER BY (analysis_id, code)
"""

SCHEMA: Final = (
    CREATE_MOTION_SAMPLES,
    CREATE_ANALYSIS_RUNS,
    CREATE_AUDIT_FINDINGS,
)

TABLES: Final = ("motion_samples", "analysis_runs", "audit_findings")


# --- The audit, as SQL ----------------------------------------------------

# Left and right are paired per instant and per joint. A pair only counts when
# both sides were actually reported at that instant, which is why the HAVING
# clause is not optional: absent readings must not be scored as agreement.
MIRRORED_SIDES: Final = """
SELECT
    countIf(left_angle = right_angle) AS identical,
    count()                           AS paired
FROM
(
    SELECT
        timestamp_seconds,
        joint,
        anyIf(angle_degrees, side = 'left')  AS left_angle,
        anyIf(angle_degrees, side = 'right') AS right_angle,
        countIf(side = 'left')  AS left_count,
        countIf(side = 'right') AS right_count
    FROM motion_samples
    WHERE analysis_id = {analysis_id:String}
    GROUP BY timestamp_seconds, joint
    HAVING left_count > 0 AND right_count > 0
)
"""

UNIFORM_VALUES: Final = """
SELECT
    count()                  AS samples,
    uniqExact(confidence)    AS confidence_values,
    uniqExact(visibility)    AS visibility_values,
    any(confidence)          AS a_confidence,
    any(visibility)          AS a_visibility
FROM motion_samples
WHERE analysis_id = {analysis_id:String}
"""

# A joint that swings widely but reverses at most once has traced one arc, which
# gait never does. Direction is computed per step, steps that do not move are
# dropped, and only then is each direction compared with the previous surviving
# one -- the same rule the Python reference applies, in the same order.
ACYCLIC_JOINTS: Final = """
SELECT
    joint_key,
    any(span)   AS span,
    any(points) AS points,
    countIf(direction != previous_direction AND previous_direction != 0)
        AS reversals
FROM
(
    SELECT
        joint_key,
        span,
        points,
        direction,
        lagInFrame(direction, 1, toInt8(0))
            OVER (PARTITION BY joint_key ORDER BY timestamp_seconds)
            AS previous_direction
    FROM
    (
        SELECT
            concat(side, '.', joint) AS joint_key,
            timestamp_seconds,
            sign(
                angle_degrees - lagInFrame(angle_degrees, 1, angle_degrees)
                    OVER (
                        PARTITION BY concat(side, '.', joint)
                        ORDER BY timestamp_seconds
                    )
            ) AS direction,
            max(angle_degrees) OVER (PARTITION BY concat(side, '.', joint))
                - min(angle_degrees) OVER (PARTITION BY concat(side, '.', joint))
                AS span,
            count() OVER (PARTITION BY concat(side, '.', joint)) AS points
        FROM motion_samples
        WHERE analysis_id = {analysis_id:String}
    )
    WHERE direction != 0
)
GROUP BY joint_key
ORDER BY joint_key
"""

# --- Library-scale questions ---------------------------------------------

LIBRARY_VERDICTS: Final = """
SELECT
    verdict,
    count()          AS analyses,
    sum(sample_count) AS samples,
    sum(total_tokens) AS tokens
FROM analysis_runs FINAL
WHERE project_id = {project_id:String}
GROUP BY verdict
ORDER BY analyses DESC
"""

UNTRUSTED_ASSETS: Final = """
SELECT
    r.analysis_id     AS analysis_id,
    r.source_url      AS source_url,
    r.verdict         AS verdict,
    r.sample_count    AS sample_count,
    groupArray(f.code) AS codes
FROM analysis_runs AS r FINAL
LEFT JOIN audit_findings AS f FINAL ON f.analysis_id = r.analysis_id
WHERE r.project_id = {project_id:String} AND r.verdict != 'usable'
GROUP BY analysis_id, source_url, verdict, sample_count
ORDER BY sample_count DESC
LIMIT {limit:UInt32}
"""

AUDIT_QUERIES: Final = {
    "mirrored_sides": MIRRORED_SIDES,
    "uniform_values": UNIFORM_VALUES,
    "acyclic_joints": ACYCLIC_JOINTS,
}

LIBRARY_QUERIES: Final = {
    "library_verdicts": LIBRARY_VERDICTS,
    "untrusted_assets": UNTRUSTED_ASSETS,
}
