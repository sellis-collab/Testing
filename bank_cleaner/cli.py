from __future__ import annotations

import argparse
from pathlib import Path

from .core import clean_transactions, load_rules, summarize_monthly, write_clean_csv, write_summary_csv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean bank CSV files into a standard schema and produce monthly summaries.")
    parser.add_argument("input_csv", type=Path, help="Path to input bank CSV")
    parser.add_argument("--rules", type=Path, required=True, help="JSON file containing category rules")
    parser.add_argument("--output-clean", type=Path, default=Path("cleaned_transactions.csv"), help="Output cleaned CSV path")
    parser.add_argument("--output-summary", type=Path, default=Path("monthly_summary.csv"), help="Output monthly summary CSV path")
    parser.add_argument("--default-currency", default="USD", help="Default currency when missing")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    rules = load_rules(args.rules)
    rows = clean_transactions(args.input_csv, rules, default_currency=args.default_currency)
    write_clean_csv(rows, args.output_clean)

    summary_rows = summarize_monthly(rows)
    write_summary_csv(summary_rows, args.output_summary)

    print(f"Wrote {len(rows)} cleaned transactions to {args.output_clean}")
    print(f"Wrote {len(summary_rows)} monthly summary rows to {args.output_summary}")


if __name__ == "__main__":
    main()
