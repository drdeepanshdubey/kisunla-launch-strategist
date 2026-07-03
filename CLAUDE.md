# CLAUDE.md

Guidance for Claude Code when working in this repo. (See `AGENTS.md` for the full
operating contract — this file is the quick reference.)

## What this is
An internal **launch-strategy decision-support** app for **Kisunla (donanemab)**.
It computes strategy frameworks deterministically and optionally narrates a
board-ready Go/No-Go via OpenRouter.

## Golden rules
- Not promotional, not medical advice. Keep the compliance banner on every narrative.
- Clinical/regulatory = grounded fact; commercial/financial = editable assumption. Never blur the two.
- No cross-trial superiority claims.
- Cite PubMed with DOI `10.1001/jama.2023.13239` for the pivotal trial.

## Map
| Path | Role |
|------|------|
| `data/kisunla_profile.json` | Connector-grounded drug profile |
| `data/competitor_landscape.json` | Competitor + market-sizing assumptions |
| `data/payer_landscape.json` | CMS-CED / payer access intelligence |
| `strategist/config.py` | Weights, thresholds, default assumptions, banner |
| `strategist/frameworks.py` | Pure calculators (TAM/SAM/SOM, GE, BCG, readiness, risk, ROI, roadmap, KPIs) |
| `strategist/synthesis.py` | Orchestrator + deterministic fallback narrative |
| `strategist/llm.py` | OpenRouter client (optional) |
| `app.py` | Streamlit + Plotly dashboard |
| `tests/test_frameworks.py` | Offline unit tests |

## Common tasks
- **Change an assumption default** → `strategist/config.py`.
- **Add/adjust a framework** → edit `frameworks.py` (keep it pure), wire in
  `synthesis.build_analysis`, add a test, surface in `app.py`.
- **Swap the drug** → replace `data/*.json` (retain `_meta` grounding + disclaimers).

## Test before you ship
```bash
python -m pytest -q
python -c "from strategist import build_briefing; print(build_briefing()['analysis']['launch_readiness'])"
```
