from .base_extractor import BaseExtractor


class GreenStreetExtractor(BaseExtractor):

    def build_prompt(self) -> str:
        return """You are an expert industrial real estate analyst reviewing Green Street Advisors data.
Extract all relevant market scores, rent forecasts, and demand metrics.
Return ONLY a valid JSON object with the fields below (use null for any not found).

{
  "market": "string (MSA or market name)",
  "submarket": "string",
  "gs_market_score": "string (Green Street grade, e.g. A, B+, B, C)",
  "gs_market_rent_growth": number (projected annual rent growth, as decimal),
  "gs_vacancy_rate": number (market vacancy rate, as decimal),
  "gs_supply_score": "string",
  "gs_demand_score": "string",
  "gs_total_return_forecast": number (as decimal),
  "gs_cap_rate": number (Green Street cap rate estimate, as decimal),
  "gs_commentary": "string (any qualitative notes from Green Street)",
  "report_date": "string",
  "notes": "string"
}

Return ONLY valid JSON, no other text."""
