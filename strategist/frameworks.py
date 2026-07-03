"""Strategy framework calculators.

Pure, deterministic functions with no I/O and no LLM calls so they can be unit
tested offline. Every function returns plain dicts/lists ready for the dashboard
or the LLM synthesiser. None of these outputs is a commercial fact - they are
computed from the explicit, editable assumptions in ``config`` and the data files.
"""
from __future__ import annotations

from typing import Any, Dict, List

from . import config


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def weighted_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """Weighted average of ``scores`` using ``weights`` (weights need not be
    pre-normalised; they are normalised here)."""
    total_w = sum(weights.get(k, 0.0) for k in scores)
    if total_w == 0:
        return 0.0
    return sum(scores[k] * weights.get(k, 0.0) for k in scores) / total_w


def _band(value: float, low: float, high: float) -> str:
    if value >= high:
        return "High"
    if value >= low:
        return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# TAM / SAM / SOM funnel
# ---------------------------------------------------------------------------
def tam_sam_som(assumptions: Dict[str, Any], penetration: float | None = None) -> Dict[str, Any]:
    """Build a transparent multiplicative access funnel.

    ``penetration`` = Kisunla's captured fraction of the access-qualified
    population at maturity. If None, uses the value in ``assumptions``.
    """
    a = assumptions
    pen = penetration if penetration is not None else a["anti_amyloid_treatment_penetration_at_maturity"]

    tam = float(a["early_symptomatic_ad_population"])
    diagnosed = tam * a["clinically_diagnosed_rate"]
    sam = diagnosed * a["amyloid_confirmed_and_eligible_rate"]
    accessible = sam * a["access_to_monitoring_site_rate"] * a["payer_covered_rate"]
    som = accessible * pen

    return {
        "stages": [
            {"label": "TAM - Early symptomatic AD", "patients": round(tam)},
            {"label": "Clinically diagnosed", "patients": round(diagnosed)},
            {"label": "SAM - Amyloid-confirmed & eligible", "patients": round(sam)},
            {"label": "Access-qualified (site + payer)", "patients": round(accessible)},
            {"label": "SOM - Kisunla treated (at maturity)", "patients": round(som)},
        ],
        "tam": round(tam),
        "sam": round(sam),
        "accessible": round(accessible),
        "som": round(som),
        "penetration_used": pen,
    }


# ---------------------------------------------------------------------------
# GE-McKinsey 9-box
# ---------------------------------------------------------------------------
def ge_mckinsey(attractiveness_scores: Dict[str, float],
                strength_scores: Dict[str, float]) -> Dict[str, Any]:
    attractiveness = weighted_score(attractiveness_scores, config.MARKET_ATTRACTIVENESS_WEIGHTS)
    strength = weighted_score(strength_scores, config.COMPETITIVE_STRENGTH_WEIGHTS)

    a_band = _band(attractiveness, 2.33, 3.66)  # on a 0-5 scale
    s_band = _band(strength, 2.33, 3.66)

    # 3x3 strategy map
    strategy_map = {
        ("High", "High"): "Invest / Grow - protect and build leadership",
        ("High", "Medium"): "Invest to build - grow selectively in areas of strength",
        ("High", "Low"): "Selective build - challenge with targeted plays or partner",
        ("Medium", "High"): "Grow / protect - invest in most attractive segments",
        ("Medium", "Medium"): "Selectivity / manage for earnings",
        ("Medium", "Low"): "Limited expansion or harvest",
        ("Low", "High"): "Protect & refocus - manage for cash",
        ("Low", "Medium"): "Manage for earnings - minimal investment",
        ("Low", "Low"): "Harvest / divest",
    }
    return {
        "attractiveness": round(attractiveness, 2),
        "strength": round(strength, 2),
        "attractiveness_band": a_band,
        "strength_band": s_band,
        "cell": f"{a_band} attractiveness / {s_band} strength",
        "strategy": strategy_map[(a_band, s_band)],
        "attractiveness_scale": 5,
        "strength_scale": 5,
    }


