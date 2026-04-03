# Skill: PDF Report Generation

## What it does

Renders a branded, styled PDF deal summary report from a scored `DealRecord`.
The report includes property details, key financial metrics, score breakdown,
flags, and the Claude-generated investment thesis. Score colour is
automatically applied (green / amber / red).

## When to use

- A deal has been scored and you want a shareable single-page PDF summary.
- Sending a deal to partners, investment committee, or filing for records.

## Inputs

- A scored `DealRecord` (must have `score_total` and `recommendation`).
- Scoring criteria (for company name and brand colour from `criteria.yaml`).
- An output directory path (default: `data/output/`).

## How to invoke

```python
from src.outputs.pdf_generator import PDFGenerator
from src.scoring.criteria_loader import CriteriaLoader

criteria = CriteriaLoader().load()
pdf_gen = PDFGenerator(output_dir="data/output", criteria=criteria)
pdf_path = pdf_gen.generate(deal)   # deal is a scored DealRecord

print(pdf_path)   # e.g. "data/output/A1B2C3D4_Eastgate_report.pdf"
```

## Outputs

A PDF file at `data/output/{deal_id}_{property_name}_report.pdf`.

Score badge colour:
- **Green** (#27ae60) — Pursue (≥ 80%)
- **Amber** (#e67e22) — Watch (60–79%)
- **Red** (#c0392b) — Pass (< 60%)

## Dependencies

Requires **WeasyPrint** and its system libraries:

| Platform | Install |
|---|---|
| macOS | `brew install pango` |
| Ubuntu/Debian | `apt-get install python3-weasyprint` |
| Windows | Use WSL, or skip PDF and rely on Excel output |

Set `SKIP_PDF=1` in `.env` to suppress PDF generation without errors.

## Customisation

- **Template**: `src/outputs/templates/report.html` (Jinja2).
- **Company name / logo / colour**: `config/criteria.yaml` → `report:` section.

```yaml
report:
  company_name: "Clarion Partners"
  logo_path: "assets/logo.png"
  primary_color: "#1a3a5c"
  analyst_name: "Jane Smith"
```
