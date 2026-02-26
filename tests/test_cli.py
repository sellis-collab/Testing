from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from bank_cleaner.core import clean_transactions, load_rules, summarize_monthly

ROOT = Path(__file__).resolve().parents[1]


def test_clean_transactions_from_sample() -> None:
    rules = load_rules(ROOT / "samples" / "category_rules.json")
    rows = clean_transactions(ROOT / "samples" / "sample_bank.csv", rules)

    assert len(rows) == 4
    assert rows[0]["date"] == "2025-01-03"
    assert rows[0]["amount"] == "-54.22"
    assert rows[0]["category"] == "Groceries"
    assert rows[1]["category"] == "Income"


def test_summary_totals() -> None:
    rules = load_rules(ROOT / "samples" / "category_rules.json")
    rows = clean_transactions(ROOT / "samples" / "sample_bank.csv", rules)
    summary = summarize_monthly(rows)

    by_key = {(item["month"], item["category"]): item["total_amount"] for item in summary}
    assert by_key[("2025-01", "Income")] == "2200.00"
    assert by_key[("2025-01", "Groceries")] == "-54.22"
    assert by_key[("2025-02", "Subscriptions")] == "-15.99"


def test_cli_end_to_end(tmp_path: Path) -> None:
    input_csv = ROOT / "tests" / "sample_data" / "alt_layout.csv"
    rules = ROOT / "samples" / "category_rules.json"
    clean_out = tmp_path / "clean.csv"
    summary_out = tmp_path / "summary.csv"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "bank_cleaner.cli",
            str(input_csv),
            "--rules",
            str(rules),
            "--output-clean",
            str(clean_out),
            "--output-summary",
            str(summary_out),
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert clean_out.exists()
    assert summary_out.exists()

    with clean_out.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["category"] == "Uncategorized"
    assert rows[1]["category"] == "Income"
