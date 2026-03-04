# Automated Industrial Real Estate Deal Review

Processes deal packages from Clarion Partners (or any source) and produces:
- A scored PDF report with investment thesis
- A running Excel deal log (`deal_log.xlsx`)

The system uses **Claude AI** to extract structured data from PDFs (brochures, site plans, market research) and Excel files (underwriting models, Green Street data), then applies configurable scoring criteria.

---

## Quick Start

### 1. Prerequisites

- Python 3.11+
- WeasyPrint system libraries (for PDF generation):
  - **macOS**: `brew install pango`
  - **Ubuntu/Debian**: `apt-get install python3-weasyprint`
  - **Windows**: Use WSL, or skip PDF generation (Excel output still works)

### 2. Install

```bash
cd deal-review
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### 4. Customise Scoring Criteria

Edit `config/criteria.yaml`. All lines marked `PLACEHOLDER` should be updated with your investment criteria:

```yaml
min_yield_on_cost: 0.065        # 6.5%
min_irr_levered: 0.15           # 15%
min_equity_multiple: 1.8
preferred_markets:
  - "Inland Empire"
  - "Dallas"
```

### 5. Run

**Via CLI:**
```bash
python -m src.orchestrator \
  --subject "Eastgate Logistics — Offering Memo" \
  --attachments path/to/brochure.pdf path/to/uw_model.xlsx path/to/gs_data.xlsx
```

**Via Python (when using Claude prompt as input):**
```python
from src.orchestrator import process_deal

result = process_deal(
    subject="Eastgate Logistics Park",
    attachment_paths=[
        "data/inbox/brochure.pdf",
        "data/inbox/uw_model.xlsx",
    ],
    email_body="See attached materials for the Eastgate deal in Phoenix...",
)
print(result["recommendation"])   # "Pursue", "Watch", or "Pass"
print(result["pdf_path"])         # Path to generated PDF report
```

---

## How It Works

```
Attachments provided
        │
        ▼
  Classify by filename + extension
        │
  ┌─────┴──────────────────────────────────────────┐
  │  brochure.pdf → BrochureExtractor              │
  │  site_plan.pdf / .jpg → SitePlanExtractor      │
  │  uw_model.xlsx → UnderwritingExtractor         │
  │  market_research.pdf → MarketDataExtractor     │
  │  gs_data.xlsx → GreenStreetExtractor           │
  └─────┬──────────────────────────────────────────┘
        │  Each extractor sends document to Claude
        │  and receives structured JSON back
        ▼
  Merge all extracted fields into DealRecord
  (Underwriting model values take priority)
        │
        ▼
  DealScorer: rule-based threshold checks + Claude narrative
        │
        ▼
  PDFGenerator → data/output/{id}_report.pdf
  ExcelGenerator → data/output/deal_log.xlsx
```

---

## Attachment Classification

Files are routed to extractors based on filename keywords:

| Keyword(s) in filename | Extractor |
|------------------------|-----------|
| `brochure`, `om`, `offering`, `memo` | BrochureExtractor |
| `site`, `plan`, `survey`, `plat` | SitePlanExtractor |
| `.jpg`, `.png`, `.tiff` | SitePlanExtractor |
| `model`, `uw`, `underwrite`, `proforma` | UnderwritingExtractor |
| `green`, `gs`, `greenstreet` | GreenStreetExtractor |
| `market`, `research`, `report` | MarketDataExtractor |
| Unknown PDF | BrochureExtractor (fallback) |
| Unknown Excel | UnderwritingExtractor (fallback) |

**Tip:** Name your files descriptively. E.g. `Eastgate_OM_Brochure.pdf` and `Eastgate_UW_Model_v3.xlsx` will be classified correctly.

---

## Scoring

Each deal is scored 0–100% across 8 criteria (configurable weights in `criteria.yaml`):

| Criterion | Default Weight | Pass Condition |
|-----------|---------------|----------------|
| Yield-on-Cost | 20% | ≥ min_yield_on_cost |
| IRR (Levered) | 20% | ≥ min_irr_levered |
| Spread | 15% | ≥ min_spread_bps |
| Equity Multiple | 15% | ≥ min_equity_multiple |
| Market Preference | 10% | In preferred_markets list |
| Pre-Lease Status | 10% | Contains "pre-leased" |
| LTC/LTV | 5% | ≤ max_ltc |
| Size | 5% | ≥ min_size_sf |

**Recommendation thresholds:**
- **Pursue**: ≥ 80%
- **Watch**: 60–79%
- **Pass**: < 60%

---

## Output Files

| File | Description |
|------|-------------|
| `data/output/{id}_{name}_report.pdf` | PDF deal summary report |
| `data/output/deal_log.xlsx` | Running Excel log, one row per deal, colour-coded |

---

## Project Structure

```
deal-review/
├── config/
│   ├── criteria.yaml     ← Edit this with your investment criteria
│   └── settings.yaml     ← Model and storage settings
├── src/
│   ├── orchestrator.py   ← Main entry point
│   ├── models/deal.py    ← DealRecord dataclass
│   ├── extractors/       ← Claude-powered document extractors
│   ├── scoring/          ← Criteria loading + deal scoring
│   └── outputs/          ← PDF and Excel generators
├── data/
│   └── output/           ← Generated reports (auto-created)
├── tests/
│   └── fixtures/         ← Sample files for testing
├── .env.example
├── requirements.txt
└── README.md
```

---

## Running Tests

```bash
python -m pytest tests/ -v
```

Sample fixture files can be placed in `tests/fixtures/` and referenced in tests.

---

## Troubleshooting

**WeasyPrint fails on Windows:**
Use WSL (Ubuntu) or set `SKIP_PDF=1` in `.env` and rely on Excel output only.

**JSON parse errors from Claude:**
Check your `ANTHROPIC_API_KEY` is valid and your account has quota. The system retries 3 times automatically.

**Excel extraction misses values:**
The underwriting model may use deeply nested formulas. Try renaming the file to include `uw` or `model` so it routes to `UnderwritingExtractor`. Open the file and confirm values are computed (not formula strings).

**Missing financial metrics:**
Claude returns `null` for fields it can't find. Check `extraction_notes` in the deal record for warnings.
