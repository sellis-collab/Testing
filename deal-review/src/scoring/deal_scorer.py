import logging
import os

import anthropic

from ..models.deal import DealRecord
from .criteria_loader import ScoringCriteria

logger = logging.getLogger(__name__)

MODEL = os.getenv("CLAUDE_MODEL", "claude-opus-4-6")
MAX_TOKENS_SCORING = int(os.getenv("CLAUDE_MAX_TOKENS_SCORING", "1000"))

# Grade mapping for Green Street scores
GS_GRADE_ORDER = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D"]


class DealScorer:

    def __init__(self, criteria: ScoringCriteria):
        self.criteria = criteria
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def score(self, deal: DealRecord) -> DealRecord:
        c = self.criteria
        flags = []
        breakdown = {}

        # --- Yield on Cost ---
        if deal.yield_on_cost is not None:
            if deal.yield_on_cost >= c.min_yield_on_cost:
                breakdown["yield_on_cost"] = c.weights.get("yield_on_cost", 0.20)
            else:
                breakdown["yield_on_cost"] = 0
                flags.append(
                    f"Yield-on-cost {deal.yield_on_cost:.1%} below minimum {c.min_yield_on_cost:.1%}"
                )
        else:
            flags.append("Yield-on-cost not available")

        # --- Levered IRR ---
        if deal.irr_levered is not None:
            if deal.irr_levered >= c.min_irr_levered:
                breakdown["irr_levered"] = c.weights.get("irr_levered", 0.20)
            else:
                breakdown["irr_levered"] = 0
                flags.append(
                    f"Levered IRR {deal.irr_levered:.1%} below minimum {c.min_irr_levered:.1%}"
                )
        else:
            flags.append("Levered IRR not available")

        # --- Spread (bps) ---
        # Compute spread if not already present
        if deal.spread_bps is None and deal.yield_on_cost and deal.market_cap_rate:
            deal.spread_bps = (deal.yield_on_cost - deal.market_cap_rate) * 10_000

        if deal.spread_bps is not None:
            if deal.spread_bps >= c.min_spread_bps:
                breakdown["spread"] = c.weights.get("spread", 0.15)
            else:
                breakdown["spread"] = 0
                flags.append(
                    f"Spread {deal.spread_bps:.0f} bps below minimum {c.min_spread_bps:.0f} bps"
                )
        else:
            flags.append("Spread not available (missing yield or cap rate)")

        # --- Equity Multiple ---
        if deal.equity_multiple is not None:
            if deal.equity_multiple >= c.min_equity_multiple:
                breakdown["equity_multiple"] = c.weights.get("equity_multiple", 0.15)
            else:
                breakdown["equity_multiple"] = 0
                flags.append(
                    f"Equity multiple {deal.equity_multiple:.2f}x below minimum {c.min_equity_multiple:.2f}x"
                )
        else:
            flags.append("Equity multiple not available")

        # --- Market preference ---
        market_normalized = (deal.market or "").lower()
        preferred_normalized = [m.lower() for m in c.preferred_markets]
        avoided_normalized = [m.lower() for m in c.avoid_markets]

        if any(m in market_normalized for m in avoided_normalized):
            breakdown["market_preference"] = 0
            flags.append(f"Market '{deal.market}' is on the avoid list")
        elif any(m in market_normalized for m in preferred_normalized):
            breakdown["market_preference"] = c.weights.get("market_preference", 0.10)
        else:
            breakdown["market_preference"] = c.weights.get("market_preference", 0.10) * 0.5
            flags.append(f"Market '{deal.market}' not in preferred list (partial credit)")

        # --- Pre-lease status ---
        pre_lease = (deal.pre_lease_status or "").lower()
        if "pre-leased" in pre_lease or "preleased" in pre_lease or "credit" in pre_lease:
            breakdown["pre_lease_status"] = c.weights.get("pre_lease_status", 0.10)
        elif "spec" in pre_lease:
            breakdown["pre_lease_status"] = 0
            flags.append("Speculative (no pre-lease) increases risk")
        else:
            breakdown["pre_lease_status"] = c.weights.get("pre_lease_status", 0.10) * 0.5

        # --- LTC/LTV ---
        if deal.ltc_ltv is not None:
            if deal.ltc_ltv <= c.max_ltc:
                breakdown["ltc"] = c.weights.get("ltc", 0.05)
            else:
                breakdown["ltc"] = 0
                flags.append(
                    f"LTC/LTV {deal.ltc_ltv:.1%} exceeds maximum {c.max_ltc:.1%}"
                )
        else:
            flags.append("LTC/LTV not available")

        # --- Size ---
        if deal.size_sf is not None:
            if deal.size_sf >= c.min_size_sf:
                breakdown["size"] = c.weights.get("size", 0.05)
            else:
                breakdown["size"] = 0
                flags.append(
                    f"Size {deal.size_sf:,.0f} SF below minimum {c.min_size_sf:,.0f} SF"
                )
        else:
            flags.append("Building size not available")

        # --- Score total ---
        total_weight = sum(c.weights.values()) or 1.0
        earned_weight = sum(breakdown.values())
        score_pct = (earned_weight / total_weight) * 100

        # --- Recommendation ---
        if score_pct >= 80:
            recommendation = "Pursue"
        elif score_pct >= 60:
            recommendation = "Watch"
        else:
            recommendation = "Pass"

        deal.score_breakdown = breakdown
        deal.score_flags = flags
        deal.score_total = round(score_pct, 1)
        deal.recommendation = recommendation

        # --- Claude narrative ---
        deal.investment_thesis = self._generate_thesis(deal, flags)

        return deal

    def _generate_thesis(self, deal: DealRecord, flags: list) -> str:
        def fmt_pct(v):
            return f"{v:.1%}" if v is not None else "N/A"

        def fmt_num(v, fmt=".2f"):
            return format(v, fmt) if v is not None else "N/A"

        summary = f"""
Property: {deal.property_name or 'Unknown'} | {deal.market or 'Unknown market'}, {deal.submarket or ''}
Size: {f"{deal.size_sf:,.0f} SF" if deal.size_sf else "N/A"} | Clear height: {deal.clear_height_ft or "N/A"} ft
Developer/Sponsor: {deal.developer_sponsor or "N/A"}
Pre-lease: {deal.pre_lease_status or "N/A"} | Tenant type: {deal.tenant_type or "N/A"}

Key returns:
  Yield-on-cost: {fmt_pct(deal.yield_on_cost)}
  Market cap rate: {fmt_pct(deal.market_cap_rate)}
  Spread: {f"{deal.spread_bps:.0f} bps" if deal.spread_bps is not None else "N/A"}
  IRR (levered): {fmt_pct(deal.irr_levered)}
  IRR (unlevered): {fmt_pct(deal.irr_unlevered)}
  Equity multiple: {fmt_num(deal.equity_multiple)}x
  LTC/LTV: {fmt_pct(deal.ltc_ltv)}

Development cost: ${f"{deal.development_cost:,.0f}" if deal.development_cost is not None else "N/A"} | Cost/SF: ${f"{deal.cost_per_sf:.0f}" if deal.cost_per_sf is not None else "N/A"}/SF
Score: {deal.score_total}% → {deal.recommendation}
Flags: {', '.join(flags) if flags else 'None'}
""".strip()

        try:
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS_SCORING,
                messages=[{
                    "role": "user",
                    "content": (
                        "You are an industrial real estate investment analyst at a major institutional fund. "
                        "Given the deal summary below, write a concise 3-5 sentence investment thesis covering: "
                        "(1) the key investment merits, (2) the main risks or concerns, and (3) your recommendation. "
                        "Be direct and specific — do not use filler phrases.\n\n"
                        + summary
                    ),
                }],
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.warning(f"Claude narrative generation failed: {e}")
            return f"Narrative unavailable ({e})"
