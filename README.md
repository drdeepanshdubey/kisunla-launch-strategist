# Kisunla Launch Strategist

An **internal, board-ready launch-strategy decision-support agent** for **Kisunla
(donanemab-azbt, Eli Lilly)** in early symptomatic Alzheimer's disease.

It fuses three lenses into one Go/No-Go package:
**clinical/regulatory readiness → commercial/market intelligence → consultant-grade
portfolio strategy (BCG + GE-McKinsey + MECE)** — with a risk register, ROI
scenarios, a 30-60-90 plan, a 3-year roadmap, and a KPI dashboard.

> ⚠️ **Internal decision-support only. Not promotional material, not medical advice.**
> Clinical/regulatory facts are grounded and cited; every market/financial number is
> an editable modelling assumption. Cross-trial comparisons are non-validated.
> The recommendation is conditional on Regulatory, Medical, Legal, and Market-Access sign-off.

## Quickstart
```bash
pip install -r requirements.txt
cp .env.example .env        # optional: add OPENROUTER_API_KEY for the LLM narrative
streamlit run app.py
```
Runs fully **without** an API key (deterministic narrative). Add an OpenRouter key
to generate the LLM-written briefing.

## What's inside
| Layer | File(s) |
|-------|---------|
| Grounded data | `data/kisunla_profile.json`, `data/competitor_landscape.json`, `data/payer_landscape.json` |
| Framework engine (pure, tested) | `strategist/frameworks.py` |
| Orchestration + fallback narrative | `strategist/synthesis.py` |
| OpenRouter client (optional) | `strategist/llm.py` |
| Config / weights / guardrails | `strategist/config.py` |
| Dashboard | `app.py` |
| Tests | `tests/test_frameworks.py` |
| Agent config | `AGENTS.md`, `CLAUDE.md`, `.claude/skills/drug-launch-strategist/SKILL.md` |

## Dashboard tabs
Executive summary → Clinical & safety → Competitor → Market funnel →
Portfolio (GE-McKinsey / BCG) → Financials (ROI) → Risk → Roadmap & KPIs →
Go/No-Go briefing.

## Grounding
- **TRAILBLAZER-ALZ 2** (ClinicalTrials.gov `NCT04437511`).
- Pivotal evidence — *According to PubMed:* Sims JR et al. JAMA 2023;330(6):512-527,
  [DOI 10.1001/jama.2023.13239](https://doi.org/10.1001/jama.2023.13239).
- **CMS NCD 200.3** (anti-amyloid Coverage with Evidence Development).
- **FDA** traditional approval 2024-07-02.

## Deploy
- **Docker:** `docker build -t kisunla-strategist . && docker run -p 8501:8501 kisunla-strategist`
- **Google Antigravity:** open the repo; `AGENTS.md` is the agent operating contract.
  Add `OPENROUTER_API_KEY` to the environment for LLM narration.

## Retarget another drug
Replace `data/*.json` (keep the `_meta` grounding blocks and disclaimers) and
re-tune the weights in `strategist/config.py`. The framework engine is drug-agnostic.

## Tests
```bash
python -m pytest -q
```
