"""Offline, deterministic tests for the framework engine. No network, no LLM."""
import math

from strategist import config, frameworks, build_analysis


# --- helpers -------------------------------------------------------------------
def test_weighted_score_normalises():
    s = {"a": 4.0, "b": 2.0}
    w = {"a": 3.0, "b": 1.0}  # not pre-normalised
    assert math.isclose(frameworks.weighted_score(s, w), (4*3 + 2*1) / 4)


# --- funnel --------------------------------------------------------------------
def test_funnel_is_monotonically_narrowing():
    a = {
        "early_symptomatic_ad_population": 6_000_000,
        "clinically_diagnosed_rate": 0.3,
        "amyloid_confirmed_and_eligible_rate": 0.5,
        "access_to_monitoring_site_rate": 0.5,
        "payer_covered_rate": 0.7,
        "anti_amyloid_treatment_penetration_at_maturity": 0.2,
    }
    f = frameworks.tam_sam_som(a)
    patients = [s["patients"] for s in f["stages"]]
    assert patients == sorted(patients, reverse=True)
    assert f["tam"] == 6_000_000
    assert f["som"] < f["accessible"] < f["sam"] < f["tam"]


def test_funnel_penetration_override():
    a = {
        "early_symptomatic_ad_population": 1_000_000,
        "clinically_diagnosed_rate": 1.0,
        "amyloid_confirmed_and_eligible_rate": 1.0,
        "access_to_monitoring_site_rate": 1.0,
        "payer_covered_rate": 1.0,
        "anti_amyloid_treatment_penetration_at_maturity": 0.2,
    }
    assert frameworks.tam_sam_som(a, penetration=0.5)["som"] == 500_000


# --- GE-McKinsey ---------------------------------------------------------------
def test_ge_bands_and_bounds():
    ge = frameworks.ge_mckinsey(config.DEFAULT_MARKET_ATTRACTIVENESS_SCORES,
                                config.DEFAULT_COMPETITIVE_STRENGTH_SCORES)
    assert 0 <= ge["attractiveness"] <= 5
    assert 0 <= ge["strength"] <= 5
    assert ge["attractiveness_band"] in {"Low", "Medium", "High"}
    assert ge["strategy"]


def test_ge_high_high_is_invest_grow():
    top = {k: 5 for k in config.DEFAULT_MARKET_ATTRACTIVENESS_SCORES}
    tops = {k: 5 for k in config.DEFAULT_COMPETITIVE_STRENGTH_SCORES}
    assert frameworks.ge_mckinsey(top, tops)["strategy"].startswith("Invest / Grow")


# --- BCG -----------------------------------------------------------------------
def test_bcg_quadrants():
    assert frameworks.bcg_matrix(0.5, 25)["quadrant"] == "Question Mark"
    assert frameworks.bcg_matrix(1.5, 25)["quadrant"] == "Star"
    assert frameworks.bcg_matrix(1.5, 5)["quadrant"] == "Cash Cow"
    assert frameworks.bcg_matrix(0.5, 5)["quadrant"] == "Dog"


# --- readiness / Go-No-Go ------------------------------------------------------
def test_readiness_verdict_thresholds():
    hi = {k: 90 for k in config.LAUNCH_READINESS_WEIGHTS}
    lo = {k: 30 for k in config.LAUNCH_READINESS_WEIGHTS}
    mid = {k: 65 for k in config.LAUNCH_READINESS_WEIGHTS}
    assert frameworks.launch_readiness(hi)["verdict"] == "GO"
    assert frameworks.launch_readiness(lo)["verdict"] == "NO-GO / REMEDIATE"
    assert frameworks.launch_readiness(mid)["verdict"] == "CONDITIONAL GO"


def test_readiness_weakest_pillars_len():
    r = frameworks.launch_readiness(config.DEFAULT_LAUNCH_READINESS_SCORES)
    assert len(r["weakest_pillars"]) == 3


# --- risk ----------------------------------------------------------------------
def test_risk_severity_and_sort():
    rr = frameworks.risk_register(config.DEFAULT_RISKS)
    sev = [r["severity"] for r in rr["risks"]]
    assert sev == sorted(sev, reverse=True)
    assert all(r["severity"] == r["likelihood"] * r["impact"] for r in rr["risks"])
    assert rr["critical_count"] >= 1  # CED bottleneck is 4x5=20


# --- ROI -----------------------------------------------------------------------
def test_roi_scales_with_patients():
    small = frameworks.roi_scenarios(100_000)["scenarios"]["Base"]
    big = frameworks.roi_scenarios(200_000)["scenarios"]["Base"]
    assert big["peak_annual_revenue_usd"] == 2 * small["peak_annual_revenue_usd"]
    assert small["yearly"][-1]["year"] == config.ROI_COST_ASSUMPTIONS["years_modelled"]


# --- end-to-end ----------------------------------------------------------------
def test_build_analysis_shape():
    a = build_analysis()
    for key in ["market_funnel", "ge_mckinsey", "bcg", "launch_readiness",
                "risk_register", "roi", "roadmap_30_60_90", "roadmap_3_year",
                "kpi_framework", "profile"]:
        assert key in a
    assert a["profile"]["brand_name"] == "Kisunla"
    assert len(a["roadmap_30_60_90"]) == 3
