# Skill: Excel Deal Log

## What it does

Appends a new row for a scored deal to a running Excel workbook
(`deal_log.xlsx`). If the file does not exist it is created with a formatted
header row. Each row is colour-coded by recommendation outcome.

### Columns written

Deal ID · Received Date · Property Name · Market · Submarket · Size (SF) ·
Clear Height (ft) · Land (Acres) · # Buildings · Developer / Sponsor ·
Tenant Type · Pre-Lease Status · Development Cost ($) · Cost / SF ($) ·
Investment Amount ($) · LTC / LTV (%) · Rent NNN / SF ($) ·
Yield-on-Cost (%) · Market Cap Rate (%) · Spread (bps) · IRR Levered (%) ·
IRR Unlevered (%) · Equity Multiple (x) · Hold Period (yrs) ·
GS Rent Growth (%) · GS Vacancy (%) · GS Market Score ·
Score (%) · Recommendation · Flags

### Row colour coding

| Recommendation | Background |
|---|---|
| Pursue | Light green (#C6EFCE) |
| Watch | Light amber (#FFEB9C) |
| Pass | Light red (#FFC7CE) |

## When to use

- After scoring a deal, to maintain a persistent portfolio-level deal log.
- Reviewing multiple deals side by side in Excel with consistent formatting.

## Inputs

- A scored `DealRecord`.
- Output path for the Excel file (default: `data/output/deal_log.xlsx`).

## How to invoke

```python
from src.outputs.excel_generator import ExcelGenerator

excel_gen = ExcelGenerator(output_path="data/output/deal_log.xlsx")
excel_path = excel_gen.generate(deal)   # deal is a scored DealRecord

print(excel_path)   # "data/output/deal_log.xlsx"
```

## Outputs

The Excel file at the specified path, with a new row appended for this deal.
The `Recommendation` cell is colour-coded. The first row is frozen for easy
scrolling.

## Notes

- The log is **append-only** — re-running on the same deal will add a second
  row. Deduplication (by Deal ID) is not applied automatically.
- All percentage fields are stored as plain numbers (e.g. `6.5` for 6.5%)
  for easy charting in Excel.
- Flags from failed scoring criteria are joined with ` | ` in the Flags column.
