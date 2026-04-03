"""
Basic extractor tests.
Place sample files in tests/fixtures/ to enable file-based tests.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_parse_response_clean_json():
    from src.extractors.base_extractor import BaseExtractor

    class DummyExtractor(BaseExtractor):
        def build_prompt(self):
            return "test"

    e = DummyExtractor()
    result = e._parse_response('{"property_name": "Eastgate", "size_sf": 250000}')
    assert result["property_name"] == "Eastgate"
    assert result["size_sf"] == 250000


def test_parse_response_with_code_fences():
    from src.extractors.base_extractor import BaseExtractor

    class DummyExtractor(BaseExtractor):
        def build_prompt(self):
            return "test"

    e = DummyExtractor()
    raw = '```json\n{"market": "Dallas", "yield_on_cost": 0.068}\n```'
    result = e._parse_response(raw)
    assert result["market"] == "Dallas"
    assert result["yield_on_cost"] == pytest.approx(0.068)


def test_parse_response_invalid_json():
    from src.extractors.base_extractor import BaseExtractor

    class DummyExtractor(BaseExtractor):
        def build_prompt(self):
            return "test"

    e = DummyExtractor()
    result = e._parse_response("This is not JSON at all.")
    assert "_parse_error" in result


def test_deal_record_merge_basic():
    from src.models.deal import DealRecord

    deal = DealRecord(deal_id="TEST01")
    deal.merge({"property_name": "Eastgate", "size_sf": 300000}, source="brochure")
    assert deal.property_name == "Eastgate"
    assert deal.size_sf == 300000


def test_deal_record_merge_no_overwrite():
    from src.models.deal import DealRecord

    deal = DealRecord(deal_id="TEST01", property_name="Original Name")
    deal.merge({"property_name": "New Name"}, source="brochure")
    # Should NOT overwrite because source != "uw"
    assert deal.property_name == "Original Name"


def test_deal_record_merge_uw_overwrite():
    from src.models.deal import DealRecord

    deal = DealRecord(deal_id="TEST01", yield_on_cost=0.060)
    deal.merge({"yield_on_cost": 0.072}, source="uw")
    # Underwriting model should force-overwrite financials
    assert deal.yield_on_cost == pytest.approx(0.072)


def test_criteria_loader_defaults():
    from src.scoring.criteria_loader import CriteriaLoader

    criteria = CriteriaLoader().load()
    assert criteria.min_yield_on_cost > 0
    assert criteria.min_irr_levered > 0
    assert isinstance(criteria.preferred_markets, list)
    assert abs(sum(criteria.weights.values()) - 1.0) < 0.01


def test_deal_scorer_recommendation():
    from src.models.deal import DealRecord
    from src.scoring.criteria_loader import CriteriaLoader
    from src.scoring.deal_scorer import DealScorer

    criteria = CriteriaLoader().load()
    scorer = DealScorer(criteria)

    # Build a deal that should easily pass
    deal = DealRecord(
        deal_id="TEST02",
        property_name="Strong Deal",
        market="Dallas",
        size_sf=500_000,
        yield_on_cost=0.075,
        market_cap_rate=0.055,
        spread_bps=200,
        irr_levered=0.18,
        irr_unlevered=0.11,
        equity_multiple=2.1,
        ltc_ltv=0.60,
        pre_lease_status="100% pre-leased to credit tenant",
    )

    result = scorer.score(deal)
    assert result.recommendation in ("Pursue", "Watch")
    assert result.score_total > 60


def test_excel_generator_creates_file(tmp_path):
    from src.models.deal import DealRecord
    from src.outputs.excel_generator import ExcelGenerator

    deal = DealRecord(
        deal_id="XL01",
        property_name="Test Property",
        market="Phoenix",
        size_sf=200_000,
        score_total=75.0,
        recommendation="Watch",
    )

    output_path = str(tmp_path / "test_log.xlsx")
    gen = ExcelGenerator(output_path=output_path)
    result_path = gen.generate(deal)

    assert os.path.exists(result_path)

    import openpyxl
    wb = openpyxl.load_workbook(result_path)
    ws = wb.active
    assert ws.max_row == 2  # header + 1 data row
