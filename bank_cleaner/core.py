from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional


DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%d-%m-%Y"]

FIELD_ALIASES = {
    "date": {"date", "transaction_date", "posted_date", "booking_date"},
    "description": {"description", "details", "memo", "narrative", "payee"},
    "amount": {"amount", "transaction_amount", "value"},
    "debit": {"debit", "withdrawal", "outflow", "money_out"},
    "credit": {"credit", "deposit", "inflow", "money_in"},
    "currency": {"currency", "ccy"},
    "account": {"account", "account_name", "account_number"},
}


@dataclass
class CategoryRule:
    category: str
    contains: List[str]


def _normalize_header(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def _parse_date(value: str) -> str:
    raw = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value!r}")


def _parse_amount(value: str) -> float:
    cleaned = value.strip().replace(",", "")
    cleaned = cleaned.replace("$", "")
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = f"-{cleaned[1:-1]}"
    return float(cleaned)


def _match_header(headers: Iterable[str], target: str) -> Optional[str]:
    candidates = FIELD_ALIASES[target]
    for header in headers:
        if _normalize_header(header) in candidates:
            return header
    return None


def load_rules(path: Path) -> List[CategoryRule]:
    payload = json.loads(path.read_text())
    rules = []
    for entry in payload.get("rules", []):
        rules.append(
            CategoryRule(
                category=entry["category"],
                contains=[s.lower() for s in entry.get("contains", [])],
            )
        )
    return rules


def apply_category(description: str, rules: List[CategoryRule]) -> str:
    text = description.lower()
    for rule in rules:
        for snippet in rule.contains:
            if snippet and snippet in text:
                return rule.category
    return "Uncategorized"


def clean_transactions(input_path: Path, rules: List[CategoryRule], default_currency: str = "USD") -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with input_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames or []

        date_h = _match_header(headers, "date")
        desc_h = _match_header(headers, "description")
        amount_h = _match_header(headers, "amount")
        debit_h = _match_header(headers, "debit")
        credit_h = _match_header(headers, "credit")
        currency_h = _match_header(headers, "currency")
        account_h = _match_header(headers, "account")

        if not date_h or not desc_h:
            raise ValueError("CSV must include recognizable date and description columns")
        if not amount_h and not (debit_h and credit_h):
            raise ValueError("CSV must include amount or both debit/credit columns")

        for raw_row in reader:
            description = raw_row.get(desc_h, "").strip()
            if not description:
                continue

            if amount_h:
                amount = _parse_amount(raw_row.get(amount_h, "0"))
            else:
                debit = _parse_amount(raw_row.get(debit_h, "0") or "0")
                credit = _parse_amount(raw_row.get(credit_h, "0") or "0")
                amount = credit - debit

            normalized = {
                "date": _parse_date(raw_row.get(date_h, "")),
                "description": re.sub(r"\s+", " ", description),
                "amount": f"{amount:.2f}",
                "currency": (raw_row.get(currency_h, "") if currency_h else "").strip() or default_currency,
                "account": (raw_row.get(account_h, "") if account_h else "").strip() or "Unknown",
                "category": apply_category(description, rules),
                "source_file": input_path.name,
            }
            rows.append(normalized)
    return rows


def write_clean_csv(rows: List[Dict[str, str]], output_path: Path) -> None:
    fieldnames = ["date", "description", "amount", "currency", "account", "category", "source_file"]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_monthly(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    summary: Dict[tuple, float] = defaultdict(float)
    for row in rows:
        month = row["date"][:7]
        key = (month, row["category"])
        summary[key] += float(row["amount"])

    output = [
        {"month": month, "category": category, "total_amount": f"{total:.2f}"}
        for (month, category), total in sorted(summary.items())
    ]
    return output


def write_summary_csv(summary_rows: List[Dict[str, str]], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["month", "category", "total_amount"])
        writer.writeheader()
        writer.writerows(summary_rows)
