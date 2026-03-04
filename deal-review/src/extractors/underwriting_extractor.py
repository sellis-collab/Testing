from .base_extractor import BaseExtractor


class UnderwritingExtractor(BaseExtractor):

    def build_prompt(self) -> str:
        return """You are an expert financial analyst specializing in industrial real estate underwriting.
The following is the text content of an Excel underwriting model or pro forma spreadsheet.
Extract all key financial metrics and return ONLY a valid JSON object.
If a metric appears in multiple scenarios, extract the base-case / stabilized value.

{
  "development_cost": number (total project cost in dollars),
  "cost_per_sf": number (all-in cost per SF in dollars),
  "investment_amount": number (total equity capital required in dollars),
  "ltc_ltv": number (loan-to-cost or loan-to-value as decimal, e.g. 0.65),
  "projected_rent_nnn_sf": number (annual NNN rent per SF in dollars),
  "yield_on_cost": number (stabilized NOI / total cost, as decimal),
  "market_cap_rate": number (prevailing market cap rate, as decimal),
  "spread_bps": number (yield_on_cost minus market_cap_rate in basis points),
  "irr_levered": number (levered internal rate of return, as decimal),
  "irr_unlevered": number (unlevered IRR, as decimal),
  "equity_multiple": number (e.g. 2.1 for 2.1x),
  "hold_period_years": number,
  "construction_start": "string (date or description)",
  "stabilization_date": "string",
  "size_sf": number,
  "notes": "string (note which sheet/tab each key metric was found in)"
}

Return ONLY valid JSON, no other text."""
