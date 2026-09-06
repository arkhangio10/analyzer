"""ClickHouse-backed evidence store for motion samples and audit results.

Motion analysis produces the only genuinely large data in this project: one
short clip at 4 fps already yields hundreds of timestamped joint readings, and a
library yields millions. That is a columnar workload, so the samples live here
rather than in a JSON file, and the plausibility audit is asked of the database
instead of of one analysis at a time.

The audit's rules are not duplicated. `evidence_schema` holds SQL that counts
exactly what the Python reference counts, and both hand their counts to
`verdict_from_counts`. A differential test asserts the two agree; if they ever
disagree, the counting is wrong, because the rules are shared.

Like every other outbound integration here, this degrades rather than fails: an
unconfigured or unreachable ClickHouse leaves `is_available` false and the
application keeps working without library-scale evidence.
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import Settings, get_settings
from app.models.motion_analysis import MotionAnalysisRecord, MotionEvidenceAudit
from app.services import evidence_schema as schema
from app.services.motion_evidence_audit import (
    MIN_SERIES_POINTS,
    MIN_SWING_SPAN_DEGREES,
    verdict_from_counts,
)


logger = logging.getLogger(__name__)

SAMPLE_COLUMNS = [
    "analysis_id",
    "project_id",
    "extraction_id",
    "source_url",
    "joint",
    "side",
    "timestamp_seconds",
    "angle_degrees",
    "confidence",
    "visibility",
    "captured_at",
]

RUN_COLUMNS = [
    "analysis_id",
    "project_id",
    "extraction_id",
    "source_url",
    "requested_fps",
    "window_start_seconds",
    "window_end_seconds",
    "subject_kind",
    "kinematic_chain",
    "sample_count",
    "distinct_joint_count",
    "observed_span_seconds",
    "samples_per_second",
    "mean_confidence",
    "clear_sample_count",
    "verdict",
    "retarget_supported",
    "provider",
    "requested_model",
    "model_version",
    "elapsed_seconds",
    "prompt_tokens",
    "candidate_tokens",
    "total_tokens",
    "cloud_calls_made",
    "created_at",
]

FINDING_COLUMNS = ["analysis_id", "code", "message", "values", "created_at"]


class EvidenceStore:
    """Write motion evidence to ClickHouse and ask it the audit questions."""

    def __init__(
        self,
        settings: Settings | None = None,
        client: Any | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._client = client
        self._failed = False
        if client is not None:
            self._failed = False

    # --- connection -------------------------------------------------------

    @property
    def is_configured(self) -> bool:
        """Report whether a ClickHouse was asked for at all."""
        return bool(
            self._settings.clickhouse_enabled and self._settings.clickhouse_host
        )

    @property
    def is_available(self) -> bool:
        """Report whether evidence can actually be written right now."""
        if not self.is_configured and self._client is None:
            return False
        return self._connect() is not None

    def _connect(self) -> Any | None:
        if self._client is not None:
            return self._client
        if self._failed or not self.is_configured:
            return None
        try:
            import clickhouse_connect
        except ImportError:
            logger.warning("clickhouse-connect is not installed; evidence is not stored.")
            self._failed = True
            return None
        try:
            self._client = clickhouse_connect.get_client(
                host=self._settings.clickhouse_host,
                port=self._settings.clickhouse_port,
                username=self._settings.clickhouse_user,
                password=self._settings.clickhouse_password or "",
                database=self._settings.clickhouse_database,
                secure=self._settings.clickhouse_secure,
            )
        except Exception as error:  # noqa: BLE001 - any driver failure degrades
            # The message can carry the host but never the password, because the
            # password is not part of what the driver reports back.
            logger.warning("ClickHouse is unreachable; evidence is not stored: %s", error)
            self._failed = True
            return None
        return self._client

    def ensure_schema(self) -> bool:
        """Create the tables if they do not exist; report whether they exist."""
        client = self._connect()
        if client is None:
            return False
        try:
            for statement in schema.SCHEMA:
                client.command(statement)
        except Exception as error:  # noqa: BLE001
            logger.warning("ClickHouse schema could not be created: %s", error)
            self._failed = True
            return False
        return True

    # --- writing ----------------------------------------------------------

    def record(self, analysis: MotionAnalysisRecord) -> bool:
        """Store one analysis: its samples, its run row, and its findings."""
        client = self._connect()
        if client is None:
            return False
        usage = analysis.usage
        try:
            if analysis.samples:
                client.insert(
                    "motion_samples",
                    [
                        [
                            analysis.analysis_id,
                            analysis.project_id,
                            analysis.extraction_id,
                            analysis.source_url,
                            sample.joint_name,
                            sample.side,
                            sample.timestamp_seconds,
                            sample.angle_degrees,
                            sample.confidence,
                            sample.visibility.value,
                            analysis.created_at,
                        ]
                        for sample in analysis.samples
                    ],
                    column_names=SAMPLE_COLUMNS,
                )
            client.insert(
                "analysis_runs",
                [
                    [
                        analysis.analysis_id,
                        analysis.project_id,
                        analysis.extraction_id,
                        analysis.source_url,
                        analysis.requested_fps,
                        analysis.window_start_seconds,
                        analysis.window_end_seconds,
                        analysis.subject_kind.value,
                        analysis.kinematic_chain,
                        analysis.sample_count,
                        analysis.distinct_joint_count,
                        analysis.observed_span_seconds,
                        analysis.samples_per_second,
                        analysis.mean_confidence,
                        analysis.clear_sample_count,
                        analysis.audit.verdict.value,
                        int(analysis.retarget.retarget_supported),
                        analysis.provider,
                        analysis.requested_model,
                        analysis.model_version or "",
                        analysis.elapsed_seconds,
                        usage.prompt_tokens or 0,
                        usage.candidate_tokens or 0,
                        usage.total_tokens or 0,
                        analysis.cloud_calls_made,
                        analysis.created_at,
                    ]
                ],
                column_names=RUN_COLUMNS,
            )
            if analysis.audit.findings:
                client.insert(
                    "audit_findings",
                    [
                        [
                            analysis.analysis_id,
                            finding.code.value,
                            finding.message,
                            dict(finding.values),
                            analysis.created_at,
                        ]
                        for finding in analysis.audit.findings
                    ],
                    column_names=FINDING_COLUMNS,
                )
        except Exception as error:  # noqa: BLE001
            logger.warning("Motion evidence could not be stored: %s", error)
            return False
        return True

    # --- the audit, asked of the database ---------------------------------

    def audit_from_sql(
        self,
        analysis_id: str,
        *,
        window_seconds: float,
    ) -> MotionEvidenceAudit | None:
        """Run the audit's counts in ClickHouse and apply the shared rules."""
        client = self._connect()
        if client is None:
            return None
        parameters = {"analysis_id": analysis_id}
        try:
            mirrored = client.query(
                schema.MIRRORED_SIDES, parameters=parameters
            ).result_rows
            uniform = client.query(
                schema.UNIFORM_VALUES, parameters=parameters
            ).result_rows
            cycles = client.query(
                schema.ACYCLIC_JOINTS, parameters=parameters
            ).result_rows
        except Exception as error:  # noqa: BLE001
            logger.warning("The SQL audit could not be run: %s", error)
            return None

        identical, paired = (mirrored[0][0], mirrored[0][1]) if mirrored else (0, 0)
        if uniform and uniform[0][0]:
            total, confidences, visibilities, a_confidence, a_visibility = (
                uniform[0][0],
                uniform[0][1],
                uniform[0][2],
                uniform[0][3],
                uniform[0][4],
            )
        else:
            total, confidences, visibilities = 0, 0, 0
            a_confidence, a_visibility = None, None

        acyclic: list[str] = []
        checked = 0
        for joint_key, span, points, reversals in cycles:
            if points < MIN_SERIES_POINTS:
                continue
            checked += 1
            if span >= MIN_SWING_SPAN_DEGREES and reversals <= 1:
                acyclic.append(joint_key)

        return verdict_from_counts(
            total_samples=int(total),
            identical_pairs=int(identical),
            paired_readings=int(paired),
            distinct_confidences=int(confidences),
            a_confidence=float(a_confidence) if a_confidence is not None else None,
            distinct_visibilities=int(visibilities),
            a_visibility=a_visibility,
            acyclic=sorted(acyclic),
            checked_joint_count=checked,
            window_seconds=window_seconds,
        )

    # --- library questions ------------------------------------------------

    def library_verdicts(self, project_id: str) -> list[dict[str, Any]]:
        """Return how one project's analyses divide across verdicts."""
        return self._rows(
            schema.LIBRARY_VERDICTS,
            {"project_id": project_id},
            ("verdict", "analyses", "samples", "tokens"),
        )

    def untrusted_assets(
        self,
        project_id: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Return the analyses whose evidence did not survive the audit."""
        return self._rows(
            schema.UNTRUSTED_ASSETS,
            {"project_id": project_id, "limit": limit},
            ("analysis_id", "source_url", "verdict", "sample_count", "codes"),
        )

    def _rows(
        self,
        query: str,
        parameters: dict[str, Any],
        fields: tuple[str, ...],
    ) -> list[dict[str, Any]]:
        client = self._connect()
        if client is None:
            return []
        try:
            result = client.query(query, parameters=parameters).result_rows
        except Exception as error:  # noqa: BLE001
            logger.warning("A library query failed: %s", error)
            return []
        return [dict(zip(fields, row)) for row in result]
