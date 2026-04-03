# Skill: Full Deal Review Pipeline

## What it does

Runs the complete end-to-end automated deal review in a single call:

```
Attachments → Extract → Merge into DealRecord → Score → PDF Report + Excel Log
```

1. **Extract** — each attachment is classified and sent to Claude for
   structured data extraction (see `document-extraction` skill).
2. **Merge** — all extracted fields are merged into a single `DealRecord`;
   underwriting model values take priority over other sources.
3. **Score** — rule-based thresholds are applied across 8 criteria and a
   Claude-generated investment thesis is produced (see `deal-scoring` skill).
4. **Output** — a PDF report and an updated Excel deal log are written to the
   output directory (see `pdf-report` and `excel-deal-log` skills).

## When to use

- You have received a deal package and want a scored recommendation and
  formatted outputs in one step.
- Running from the command line or integrating into an email automation.

## Inputs

| Parameter | Type | Required | Description |
|---|---|---|---|
| `subject` | str | Yes | Email subject / property name (fallback) |
| `attachment_paths` | list[str] | Yes | Local file paths to attachments |
| `email_body` | str | No | Plain-text email body for extra context |
| `received_date` | date | No | Defaults to today |
| `output_dir` | str | No | Defaults to `data/output/` |

## How to invoke

**Python:**

```python
from src.orchestrator import process_deal

result = process_deal(
    subject="Eastgate Logistics Park — Offering Memo",
    attachment_paths=[
        "data/inbox/Eastgate_OM_Brochure.pdf",
        "data/inbox/Eastgate_UW_Model_v3.xlsx",
        "data/inbox/Eastgate_GS_Data.xlsx",
    ],
    email_body="Please review the attached deal package for Eastgate in Phoenix.",
)

print(result["recommendation"])    # "Pursue" | "Watch" | "Pass"
print(result["score_total"])       # e.g. 78.5
print(result["investment_thesis"]) # Claude narrative
print(result["pdf_path"])          # path to PDF report
print(result["excel_path"])        # path to deal_log.xlsx
```

**CLI:**

```bash
python -m src.orchestrator \
  --subject "Eastgate Logistics Park — Offering Memo" \
  --attachments data/inbox/Eastgate_OM_Brochure.pdf \
                data/inbox/Eastgate_UW_Model_v3.xlsx \
  --body "Phoenix deal, see attachments." \
  --output-dir data/output
```

## Outputs

`result` dict returned by `process_deal()`:

| Key | Description |
|---|---|
| `deal_id` | Auto-generated 8-char uppercase ID |
| `property_name` | Extracted property name |
| `recommendation` | "Pursue", "Watch", or "Pass" |
| `score_total` | Percentage score (0–100) |
| `flags` | List of failed/missing criteria |
| `investment_thesis` | Claude-generated 3–5 sentence narrative |
| `pdf_path` | Path to generated PDF (None if WeasyPrint unavailable) |
| `excel_path` | Path to updated Excel deal log |

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Required. Your Anthropic API key. |
| `CLAUDE_MODEL` | `claude-opus-4-6` | Claude model for extraction and scoring |
| `OUTPUT_DIR` | `data/output` | Default output directory |
| `SKIP_PDF` | — | Set to `1` to skip PDF generation |

Copy `.env.example` to `.env` and fill in your key before running.

## File naming tips

Name attachments descriptively so the classifier routes them correctly:

| Good name | Extractor used |
|---|---|
| `Eastgate_OM_Brochure.pdf` | BrochureExtractor |
| `Eastgate_UW_Model_v3.xlsx` | UnderwritingExtractor |
| `Eastgate_GS_Data.xlsx` | GreenStreetExtractor |
| `Eastgate_Site_Plan.pdf` | SitePlanExtractor |
| `CBRE_Market_Report_Phoenix.pdf` | MarketDataExtractor |
