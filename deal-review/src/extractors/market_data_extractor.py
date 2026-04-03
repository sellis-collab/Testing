from .base_extractor import BaseExtractor


class MarketDataExtractor(BaseExtractor):

    def build_prompt(self) -> str:
        return """You are an expert industrial real estate market analyst.
Extract market fundamentals and supply/demand data from this research document or report.
Return ONLY a valid JSON object with the fields below (use null for any not found).

{
  "market": "string (MSA or market name)",
  "submarket": "string",
  "market_cap_rate": number (prevailing industrial cap rate, as decimal),
  "market_vacancy_rate": number (overall vacancy, as decimal),
  "asking_rent_sf": number (average asking NNN rent per SF per year),
  "rent_growth_yoy": number (year-over-year rent growth, as decimal),
  "net_absorption_sf": number (annual net absorption in SF),
  "under_construction_sf": number (SF currently under construction),
  "new_supply_sf": number (SF delivered in past 12 months),
  "market_outlook": "string (brief qualitative summary)",
  "data_source": "string (e.g. CBRE, JLL, Cushman Q4 2024)",
  "notes": "string"
}

Return ONLY valid JSON, no other text."""
