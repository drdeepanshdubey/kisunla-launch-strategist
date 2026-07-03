---
name: drug-launch-strategist
description: >
  Build a board-ready pharmaceutical launch strategy for a chosen drug by fusing
  clinical/regulatory readiness, commercial market intelligence, and consultant-grade
  portfolio strategy (BCG + GE-McKinsey + MECE) into a Go/No-Go decision package with
  risk register, ROI scenarios, a 30-60-90 plan, a 3-year roadmap, and a KPI dashboard.
  Use when the user asks to create a launch strategy, launch plan, go-to-market, or
  commercial-readiness assessment for a specific therapy. NEGATIVE: not for clinical
  data analysis alone, not for promotional copy, not for medical advice.
---

# Drug Launch Strategist

A composite skill that turns a single drug into a C-suite launch decision package.
It is the fusion of three sub-disciplines:

1. **Healthcare/clinical data analyst** — efficacy, safety, regulatory status,
   trial design (grounded in ClinicalTrials.gov, PubMed, FDA, CMS).
2. **Pharma market-research intelligence** — market sizing (TAM/SAM/SOM),
   competitor benchmarking, payer/access landscape, patient/diagnostic funnel.
3. **Consultant strategy builder** — BCG growth-share, GE-McKinsey attractiveness
   × strength, MECE risk structuring, ROI scenarios, cross-functional roadmap.

## Method (the pipeline this repo implements)
1. **Ground the profile.** Pull real clinical/regulatory facts; keep sources in
   `_meta`. Separate facts from commercial assumptions explicitly.
2. **Size the market.** Multiplicative access funnel — TAM → diagnosed → amyloid-
   confirmed/eligible (SAM) → site+payer accessible → treated (SOM). Every gate is
   an editable assumption.
3. **Benchmark competition.** Head-to-head framing vs the entrenched competitor,
   labelled non-validated (no cross-trial superiority claims).
4. **Read the payer landscape.** Model the coverage bottleneck (for anti-amyloids,
   CMS Coverage-with-Evidence-Development) as the primary revenue gate.
5. **Position the portfolio.** GE-McKinsey (weighted attractiveness × strength) and
   BCG (relative share × market growth) → strategy call.
6. **Score launch readiness.** Weighted pillars → composite → Go / Conditional Go /
   No-Go against thresholds.
7. **Structure risk.** Likelihood × impact → severity tiers → mitigations (MECE).
8. **Model ROI.** Bear/Base/Bull scenarios → peak revenue, cumulative EBIT, payback.
9. **Plan execution.** 30-60-90 by function (R&D/Medical, Access, Commercial,
   Supply Chain) + 3-year roadmap + leading/lagging KPI framework.
10. **Decide.** Board-ready Go/No-Go narrative behind a mandatory compliance banner,
    conditional on human sign-off.

## Guardrails
- Internal decision-support only — never promotional, never medical advice.
- Facts are grounded and cited (PubMed → attribute + DOI); commercial numbers are
  transparent, editable assumptions.
- No head-to-head superiority claims from cross-trial data.
- Always require Regulatory/Medical/Legal/Market-Access validation.

## Reference implementation
- Framework engine: `strategist/frameworks.py` (pure, testable).
- Orchestration: `strategist/synthesis.py`.
- Dashboard: `app.py` (Streamlit + Plotly).
- Drug-agnostic: swap `data/*.json` to retarget another therapy.