# ---------------------------------------------------------------------------
# BCG growth-share matrix
# ---------------------------------------------------------------------------
def bcg_matrix(relative_market_share: float, market_growth_pct: float,
               share_threshold: float = 1.0, growth_threshold: float = 10.0) -> Dict[str, Any]:
    high_share = relative_market_share >= share_threshold
    high_growth = market_growth_pct >= growth_threshold

    if high_growth and high_share:
        quadrant, strategy = "Star", "Invest to sustain leadership in a growing market"
    elif high_growth and not high_share:
        quadrant, strategy = "Question Mark", "Build share selectively or exit - invest where the right to win is clear"
    elif not high_growth and high_share:
        quadrant, strategy = "Cash Cow", "Harvest and fund other bets"
    else:
        quadrant, strategy = "Dog", "Divest or minimise investment"

    return {
        "relative_market_share": relative_market_share,
        "market_growth_pct": market_growth_pct,
        "quadrant": quadrant,
        "strategy": strategy,
        "interpretation": (
            "A high-growth class with a first-mover ahead places Kisunla as a Question Mark: "
            "the disciplined call is to invest behind clear points of difference (finite-duration "
            "dosing, total cost of therapy) rather than compete head-to-head on raw efficacy."
            if quadrant == "Question Mark" else ""
        ),
    }


# ---------------------------------------------------------------------------
# Launch readiness + Go/No-Go
# ---------------------------------------------------------------------------
def launch_readiness(scores: Dict[str, float]) -> Dict[str, Any]:
    composite = weighted_score(scores, config.LAUNCH_READINESS_WEIGHTS)
    if composite >= config.GO_THRESHOLD:
        verdict = "GO"
    elif composite >= config.CONDITIONAL_GO_THRESHOLD:
        verdict = "CONDITIONAL GO"
    else:
        verdict = "NO-GO / REMEDIATE"

    # weakest pillars drive the conditions
    ranked = sorted(scores.items(), key=lambda kv: kv[1])
    weakest = [{"pillar": k, "score": v} for k, v in ranked[:3]]

    return {
        "composite": round(composite, 1),
        "verdict": verdict,
        "go_threshold": config.GO_THRESHOLD,
        "conditional_threshold": config.CONDITIONAL_GO_THRESHOLD,
        "pillar_scores": scores,
        "weakest_pillars": weakest,
    }


# ---------------------------------------------------------------------------
# Risk register
# ---------------------------------------------------------------------------
def risk_register(risks: List[Dict[str, Any]]) -> Dict[str, Any]:
    scored = []
    for r in risks:
        severity = r["likelihood"] * r["impact"]
        if severity >= 15:
            tier = "Critical"
        elif severity >= 8:
            tier = "High"
        elif severity >= 4:
            tier = "Moderate"
        else:
            tier = "Low"
        scored.append({**r, "severity": severity, "tier": tier})

    scored.sort(key=lambda x: x["severity"], reverse=True)
    return {
        "risks": scored,
        "top_risks": scored[:3],
        "critical_count": sum(1 for r in scored if r["tier"] == "Critical"),
        "high_count": sum(1 for r in scored if r["tier"] == "High"),
    }


# ---------------------------------------------------------------------------
# ROI scenarios
# ---------------------------------------------------------------------------
def roi_scenarios(accessible_patients: float,
                  scenarios: Dict[str, Dict[str, float]] | None = None,
                  costs: Dict[str, Any] | None = None) -> Dict[str, Any]:
    scenarios = scenarios or config.ROI_SCENARIOS
    costs = costs or config.ROI_COST_ASSUMPTIONS
    ramp = costs["ramp"]
    years = costs["years_modelled"]

    results = {}
    for name, s in scenarios.items():
        steady_patients = accessible_patients * s["penetration"]
        net_price = s["net_price"]
        yearly = []
        cum_ebit = 0.0
        cum_rev = 0.0
        payback_year = None
        for i in range(years):
            r = ramp[i] if i < len(ramp) else 1.0
            patients = steady_patients * r
            revenue = patients * net_price
            gross = revenue * (1 - costs["cogs_pct"])
            opex = revenue * costs["sga_pct"]
            ebit = gross - opex
            cum_ebit += ebit
            cum_rev += revenue
            if payback_year is None and cum_ebit >= costs["launch_investment_usd"]:
                payback_year = i + 1
            yearly.append({
                "year": i + 1,
                "patients": round(patients),
                "revenue_usd": round(revenue),
                "ebit_usd": round(ebit),
                "cumulative_ebit_usd": round(cum_ebit),
            })
        results[name] = {
            "steady_state_patients": round(steady_patients),
            "peak_annual_revenue_usd": round(yearly[-1]["revenue_usd"]),
            "cumulative_revenue_usd": round(cum_rev),
            "cumulative_ebit_usd": round(cum_ebit),
            "net_of_launch_investment_usd": round(cum_ebit - costs["launch_investment_usd"]),
            "payback_year": payback_year,
            "yearly": yearly,
            "assumptions": s,
        }
    return {"scenarios": results, "cost_assumptions": costs}


