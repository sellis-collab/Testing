# Skill: Document Extraction

## What it does

Classifies deal package attachments by filename and routes each file to the
appropriate Claude-powered extractor. Returns structured JSON fields merged
into a `DealRecord`.

Supported file types and their extractors:

| File pattern | Extractor |
|---|---|
| `*brochure*`, `*om*`, `*offering*`, `*memo*` (PDF) | BrochureExtractor |
| `*site*`, `*plan*`, `*survey*`, `*plat*` (PDF) | SitePlanExtractor |
| `.jpg`, `.png`, `.tiff`, `.webp` | SitePlanExtractor |
| `*model*`, `*uw*`, `*underwrite*`, `*proforma*` (Excel) | UnderwritingExtractor |
| `*green*`, `*gs*`, `*greenstreet*` (Excel) | GreenStreetExtractor |
| `*market*`, `*research*`, `*report*`, `*cbre*`, `*jll*` (PDF/Excel) | MarketDataExtractor |
| Unknown PDF | BrochureExtractor (fallback) |
| Unknown Excel | UnderwritingExtractor (fallback) |

Underwriting model values override all other sources when fields conflict.

## When to use

- You have received a deal package with one or more attachments (PDFs, Excel
  models, site plan images).
- You need structured financial and property data before scoring.

## Inputs

- One or more file paths to attachments (PDF, Excel, or image).
- Optionally, an email body string for supplementary context.

## How to invoke

```python
from src.extractors.attachment_handler import classify_and_extract

extracted_data, source_label = classify_and_extract("path/to/file.pdf")
# extracted_data: dict of field → value
# source_label:   "brochure" | "site_plan" | "uw" | "green_street" | "market"
```

Or as part of the full pipeline via `process_deal()` — see the
`full-pipeline` skill.

## Outputs

A `dict` of extracted fields (property name, market, size, financial metrics,
etc.) and a `source_label` string. Fields not found in the document are
returned as `null`. A `_parse_error` key is present if Claude could not parse
the response.

## Tips

- Name files descriptively so classification is accurate, e.g.
  `Eastgate_OM_Brochure.pdf` and `Eastgate_UW_Model_v3.xlsx`.
- If values are missing, check `extraction_notes` on the `DealRecord` for
  Claude's explanation.
- The system retries Claude API calls 3 times automatically on failure.
