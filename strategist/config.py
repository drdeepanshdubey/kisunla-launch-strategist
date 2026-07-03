"""Central configuration for the Kisunla Launch Strategist.

All strategic weights, thresholds, and default modelling assumptions live here so
they are transparent and editable in one place. Nothing in this module asserts a
commercial fact; every number is an explicit, reviewable input.
"""
from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"


def _load_dotenv() -> None:
    """Minimal .env loader (no dependency). Values already in the environment win."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val
    except OSError:
        pass


_load_dotenv()

PROFILE_FILE = DATA_DIR / "kisunla_profile.json"
COMPETITOR_FILE = DATA_DIR / "competitor_landscape.json"
PAYER_FILE = DATA_DIR / "payer_landscape.json"

# ---------------------------------------------------------------------------
# Compliance / governance
# ---------------------------------------------------------------------------
APP_TITLE = "Kisunla (donanemab) Launch Strategist"
APP_SUBTITLE = "Internal strategic decision-support - board-ready launch analysis"

COMPLIANCE_BANNER = (
    "INTERNAL DECISION-SUPPORT ONLY. This tool synthesises public clinical/regulatory "
    "data with editable commercial assumptions to support launch planning. It is NOT "
    "promotional material, NOT medical advice, and NOT a substitute for Regulatory, "
    "Medical, Legal, and Market-Access review. Cross-trial comparisons are not "
    "statistically valid and must not be used in promotion. All market, financial, and "
    "share figures are illustrative modelling inputs requiring human validation."
)

LLM_SYSTEM_GUARDRAIL = (
    "You are a pharmaceutical launch-strategy analyst producing an INTERNAL, board-level "
    "decision-support briefing. Rules you must follow:\n"
    "1. This is not promotional content and not medical advice. Never write copy that could "
    "be used to promote the drug to patients or prescribers.\n"
    "2. Never make head-to-head superiority claims from cross-trial data; label any competitor "
    "comparison as non-validated context.\n"
    "3. Treat all market-size, share, pricing, and ROI numbers as explicit assumptions provided "
    "to you, not as established facts. Reference them as 'modelled' or 'assumed'.\n"
    "4. Be decision-useful, structured, and concise. Surface risks honestly, especially safety "
    "(ARIA) and access (CMS CED) constraints.\n"
    "5. Always frame the recommendation as conditional on human validation and cross-functional sign-off."
)

# ---------------------------------------------------------------------------
# GE-McKinsey factor weights (must sum to 1.0 within each dimension)
# ---------------------------------------------------------------------------
MARKET_ATTRACTIVENESS_WEIGHTS = {
    "market_size": 0.20,
    "growth_rate": 0.25,
    "unmet_need": 0.25,
    "reimbursement_environment": 0.20,
    "competitive_intensity_inverse": 0.10,
}

COMPETITIVE_STRENGTH_WEIGHTS = {
    "efficacy": 0.22,
    "safety_tolerability": 0.20,
    "dosing_convenience": 0.18,
    "evidence_base": 0.15,
    "value_cost": 0.15,
    "kol_medical_support": 0.10,
}

# Default 0-5 factor scores for Kisunla (editable in the app). 5 = most favourable.
DEFAULT_MARKET_ATTRACTIVENESS_SCORES = {
    "market_size": 4.5,
    "growth_rate": 4.0,
    "unmet_need": 5.0,
    "reimbursement_environment": 2.0,   # CMS CED is a real drag
    "competitive_intensity_inverse": 2.5,  # entrenched first mover
}

DEFAULT_COMPETITIVE_STRENGTH_SCORES = {
    "efficacy": 4.0,
    "safety_tolerability": 2.5,   # ARIA burden
    "dosing_convenience": 3.5,    # Q4W + finite duration, but IV
    "evidence_base": 4.5,         # tau-stratified pivotal trial
    "value_cost": 3.5,            # limited-duration cost story
    "kol_medical_support": 4.0,
}

# ---------------------------------------------------------------------------
# Launch-readiness pillars (weights sum to 1.0). Default 0-100 scores editable.
# ---------------------------------------------------------------------------
LAUNCH_READINESS_WEIGHTS = {
    "regulatory": 0.12,
    "clinical_evidence": 0.15,
    "manufacturing_supply": 0.12,
    "market_access_payer": 0.20,
    "medical_affairs_kol": 0.12,
    "commercial_salesforce": 0.10,
    "diagnostic_ecosystem": 0.10,
    "safety_monitoring_infra": 0.09,
}

DEFAULT_LAUNCH_READINESS_SCORES = {
    "regulatory": 95,          # traditional approval secured
    "clinical_evidence": 90,
    "manufacturing_supply": 70,
    "market_access_payer": 55,  # CED gate
    "medical_affairs_kol": 75,
    "commercial_salesforce": 65,
    "diagnostic_ecosystem": 50,  # funnel drop-off
    "safety_monitoring_infra": 60,
}

# ---------------------------------------------------------------------------
# Risk register (likelihood & impact on 1-5; severity = L x I, max 25)
# ---------------------------------------------------------------------------
DEFAULT_RISKS = [
    {"risk": "ARIA safety events / litigation exposure", "category": "Safety", "likelihood": 3, "impact": 5,
     "mitigation": "Mandatory MRI protocol, APOE4 genotyping, site certification, proactive REMS-style education"},
    {"risk": "CMS CED registry bottleneck slows uptake", "category": "Access", "likelihood": 4, "impact": 5,
     "mitigation": "Dedicated registry-onboarding field team; streamline data entry; site incentives"},
    {"risk": "Diagnostic funnel drop-off (amyloid confirmation)", "category": "Access", "likelihood": 4, "impact": 4,
     "mitigation": "Expand plasma p-tau217 and PET access; primary-care referral pathways"},
    {"risk": "Entrenched first-mover competitor (Leqembi)", "category": "Commercial", "likelihood": 4, "impact": 3,
     "mitigation": "Total-cost-of-therapy and finite-duration value narrative; VBC contracting"},
    {"risk": "Subcutaneous / at-home competitor convenience", "category": "Commercial", "likelihood": 3, "impact": 3,
     "mitigation": "Emphasise limited-duration dosing; monitor own SC/next-gen pipeline"},
    {"risk": "Pricing / IRA / payer pushback", "category": "Financial", "likelihood": 3, "impact": 4,
     "mitigation": "Outcomes-based and finite-duration contracts; robust value dossier"},
    {"risk": "Manufacturing / infusion capacity scale-up", "category": "Operations", "likelihood": 2, "impact": 4,
     "mitigation": "Capacity planning; infusion-center partnerships; demand shaping by geography"},
    {"risk": "Guideline / KOL adoption lag", "category": "Medical", "likelihood": 2, "impact": 3,
     "mitigation": "KOL advisory boards, RWE generation, medical education"},
]

# ---------------------------------------------------------------------------
# ROI scenario defaults (illustrative, editable)
# ---------------------------------------------------------------------------
ROI_SCENARIOS = {
    "Bear": {"penetration": 0.10, "net_price": 20000, "duration_years": 1.3},
    "Base": {"penetration": 0.20, "net_price": 22000, "duration_years": 1.5},
    "Bull": {"penetration": 0.32, "net_price": 24000, "duration_years": 1.7},
}
ROI_COST_ASSUMPTIONS = {
    "cogs_pct": 0.15,          # % of net revenue
    "sga_pct": 0.35,           # % of net revenue (launch-heavy)
    "launch_investment_usd": 800_000_000,  # illustrative cumulative launch spend
    "years_modelled": 5,
    "ramp": [0.15, 0.40, 0.70, 0.90, 1.00],  # fraction of steady-state patients captured per year
}

# ---------------------------------------------------------------------------
# Go / No-Go thresholds on the composite launch-readiness score
# ---------------------------------------------------------------------------
GO_THRESHOLD = 75
CONDITIONAL_GO_THRESHOLD = 60


def get_openrouter_key() -> str | None:
    """Return the OpenRouter API key from the environment, if present."""
    return os.environ.get("OPENROUTER_API_KEY")


DEFAULT_MODEL = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
