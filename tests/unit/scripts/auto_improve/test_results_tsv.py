"""Tests for results.tsv I/O — design §4 schema enforcement."""

import pytest

from superclaude.scripts.auto_improve.results_tsv import (
    STATUS_VALUES,
    ResultRow,
    ResultsTsv,
)


@pytest.fixture
def tsv_path(tmp_path):
    return tmp_path / "results.tsv"


def test_writes_header_on_init(tsv_path):
    ResultsTsv(tsv_path).init()
    header = tsv_path.read_text().splitlines()[0]
    expected = (
        "# cycle_id\ttimestamp\tcommit_hash\tmetric_value\t"
        "status\tdesc\ttokens_used\twall_seconds"
    )
    assert header == expected


def test_appends_row_with_all_columns(tsv_path):
    tsv = ResultsTsv(tsv_path)
    tsv.init()
    row = ResultRow(
        cycle_id=1,
        timestamp="2026-04-27T02:50:00Z",
        commit_hash="a" * 40,
        metric_value=42.0,
        status="improved",
        desc="reduced lr to 1e-4",
        tokens_used=1234,
        wall_seconds=12,
    )
    tsv.append(row)
    lines = tsv_path.read_text().splitlines()
    assert len(lines) == 2
    fields = lines[1].split("\t")
    assert fields == [
        "1",
        "2026-04-27T02:50:00Z",
        "a" * 40,
        "42.0",
        "improved",
        "reduced lr to 1e-4",
        "1234",
        "12",
    ]


def test_rejects_empty_desc(tsv_path):
    tsv = ResultsTsv(tsv_path)
    tsv.init()
    with pytest.raises(ValueError, match="desc"):
        ResultRow(
            cycle_id=1,
            timestamp="2026-04-27T02:50:00Z",
            commit_hash="-",
            metric_value=0.0,
            status="mutation_error",
            desc="",
            tokens_used=0,
            wall_seconds=0,
        )


def test_status_enum_validation(tsv_path):
    valid = {
        "baseline",
        "improved",
        "regressed",
        "smoke_fail",
        "eval_timeout",
        "mutation_error",
    }
    assert valid == STATUS_VALUES
    with pytest.raises(ValueError, match="status"):
        ResultRow(
            cycle_id=0,
            timestamp="2026-04-27T02:50:00Z",
            commit_hash="-",
            metric_value=1.0,
            status="bogus",
            desc="x",
            tokens_used=0,
            wall_seconds=0,
        )


def test_desc_with_embedded_newlines_stays_single_row(tsv_path):
    """Mutator stderr can contain CRLF; desc must be sanitized so the row
    stays on one physical line and read_all() can parse it back.
    """
    tsv = ResultsTsv(tsv_path)
    tsv.init()
    multiline_desc = "claude exited 1: line1\r\nline2\nline3\twith tab"
    tsv.append(
        ResultRow(
            cycle_id=1,
            timestamp="2026-04-27T02:50:00Z",
            commit_hash="-",
            metric_value=0.0,
            status="mutation_error",
            desc=multiline_desc,
            tokens_used=0,
            wall_seconds=0,
        )
    )
    physical_lines = tsv_path.read_text(encoding="utf-8").splitlines()
    assert len(physical_lines) == 2
    rows = tsv.read_all()
    assert len(rows) == 1
    assert (
        "\n" not in rows[0].desc
        and "\t" not in rows[0].desc
        and "\r" not in rows[0].desc
    )


def test_read_all_returns_inserted_rows(tsv_path):
    tsv = ResultsTsv(tsv_path)
    tsv.init()
    for i in range(3):
        tsv.append(
            ResultRow(
                cycle_id=i,
                timestamp=f"2026-04-27T02:5{i}:00Z",
                commit_hash="-" if i == 0 else "b" * 40,
                metric_value=float(i),
                status="baseline" if i == 0 else "improved",
                desc=f"step {i}",
                tokens_used=10 * i,
                wall_seconds=i,
            )
        )
    rows = tsv.read_all()
    assert len(rows) == 3
    assert rows[0].status == "baseline"
    assert rows[2].metric_value == 2.0
