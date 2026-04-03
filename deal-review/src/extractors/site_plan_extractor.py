from .base_extractor import BaseExtractor


class SitePlanExtractor(BaseExtractor):

    def build_prompt(self) -> str:
        return """You are an expert industrial real estate analyst reviewing a site plan or survey document.
Extract all available physical and site data.
Return ONLY a valid JSON object with the fields below (use null for any not found).

{
  "property_name": "string",
  "address": "string",
  "land_acres": number (total site area in acres),
  "size_sf": number (total building gross square footage),
  "num_buildings": number,
  "clear_height_ft": number (interior clear height in feet),
  "dock_doors": number (number of dock-high loading doors),
  "drive_in_doors": number (number of grade-level drive-in doors),
  "trailer_parking_spaces": number,
  "car_parking_spaces": number,
  "column_spacing": "string (e.g. 52x50 ft)",
  "building_dimensions": "string",
  "sprinkler_system": "string (e.g. ESFR, K-17)",
  "power_amps": "string (electrical service)",
  "notes": "string"
}

Return ONLY valid JSON, no other text."""
