"""Orchestrator: turn grounded data + editable assumptions into a full launch
decision package, then (optionally) narrate it with the LLM.

``build_analysis`` is pure and offline. ``build_briefing`` adds the narrative,
falling back to a deterministic template when no LLM key is present.
"""
from __future__ import annotations

import copy
from typing import Any, Dict, Optional

from . import config, data_loader, frameworks, llm


def build_analysis(overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run every framework and return one structured analysis dict.

    ``overrides`` may contain any of: market_assumptions, attractiveness_scores,
    strength_scores, readiness_scores, risks, bcg (relative_market_share,
    market_growth_pct), roi_scenarios.
    """
    overrides = overrides or {}
    data = data_loader.load_all()

    market_assumptions = copy.deepcopy(
        data["competitors"]["market_sizing_assumptions_us"])
    market_assumptions.update(overrides.get("market_assumptions", {}))

    attractiveness = {**config.DEFAULT_MARKET_ATTRACTIVENESS_SCORES,
                      **overrides.get("attractiveness_scores", {})}
    strength = {**config.DEFAULT_COMPETITIVE_STRENGTH_SCORES,
                **overrides.get("strength_scores", {})}
    readiness = {**config.DEFAULT_LAUNCH_READINESS_SCORES,
                 **overrides.get("readiness_scores", {})}
    risks = overrides.get("risks", config.DEFAULT_RISKS)

    bcg_in = {"relative_market_share": 0.6, "market_growth_pct": 25.0}
    bcg_in.update(overrides.get("bcg", {}))

    funnel = frameworks.tam_sam_som(market_assumptions)
    roi = frameworks.roi_scenarios(
        funnel["accessible"], overrides.get("roi_scenarios"))

    analysis = {
        "meta": {
            "app": config.APP_TITLE,
            "compliance": config.COMPLIANCE_BANNER,
            "drug": data["profile"]["brand_name"],
            "indication": data["profile"]["indication"],
        },
        "profile": data["profile"],
        "competitors": data["competitors"],
        "payers": data["payers"],
        "market_funnel": funnel,
        "ge_mckinsey": frameworks.ge_mckinsey(attractiveness, strength),
        "bcg": frameworks.bcg_matrix(**bcg_in),
        "launch_readiness": frameworks.launch_readiness(readiness),
        "risk_register": frameworks.risk_register(risks),
        "roi": roi,
        "roadmap_30_60_90": frameworks.thirty_sixty_ninety(),
        "roadmap_3_year": frameworks.three_year_roadmap(),
        "kpi_framework": frameworks.kpi_framework(),
    }
    return analysis


def _context_for_llm(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Trim the analysis to the decision-relevant signal for the LLM."""
    base = analysis["roi"]["scenarios"].get("Base", {})
    return {
        "drug": analysis["profile"]["brand_name"],
        "indication": analysis["profile"]["indication"],
        "differentiators": analysis["profile"]["differentiators"],
        "liabilities": analysis["profile"]["liabilities"],
        "competitor": analysis["competitors"]["kisunla_vs_leqembi"],
        "cms_access": analysis["payers"]["cms_coverage_framework"],
        "market_funnel": analysis["market_funnel"],
        "ge_mckinsey": analysis["ge_mckinsey"],
        "bcg": analysis["bcg"],
        "launch_readiness": analysis["launch_readiness"],
        "top_risks": analysis["risk_register"]["top_risks"],
        "roi_base_case": base,
    }


def deterministic_briefing(analysis: Dict[str, Any]) -> str:
    """A no-LLM fallback narrative built straight from the numbers."""
    lr = analysis["launch_readiness"]
    ge = analysis["ge_mckinsey"]
    bcg = analysis["bcg"]
    funnel = analysis["market_funnel"]
    base = analysis["roi"]["scenarios"].get("Base", {})
    top = analysis["risk_register"]["top_risks"]

    def usd(x):
        return f"${x/1e9:.2f}B" if abs(x) >= 1e9 else f"${x/1e6:.0f}M"

    lines = []
    lines.append(f"RECOMMENDATION: {lr['verdict']} "
                 f"(composite launch-readiness {lr['composite']}/100).")
    lines.append("")
    lines.append("Market & competitive position: The anti-amyloid class is a high-growth, "
                 f"high-unmet-need market. GE-McKinsey places Kisunla at {ge['cell']} "
                 f"({ge['strategy']}); BCG classifies it as a {bcg['quadrant']} "
                 f"({bcg['strategy']}). The strategic thesis is to compete on total cost of "
                 "therapy and finite-duration dosing rather than head-to-head efficacy.")
    lines.append("")
    lines.append("Access & payer: CMS Coverage-with-Evidence-Development (NCD 200.3) is the "
                 "gating constraint. The modelled funnel narrows from "
                 f"{funnel['tam']:,} early-symptomatic patients to a Base-case treated "
                 f"population of {base.get('steady_state_patients', 0):,}. Site enablement, "
                 "registry onboarding, and the diagnostic funnel drive launch velocity.")
    lines.append("")
    lines.append("Financial outlook (MODELLED, not a forecast): Base-case peak annual revenue "
                 f"{usd(base.get('peak_annual_revenue_usd', 0))}, 5-year cumulative EBIT "
                 f"{usd(base.get('cumulative_ebit_usd', 0))}, payback in year "
                 f"{base.get('payback_year', 'n/a')}.")
    lines.append("")
    lines.append("Top risks: " + "; ".join(
        f"{r['risk']} (severity {r['severity']}, {r['tier']})" for r in top))
    lines.append("")
    lines.append("Conditions to proceed: (1) accelerate CED registry/site enablement; "
                 "(2) fund the diagnostic funnel (PET + plasma p-tau217); (3) lock ARIA-safety "
                 "monitoring infrastructure; (4) execute finite-duration value-based contracts. "
                 "This recommendation is conditional on Regulatory, Medical, Legal, and "
                 "Market-Access validation.")
    return "\n".join(lines)


def build_briefing(overrides: Optional[Dict[str, Any]] = None,
                   model: Optional[str] = None) -> Dict[str, Any]:
    """Full package: analysis + narrative (LLM if available, else deterministic)."""
    analysis = build_analysis(overrides)
    used_llm = False
    error = None
    if llm.is_configured():
        try:
            narrative = llm.generate_briefing(_context_for_llm(analysis), model=model)
            used_llm = True
        except Exception as exc:  # network / auth / library issues -> graceful fallback
            narrative = deterministic_briefing(analysis)
            error = str(exc)
    else:
        narrative = deterministic_briefing(analysis)

    return {
        "analysis": analysis,
        "narrative": narrative,
        "used_llm": used_llm,
        "llm_error": error,
    }