# ---------------------------------------------------------------------------
# 30-60-90 and 3-year roadmap (structured plans)
# ---------------------------------------------------------------------------
def thirty_sixty_ninety() -> List[Dict[str, Any]]:
    return [
        {"horizon": "Days 0-30", "focus": "Mobilise & certify", "workstreams": {
            "Regulatory/Medical": "Finalise label-aligned medical narrative; stand up MSL field plan",
            "Market Access": "Kick off CMS-registry site onboarding at top-50 centres",
            "Commercial": "Deploy account teams to certified infusion/MRI-ready sites",
            "Supply Chain": "Confirm launch-quantity supply and infusion logistics",
        }},
        {"horizon": "Days 31-60", "focus": "Enable access & demand", "workstreams": {
            "Regulatory/Medical": "KOL advisory boards; ARIA-management education rollout",
            "Market Access": "Value dossiers to commercial payers; VBC pilot outreach",
            "Commercial": "Diagnostic-referral pathways with neurology & primary care",
            "Supply Chain": "Scale infusion-center coverage by geography",
        }},
        {"horizon": "Days 61-90", "focus": "Convert & measure", "workstreams": {
            "Regulatory/Medical": "Begin RWE capture from CED registry",
            "Market Access": "First outcomes-based contract executions",
            "Commercial": "Optimise site throughput; track first-fill funnel",
            "Supply Chain": "Demand-shaping and inventory rebalancing",
        }},
    ]


def three_year_roadmap() -> List[Dict[str, Any]]:
    return [
        {"year": "Year 1", "theme": "Access-led launch",
         "objectives": ["Site certification at scale", "CED registry throughput", "Establish finite-duration value story"]},
        {"year": "Year 2", "theme": "Scale & differentiate",
         "objectives": ["Expand diagnostic funnel (plasma p-tau217)", "VBC contract expansion", "RWE publications"]},
        {"year": "Year 3", "theme": "Defend & extend",
         "objectives": ["Guideline positioning", "Ex-US access workstreams (EU/Japan/UK HTA)", "Lifecycle & next-gen delivery"]},
    ]


# ---------------------------------------------------------------------------
# KPI framework
# ---------------------------------------------------------------------------
def kpi_framework() -> Dict[str, List[Dict[str, str]]]:
    return {
        "Access": [
            {"kpi": "Certified/registry-active sites", "type": "Leading"},
            {"kpi": "Prior-auth approval rate & turnaround", "type": "Leading"},
            {"kpi": "% target population with covered access", "type": "Lagging"},
        ],
        "Diagnostic funnel": [
            {"kpi": "Amyloid-confirmation test volume", "type": "Leading"},
            {"kpi": "Referral-to-confirmation conversion", "type": "Leading"},
        ],
        "Commercial": [
            {"kpi": "First infusions / new patient starts", "type": "Lagging"},
            {"kpi": "Site throughput (patients/site/month)", "type": "Leading"},
            {"kpi": "Net revenue vs plan", "type": "Lagging"},
        ],
        "Safety/Medical": [
            {"kpi": "ARIA monitoring adherence (MRI completion)", "type": "Leading"},
            {"kpi": "Reported ARIA event rate vs label", "type": "Lagging"},
        ],
        "Value": [
            {"kpi": "Outcomes-based contracts signed", "type": "Leading"},
            {"kpi": "Average therapy duration (finite-dosing realisation)", "type": "Lagging"},
        ],
    }
