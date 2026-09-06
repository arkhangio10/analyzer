"""Tests for the ClickHouse schema and the audit expressed as SQL.

These cover what can be checked without a server: that the statements are
parameterised rather than interpolated, that every table is sorted the way the
audit reads it, and that the queries only touch tables this schema creates. The
behavioural check that the SQL agrees with the Python reference lives in
`test_evidence_store.py` and needs a real ClickHouse.
"""

import re

from app.services import evidence_schema as schema


ALL_STATEMENTS = {
    **{f"ddl:{name}": sql for name, sql in zip(schema.TABLES, schema.SCHEMA)},
    **{f"audit:{name}": sql for name, sql in schema.AUDIT_QUERIES.items()},
    **{f"library:{name}": sql for name, sql in schema.LIBRARY_QUERIES.items()},
}


def test_every_table_is_created_if_missing() -> None:
    for name, sql in zip(schema.TABLES, schema.SCHEMA):
        assert "CREATE TABLE IF NOT EXISTS" in sql
        assert name in sql


def test_every_table_declares_an_engine_and_sort_key() -> None:
    for sql in schema.SCHEMA:
        assert "ENGINE =" in sql
        assert "ORDER BY" in sql


def test_samples_are_sorted_the_way_the_audit_reads_them() -> None:
    """One joint's series in time order, which is what every check walks."""
    assert (
        "ORDER BY (analysis_id, joint, side, timestamp_seconds)"
        in schema.CREATE_MOTION_SAMPLES
    )


def test_runs_and_findings_replace_rather_than_duplicate_on_retry() -> None:
    assert "ReplacingMergeTree" in schema.CREATE_ANALYSIS_RUNS
    assert "ORDER BY analysis_id" in schema.CREATE_ANALYSIS_RUNS
    assert "ReplacingMergeTree" in schema.CREATE_AUDIT_FINDINGS


def test_no_statement_interpolates_a_value() -> None:
    """Identifiers and values are bound, never formatted into the text."""
    for name, sql in ALL_STATEMENTS.items():
        assert "%s" not in sql, name
        assert "format(" not in sql, name
        assert not re.search(r"\{\s*\}", sql), name
        for placeholder in re.findall(r"\{([^}]*)\}", sql):
            assert ":" in placeholder, f"{name} has an untyped placeholder"


def test_every_query_binds_the_identifier_it_filters_on() -> None:
    for name, sql in schema.AUDIT_QUERIES.items():
        assert "{analysis_id:String}" in sql, name
    for name, sql in schema.LIBRARY_QUERIES.items():
        assert "{project_id:String}" in sql, name


def test_queries_only_read_tables_this_schema_creates() -> None:
    for name, sql in {**schema.AUDIT_QUERIES, **schema.LIBRARY_QUERIES}.items():
        referenced = set(re.findall(r"FROM\s+([a-z_]+)", sql))
        referenced |= set(re.findall(r"JOIN\s+([a-z_]+)", sql))
        unknown = referenced - set(schema.TABLES)
        assert unknown == set(), f"{name} reads unknown tables: {unknown}"


def test_the_mirror_check_ignores_instants_missing_a_side() -> None:
    """A joint seen on one side only is not evidence of agreement."""
    assert "left_count > 0 AND right_count > 0" in schema.MIRRORED_SIDES
    assert "HAVING" in schema.MIRRORED_SIDES


def test_the_cycle_check_drops_still_steps_before_comparing_direction() -> None:
    """Matches the Python reference: zero-delta steps never count as a turn."""
    assert "WHERE direction != 0" in schema.ACYCLIC_JOINTS
    assert "previous_direction != 0" in schema.ACYCLIC_JOINTS


def test_the_first_reading_of_a_joint_cannot_invent_a_direction() -> None:
    """lagInFrame defaults to the row's own angle, so the first delta is zero."""
    assert (
        "lagInFrame(angle_degrees, 1, angle_degrees)" in schema.ACYCLIC_JOINTS
    )


def test_library_queries_read_the_deduplicated_view() -> None:
    """Without FINAL a retried run would be counted twice."""
    assert "analysis_runs FINAL" in schema.LIBRARY_VERDICTS
    assert "analysis_runs AS r FINAL" in schema.UNTRUSTED_ASSETS


def test_the_untrusted_query_is_bounded() -> None:
    assert "{limit:UInt32}" in schema.UNTRUSTED_ASSETS
    assert "verdict != 'usable'" in schema.UNTRUSTED_ASSETS
