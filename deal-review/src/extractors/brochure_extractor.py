from .base_extractor import BaseExtractor


class BrochureExtractor(BaseExtractor):

    def build_prompt(self) -> str:
        return """You are an expert industrial real estate analyst.
Extract all available data from this marketing brochure or offering memorandum.
Return ONLY a valid JSON object with the fields below (use null for any not found).

{
  "property_name": "string",
  "address": "string",
  "market": "string (e.g. Inland Empire, Dallas, Phoenix)",
  "submarket": "string",
  "developer_sponsor": "string",
  "size_sf": number (total building square footage),
  "clear_height_ft": number,
  "land_acres": number,
  "num_buildings": number,
  "tenant_type": "string (e.g. single-tenant NNN, multi-tenant)",
  "pre_lease_status": "string (e.g. 100% pre-leased, speculative)",
  "projected_rent_nnn_sf": number (annual NNN rent per SF in dollars),
  "development_cost": number (total project cost in dollars),
  "cost_per_sf": number (all-in cost per SF in dollars),
  "yield_on_cost": number (as decimal, e.g. 0.065),
  "market_cap_rate": number (as decimal),
  "construction_start": "string",
  "stabilization_date": "string",
  "hold_period_years": number,
  "notes": "string (any additional context worth noting)"
}

Return ONLY valid JSON, no other text."""
