# Architecture

## Overview
A layered, drug-agnostic launch-strategy engine with a Streamlit front end.

```
          ┌──────────────────────────────────────────────┐
          │                 app.py (UI)                  │
          │  Streamlit + Plotly · editable assumptions   │
          └───────────────┬──────────────────────────────┘
                          │ overrides (dict)
          ┌───────────────▼──────────────────────────────┐
          │        strategist/synthesis.py               │
          │  build_analysis() → structured package        │
          │  build_briefing() → + narrative (LLM/fallback) │
          └───────┬───────────────────────┬──────────────┘
                  │                        │
   ┌──────────────▼─────────┐   ┌──────────▼───────────────┐
   │ strategist/frameworks  │   │   strategist/llm.py       │
   │ pure calculators       │   │   OpenRouter (optional)   │
   │ (unit-tested, offline) │   └───────────────────────────┘
   └──────────────┬─────────┘
                  │ reads
   ┌──────────────▼─────────────────────────────────────────┐
   │ data/*.json  (grounded profile · competitor · payer)   │
   └────────────────────────────────────────────────────────┘
```

## Design principles
- **Deterministic core, optional intelligence.** All numbers come from pure
  functions in `frameworks.py`; the LLM only narrates. The app is fully usable
  offline with no API key.
- **Facts vs assumptions, enforced by structure.** Grounded clinical/regulatory
  data lives in JSON `_meta.sources`; every commercial number is an editable
  assumption in `config.py` or the sidebar.
- **Drug-agnostic engine.** Swap `data/*.json` and re-tune `config.py` weights to
  retarget any therapy; the framework layer is unchanged.
- **Compliance by construction.** A single `COMPLIANCE_BANNER` and
  `LLM_SYSTEM_GUARDRAIL` gate every narrative surface.

## Data flow
1. Sidebar edits → `overrides` dict.
2. `build_analysis(overrides)` loads data, runs TAM/SAM/SOM, GE-McKinsey, BCG,
   launch-readiness, risk register, ROI scenarios, roadmaps, KPIs.
3. `build_briefing()` wraps that with a narrative — LLM if `OPENROUTER_API_KEY`
   is set, otherwise `deterministic_briefing()`.
4. `app.py` renders eight tabs + an executive summary.

## Grounding provenance
- `data/kisunla_profile.json`: ClinicalTrials.gov NCT04437511 (TRAILBLAZER-ALZ 2),
  Sims et al. JAMA 2023 (DOI 10.1001/jama.2023.13239, via PubMed), CMS NCD 200.3,
  FDA traditional approval 2024-07-02.
- Competitor clinical facts are compiled from public disclosures and flagged
  verify-before-use (not connector-grounded to the same standard).

## Testing
`tests/test_frameworks.py` covers funnel monotonicity, GE/BCG placement, readiness
verdict thresholds, risk severity/sorting, ROI linearity, and end-to-end shape —
all offline.
