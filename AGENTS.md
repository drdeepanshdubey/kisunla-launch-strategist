# AGENTS.md — Kisunla Launch Strategist

Operating contract for any agent (Google Antigravity, Claude Code, or similar)
working in this repository.

## Mission
Produce a **board-ready launch decision package** for **Kisunla (donanemab-azbt,
Eli Lilly)** in early symptomatic Alzheimer's disease, by fusing three lenses:
clinical/regulatory readiness → commercial/market intelligence → consultant-grade
portfolio strategy (BCG + GE-McKinsey + MECE), ending in a Go/No-Go with a risk
register, ROI scenarios, a 30-60-90 plan, a 3-year roadmap, and a KPI dashboard.

## Non-negotiable guardrails
1. **Internal decision-support only.** Nothing produced here is promotional or
   medical advice. Preserve the compliance banner (`strategist/config.py:COMPLIANCE_BANNER`)
   wherever a narrative is surfaced.
2. **No head-to-head superiority claims** from cross-trial data. Competitor
   comparisons are non-validated context.
3. **Facts vs assumptions.** Clinical/regulatory facts are connector-grounded
   (see `data/kisunla_profile.json` `_meta.sources`). Every market, share, price,
   and ROI number is an explicit, editable modelling assumption — never assert it
   as fact.
4. **PubMed attribution.** When citing the pivotal evidence, attribute
   "According to PubMed" and link the DOI `10.1001/jama.2023.13239`.
5. **Human-in-the-loop.** The recommendation is always conditional on Regulatory,
   Medical, Legal, and Market-Access sign-off.

## Architecture (where things live)
- `data/*.json` — grounded profile, competitor/market, payer/CMS-CED intelligence.
- `strategist/frameworks.py` — pure, offline framework calculators (unit-tested).
- `strategist/synthesis.py` — orchestrator → structured analysis + narrative.
- `strategist/llm.py` — OpenRouter client (bring-your-own key; optional).
- `app.py` — Streamlit + Plotly executive dashboard.

## How to run
```bash
pip install -r requirements.txt
cp .env.example .env          # add OPENROUTER_API_KEY for LLM narrative (optional)
streamlit run app.py
python -m pytest -q           # offline framework tests
```

## Definition of done
- `pytest` green (frameworks deterministic and offline).
- Dashboard renders all pillars: clinical/safety, competitor, funnel, GE/BCG,
  financials, risk, roadmap/KPIs, Go/No-Go.
- Works with **no** API key (deterministic narrative) and **with** a key (LLM narrative).
- Guardrails and grounding intact.

## Extending
- New drug? Replace `data/*.json` (keep the `_meta` grounding + disclaimers) and
  re-tune weights in `config.py`. The framework engine is drug-agnostic.
- New framework? Add a pure function in `frameworks.py`, wire it in `synthesis.py`,
  add a test, then surface it in `app.py`.
