import os
from dataclasses import dataclass, field
from typing import Optional

import yaml


@dataclass
class ReportConfig:
    company_name: str = "Clarion Partners"
    logo_path: str = ""
    primary_color: str = "#1a3a5c"
    analyst_name: str = ""


@dataclass
class ScoringCriteria:
    # Quantitative thresholds
    min_yield_on_cost: float = 0.065
    max_acceptable_cap_rate: float = 0.060
    min_spread_bps: float = 75
    min_irr_levered: float = 0.15
    min_irr_unlevered: float = 0.09
    min_equity_multiple: float = 1.8
    max_ltc: float = 0.65
    min_size_sf: float = 100_000
    max_cost_per_sf: float = 175

    # Market preferences
    preferred_markets: list = field(default_factory=list)
    avoid_markets: list = field(default_factory=list)
    preferred_tenant_types: list = field(default_factory=list)

    # Scoring weights
    weights: dict = field(default_factory=lambda: {
        "yield_on_cost": 0.20,
        "irr_levered": 0.20,
        "spread": 0.15,
        "equity_multiple": 0.15,
        "market_preference": 0.10,
        "pre_lease_status": 0.10,
        "ltc": 0.05,
        "size": 0.05,
    })

    # Green Street thresholds
    gs_min_market_score: str = "B"
    gs_max_vacancy_rate: float = 0.08

    # Report settings
    report: ReportConfig = field(default_factory=ReportConfig)


class CriteriaLoader:
    DEFAULT_PATH = os.path.join(
        os.path.dirname(__file__), "..", "..", "config", "criteria.yaml"
    )

    def load(self, path: Optional[str] = None) -> ScoringCriteria:
        path = path or self.DEFAULT_PATH
        with open(path) as f:
            data = yaml.safe_load(f)

        report_data = data.pop("report", {})
        report = ReportConfig(**report_data) if report_data else ReportConfig()

        criteria = ScoringCriteria(**{k: v for k, v in data.items() if k != "report"})
        criteria.report = report
        return criteria
