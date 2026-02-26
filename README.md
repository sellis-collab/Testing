# Bank CSV Cleaner CLI

A small Python CLI that:

1. Cleans raw bank CSV exports into a standard transaction schema.
2. Applies rule-based categories from keyword matching.
3. Produces a monthly category summary CSV.

## Planned Repository Structure

```text
.
├── bank_cleaner/
│   ├── __init__.py
│   ├── cli.py
│   └── core.py
├── samples/
│   ├── category_rules.json
│   └── sample_bank.csv
├── tests/
│   ├── sample_data/
│   │   └── alt_layout.csv
│   └── test_cli.py
├── pyproject.toml
└── README.md
```

## Standard Output Schema

The cleaned CSV always has these columns:

- `date` (`YYYY-MM-DD`)
- `description`
- `amount` (signed decimal; expenses negative, income positive)
- `currency`
- `account`
- `category`
- `source_file`

## Rule File Format

Rules are loaded from JSON (`samples/category_rules.json`):

```json
{
  "rules": [
    {"category": "Groceries", "contains": ["wholefoods", "grocery"]},
    {"category": "Income", "contains": ["payroll", "salary"]}
  ]
}
```

The first rule with a matching `contains` keyword in the description wins. If no rule matches, category becomes `Uncategorized`.

## Installation

```bash
python -m pip install -e .
```

## Usage Examples

### 1) Run against the included sample

```bash
python -m bank_cleaner.cli samples/sample_bank.csv \
  --rules samples/category_rules.json \
  --output-clean cleaned_transactions.csv \
  --output-summary monthly_summary.csv
```

### 2) Use default filenames

```bash
python -m bank_cleaner.cli samples/sample_bank.csv --rules samples/category_rules.json
```

### 3) Override default currency when input is missing currency

```bash
python -m bank_cleaner.cli tests/sample_data/alt_layout.csv \
  --rules samples/category_rules.json \
  --default-currency EUR
```

## Testing

```bash
pytest
```
