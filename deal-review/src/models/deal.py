from dataclasses import dataclass, field
from typing import Optional
from datetime import date


@dataclass
class DealRecord:
    # --- Identity ---
    deal_id: str = ""
    source_email_subject: str = ""
    received_date: Optional[date] = None

    # --- Location & Property ---
    market: str = ""
    submarket: str = ""
    property_name: str = ""
    address: str = ""

    # --- Physical Metrics ---
    size_sf: Optional[float] = None
    clear_height_ft: Optional[float] = None
    land_acres: Optional[float] = None
    num_buildings: Optional[int] = None

    # --- Parties ---
    developer_sponsor: str = ""
    tenant_type: str = ""       # e.g. "single-tenant NNN", "multi-tenant"
    pre_lease_status: str = ""  # e.g. "100% pre-leased", "speculative"

    # --- Financial: Development ---
    development_cost: Optional[float] = None
    cost_per_sf: Optional[float] = None
    investment_amount: Optional[float] = None   # equity required
    ltc_ltv: Optional[float] = None             # decimal, e.g. 0.65

    # --- Financial: Returns ---
    projected_rent_nnn_sf: Optional[float] = None
    yield_on_cost: Optional[float] = None       # decimal
    market_cap_rate: Optional[float] = None     # decimal
    spread_bps: Optional[float] = None          # yield_on_cost minus market_cap_rate in bps
    irr_levered: Optional[float] = None         # decimal
    irr_unlevered: Optional[float] = None       # decimal
    equity_multiple: Optional[float] = None

    # --- Timeline ---
    construction_start: Optional[str] = None
    stabilization_date: Optional[str] = None
    hold_period_years: Optional[float] = None

    # --- Green Street Data ---
    gs_market_rent_growth: Optional[float] = None   # decimal
    gs_vacancy_rate: Optional[float] = None          # decimal
    gs_market_score: Optional[str] = None            # e.g. "A", "B+", "C"

    # --- Scoring Output (populated by DealScorer) ---
    score_total: Optional[float] = None
    score_breakdown: dict = field(default_factory=dict)
    score_flags: list = field(default_factory=list)
    recommendation: str = ""       # "Pursue", "Watch", or "Pass"
    investment_thesis: str = ""    # Claude-generated narrative

    # --- Extraction Metadata ---
    extraction_notes: list = field(default_factory=list)

    def merge(self, data: dict, source: str = "") -> None:
        """
        Merge a dict of extracted values into this record.
        Only overwrites fields that are currently None / empty.
        Exception: financial metrics from the underwriting model are
        always written (caller sets source="uw" to force overwrite).
        """
        force = source == "uw"
        for key, value in data.items():
            if key.startswith("_") or value is None:
                continue
            current = getattr(self, key, None)
            if force or current is None or current == "" or current == []:
                try:
                    setattr(self, key, value)
                except AttributeError:
                    pass
