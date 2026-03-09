# Skill: Deal Scoring

## What it does

Applies rule-based threshold checks across 8 weighted criteria to score a
deal 0–100%, assigns a **Pursue / Watch / Pass** recommendation, and generates
a concise investment thesis narrative via Claude.

### Scoring criteria (default weights)

| Criterion | Weight | Pass condition |
|---|---|---|
| Yield-on-Cost | 20% | ≥ `min_yield_on_cost` (default 6.5%) |
| IRR (Levered) | 20% | ≥ `min_irr_levered` (default 15%) |
| Spread | 15% | ≥ `min_spread_bps` (default 75 bps) |
| Equity Multiple | 15% | ≥ `min_equity_multiple` (default 1.8×) |
| Market Preference | 10% | In `preferred_markets` list |
| Pre-Lease Status | 10% | Contains "pre-leased" / "credit" |
| LTC / LTV | 5% | ≤ `max_ltc` (default 65%) |
| Size | 5% | ≥ `min_size_sf` (default 100,000 SF) |

### Recommendation thresholds

| Score | Recommendation |
|---|---|
| ≥ 80% | **Pursue** |
| 60–79% | **Watch** |
| < 60% | **Pass** |

Spread is computed automatically as `(yield_on_cost − market_cap_rate) × 10,000`
if not already present in the deal record.

## When to use

- A `DealRecord` has been populated (by the Document Extraction skill or
  manually) and you need a scored recommendation.
- You want to adjust scoring weights or thresholds for a specific fund mandate.

## Inputs

- A populated `DealRecord` object.
- Scoring criteria loaded from `config/criteria.yaml` (edit thresholds and
  weights there).

## How to invoke

```python
from src.scoring.criteria_loader import CriteriaLoader
from src.scoring.deal_scorer import DealScorer

criteria = CriteriaLoader().load()          # reads config/criteria.yaml
scorer = DealScorer(criteria)
deal = scorer.score(deal)                   # deal is a DealRecord

print(deal.score_total)       # e.g. 73.5
print(deal.recommendation)   # "Pursue" | "Watch" | "Pass"
print(deal.investment_thesis) # Claude-generated narrative
print(deal.score_flags)       # list of failed criteria
```

## Outputs

Updates the `DealRecord` in-place with:

- `score_total` — percentage score (0–100)
- `score_breakdown` — dict of criterion → earned weight
- `score_flags` — list of failed or missing criteria messages
- `recommendation` — "Pursue", "Watch", or "Pass"
- `investment_thesis` — 3–5 sentence narrative from Claude

## Configuration

Edit `config/criteria.yaml` to change thresholds, weights, preferred markets,
and avoid markets. All percentage values are decimals (e.g. `0.065` = 6.5%).

```yaml
min_yield_on_cost: 0.065
min_irr_levered: 0.15
min_equity_multiple: 1.8
preferred_markets:
  - "Inland Empire"
  - "Dallas"
weights:
  yield_on_cost: 0.20
  irr_levered: 0.20
  ...
```
