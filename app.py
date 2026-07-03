"""Kisunla (donanemab) Launch Strategist - Streamlit executive dashboard.

Run:  streamlit run app.py
Optional LLM narrative: set OPENROUTER_API_KEY (see .env.example).
"""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from strategist import config, data_loader, frameworks
from strategist.synthesis import build_briefing

st.set_page_config(page_title="Kisunla Launch Strategist", layout="wide",
                   initial_sidebar_state="expanded")

# --- Palette (dark-neon, matches RxPlained style) ------------------------------
INK = "#0b1020"
CARD = "#141b2e"
NEON = "#00e5ff"
LIME = "#7CFC00"
AMBER = "#ffb020"
RED = "#ff4d6d"
MUTE = "#8aa0c0"

st.markdown(f"""
<style>
    .stApp {{ background: {INK}; }}
    .block-container {{ padding-top: 1.4rem; }}
    h1, h2, h3, h4 {{ color: #eaf2ff; }}
    .metric-card {{ background:{CARD}; border:1px solid #223; border-radius:14px;
        padding:14px 16px; }}
    .banner {{ background:#20140a; border:1px solid {AMBER}; color:#ffd9a0;
        border-radius:12px; padding:10px 14px; font-size:0.82rem; }}
    .verdict-go {{ color:{LIME}; }} .verdict-cond {{ color:{AMBER}; }}
    .verdict-no {{ color:{RED}; }}
    .pill {{ display:inline-block; padding:2px 10px; border-radius:999px;
        background:#0e2233; color:{NEON}; font-size:0.72rem; border:1px solid #1c3a4d; }}
    .cite {{ font-size:0.75rem; color:{MUTE}; }}
    a {{ color:{NEON}; }}
</style>
""", unsafe_allow_html=True)


# --- Header --------------------------------------------------------------------
st.markdown(f"# {config.APP_TITLE}")
st.caption(config.APP_SUBTITLE)
st.markdown(f"<div class='banner'>{config.COMPLIANCE_BANNER}</div>", unsafe_allow_html=True)

profile = data_loader.load_profile()
competitors = data_loader.load_competitors()
payers = data_loader.load_payers()


# --- Sidebar: editable assumptions ---------------------------------------------
st.sidebar.header("Modelling assumptions")
st.sidebar.caption("Every figure below is an editable input, not a fact.")

with st.sidebar.expander("Market funnel (US)", expanded=True):
    ms = competitors["market_sizing_assumptions_us"]
    pop = st.number_input("Early symptomatic AD population",
                          value=int(ms["early_symptomatic_ad_population"]), step=100000)
    dx = st.slider("Clinically diagnosed rate", 0.0, 1.0, float(ms["clinically_diagnosed_rate"]), 0.01)
    amy = st.slider("Amyloid-confirmed & eligible rate", 0.0, 1.0,
                    float(ms["amyloid_confirmed_and_eligible_rate"]), 0.01)
    site = st.slider("Monitoring-site access rate", 0.0, 1.0,
                     float(ms["access_to_monitoring_site_rate"]), 0.01)
    pay = st.slider("Payer-covered rate", 0.0, 1.0, float(ms["payer_covered_rate"]), 0.01)

with st.sidebar.expander("Competitive position"):
    rel_share = st.slider("Relative market share (vs leader)", 0.1, 2.0, 0.6, 0.05)
    growth = st.slider("Market growth (%)", 0.0, 60.0, 25.0, 1.0)

with st.sidebar.expander("Launch-readiness pillars (0-100)"):
    readiness_scores = {}
    for pillar, val in config.DEFAULT_LAUNCH_READINESS_SCORES.items():
        readiness_scores[pillar] = st.slider(pillar.replace("_", " "), 0, 100, int(val), 1)

with st.sidebar.expander("ROI scenarios"):
    scenarios = {}
    for name, s in config.ROI_SCENARIOS.items():
        st.markdown(f"**{name}**")
        pen = st.slider(f"{name} penetration", 0.0, 0.6, float(s["penetration"]), 0.01, key=f"pen{name}")
        price = st.number_input(f"{name} net price/yr ($)", value=int(s["net_price"]), step=1000, key=f"pr{name}")
        scenarios[name] = {"penetration": pen, "net_price": price, "duration_years": s["duration_years"]}

overrides = {
    "market_assumptions": {
        "early_symptomatic_ad_population": pop,
        "clinically_diagnosed_rate": dx,
        "amyloid_confirmed_and_eligible_rate": amy,
        "access_to_monitoring_site_rate": site,
        "payer_covered_rate": pay,
    },
    "readiness_scores": readiness_scores,
    "bcg": {"relative_market_share": rel_share, "market_growth_pct": growth},
    "roi_scenarios": scenarios,
}

st.sidebar.divider()
llm_on = "configured" if config.get_openrouter_key() else "not set (deterministic narrative)"
st.sidebar.caption(f"OpenRouter: **{llm_on}**  \nModel: `{config.DEFAULT_MODEL}`")
run = st.sidebar.button("Run launch synthesis", type="primary", use_container_width=True)


# --- Build analysis ------------------------------------------------------------
result = build_briefing(overrides)
A = result["analysis"]
lr = A["launch_readiness"]
ge = A["ge_mckinsey"]
bcg = A["bcg"]
funnel = A["market_funnel"]
roi = A["roi"]["scenarios"]


def usd(x):
    return f"${x/1e9:.2f}B" if abs(x) >= 1e9 else f"${x/1e6:.0f}M"


# --- Executive summary ---------------------------------------------------------
st.subheader("Executive summary")
vclass = {"GO": "verdict-go", "CONDITIONAL GO": "verdict-cond"}.get(lr["verdict"], "verdict-no")
c1, c2, c3, c4, c5 = st.columns(5)
c1.markdown(f"<div class='metric-card'>Go/No-Go<br><span class='{vclass}' style='font-size:1.5rem;font-weight:700'>{lr['verdict']}</span></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='metric-card'>Readiness<br><span style='font-size:1.5rem;color:{NEON}'>{lr['composite']}/100</span></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='metric-card'>SOM (treated)<br><span style='font-size:1.4rem;color:{LIME}'>{funnel['som']:,}</span></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='metric-card'>Base peak rev<br><span style='font-size:1.4rem;color:{LIME}'>{usd(roi['Base']['peak_annual_revenue_usd'])}</span></div>", unsafe_allow_html=True)
c5.markdown(f"<div class='metric-card'>GE / BCG<br><span style='font-size:0.95rem;color:{AMBER}'>{ge['strength_band']} str · {bcg['quadrant']}</span></div>", unsafe_allow_html=True)


# --- Tabs ----------------------------------------------------------------------
tabs = st.tabs([
    "Clinical & safety", "Competitor", "Market funnel", "Portfolio (GE/BCG)",
    "Financials", "Risk", "Roadmap & KPIs", "Go/No-Go briefing",
])

# 1. Clinical & safety ----------------------------------------------------------
with tabs[0]:
    pt = profile["pivotal_trial"]
    st.markdown(f"### {profile['brand_name']} ({profile['inn']})")
    st.write(profile["modality"])
    st.markdown(f"**Indication:** {profile['indication']}  \n"
                f"**Regulatory:** {profile['fda_status']} ({profile['fda_approval_date']})  \n"
                f"**Dosing:** {profile['route']}")
    st.markdown(f"#### Pivotal: {pt['name']} ({pt['nct_id']})")
    eff = pt["efficacy"]
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("iADRS slowing (low/med tau)", f"{eff['iadrs_low_med_tau']['relative_slowing_pct']}%")
    e2.metric("CDR-SB slowing (low/med tau)", f"{eff['cdrsb_low_med_tau']['relative_slowing_pct']}%")
    e3.metric("ARIA-E", f"{pt['safety']['aria_e_pct']}%")
    e4.metric("N (randomised)", f"{pt['n_total']:,}")
    st.markdown("**Differentiators**")
    for d in profile["differentiators"]:
        st.markdown(f"- {d}")
    st.markdown("**Liabilities**")
    for d in profile["liabilities"]:
        st.markdown(f"- {d}")
    st.markdown(f"<div class='banner'>Boxed warning: {pt['safety']['boxed_warning']}. "
                f"{pt['safety']['monitoring']}.</div>", unsafe_allow_html=True)
    st.markdown(f"<p class='cite'>According to PubMed - {pt['citation']} "
                f"(<a href='https://doi.org/10.1001/jama.2023.13239' target='_blank'>"
                f"DOI 10.1001/jama.2023.13239</a>). Grounded via ClinicalTrials.gov "
                f"{pt['nct_id']} and CMS NCD 200.3.</p>", unsafe_allow_html=True)

# 2. Competitor -----------------------------------------------------------------
with tabs[1]:
    st.markdown("### Competitive benchmarking")
    st.caption(competitors["_meta"]["note"])
    vs = competitors["kisunla_vs_leqembi"]
    rows = [k for k in vs if not k.startswith("_") and k not in ("differentiation_thesis",)]
    table = {"Dimension": [], "Kisunla": [], "Leqembi": []}
    for k in rows:
        table["Dimension"].append(k.replace("_", " ").title())
        table["Kisunla"].append(vs[k].get("kisunla", ""))
        table["Leqembi"].append(vs[k].get("leqembi", ""))
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.markdown(f"<div class='banner'>{vs['_disclaimer']}</div>", unsafe_allow_html=True)
    st.markdown(f"**Differentiation thesis:** {vs['differentiation_thesis']}")
    comp = competitors["competitors"][0]
    st.markdown(f"#### Primary competitor: {comp['brand_name']} ({comp['inn']})")
    st.write(f"{comp['manufacturer']} · {comp['route']} · approved {comp['fda_approval_date']}")
    st.write(comp["strategic_notes"])

# 3. Market funnel --------------------------------------------------------------
with tabs[2]:
    st.markdown("### TAM -> SAM -> SOM access funnel")
    labels = [s["label"] for s in funnel["stages"]]
    vals = [s["patients"] for s in funnel["stages"]]
    fig = go.Figure(go.Funnel(y=labels, x=vals, textinfo="value+percent initial",
                              marker={"color": [NEON, "#33c9e0", LIME, AMBER, RED]}))
    fig.update_layout(paper_bgcolor=INK, plot_bgcolor=INK, font_color="#eaf2ff", height=420,
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Illustrative funnel from editable assumptions. CMS CED and the diagnostic "
               "funnel are the dominant constraints on realised demand.")

# 4. Portfolio ------------------------------------------------------------------
with tabs[3]:
    colA, colB = st.columns(2)
    with colA:
        st.markdown("### GE-McKinsey 9-box")
        fig = go.Figure()
        for i in range(3):
            for j in range(3):
                score = i + j
                shade = f"rgba(0,229,255,{0.05 + score*0.05})"
                fig.add_shape(type="rect", x0=i*(5/3), x1=(i+1)*(5/3), y0=j*(5/3), y1=(j+1)*(5/3),
                              fillcolor=shade, line=dict(color="#223"))
        fig.add_trace(go.Scatter(x=[ge["strength"]], y=[ge["attractiveness"]], mode="markers+text",
                                 marker=dict(size=26, color=LIME, line=dict(color="white", width=2)),
                                 text=["Kisunla"], textposition="top center"))
        fig.update_layout(xaxis=dict(title="Competitive strength", range=[0, 5]),
                          yaxis=dict(title="Market attractiveness", range=[0, 5]),
                          paper_bgcolor=INK, plot_bgcolor=INK, font_color="#eaf2ff", height=380,
                          margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"**{ge['cell']}** — {ge['strategy']}")
    with colB:
        st.markdown("### BCG growth-share")
        fig = go.Figure()
        fig.add_shape(type="line", x0=1, x1=1, y0=0, y1=60, line=dict(color=MUTE, dash="dash"))
        fig.add_shape(type="line", x0=0, x1=2, y0=10, y1=10, line=dict(color=MUTE, dash="dash"))
        for (qx, qy, lbl) in [(1.6, 45, "Star"), (0.4, 45, "Question Mark"),
                              (1.6, 5, "Cash Cow"), (0.4, 5, "Dog")]:
            fig.add_annotation(x=qx, y=qy, text=lbl, showarrow=False, font=dict(color=MUTE, size=11))
        fig.add_trace(go.Scatter(x=[bcg["relative_market_share"]], y=[bcg["market_growth_pct"]],
                                 mode="markers+text", marker=dict(size=26, color=AMBER,
                                 line=dict(color="white", width=2)),
                                 text=["Kisunla"], textposition="top center"))
        fig.update_layout(xaxis=dict(title="Relative market share", range=[0, 2]),
                          yaxis=dict(title="Market growth (%)", range=[0, 60]),
                          paper_bgcolor=INK, plot_bgcolor=INK, font_color="#eaf2ff", height=380,
                          margin=dict(l=10, r=10, t=10, b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.info(f"**{bcg['quadrant']}** — {bcg['strategy']}")

# 5. Financials -----------------------------------------------------------------
with tabs[4]:
    st.markdown("### ROI scenarios (modelled - not a forecast)")
    names = list(roi.keys())
    years = [y["year"] for y in roi[names[0]]["yearly"]]
    fig = go.Figure()
    palette = {"Bear": RED, "Base": NEON, "Bull": LIME}
    for n in names:
        fig.add_trace(go.Bar(name=n, x=years, y=[y["revenue_usd"]/1e9 for y in roi[n]["yearly"]],
                             marker_color=palette.get(n, MUTE)))
    fig.update_layout(barmode="group", paper_bgcolor=INK, plot_bgcolor=INK, font_color="#eaf2ff",
                      height=360, yaxis_title="Revenue ($B)", xaxis_title="Launch year",
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    summ = {"Scenario": [], "Steady patients": [], "Peak revenue": [],
            "5y cum. EBIT": [], "Net of launch inv.": [], "Payback yr": []}
    for n in names:
        r = roi[n]
        summ["Scenario"].append(n)
        summ["Steady patients"].append(f"{r['steady_state_patients']:,}")
        summ["Peak revenue"].append(usd(r["peak_annual_revenue_usd"]))
        summ["5y cum. EBIT"].append(usd(r["cumulative_ebit_usd"]))
        summ["Net of launch inv."].append(usd(r["net_of_launch_investment_usd"]))
        summ["Payback yr"].append(r["payback_year"] or "n/a")
    st.dataframe(summ, use_container_width=True, hide_index=True)
    st.caption(f"Cost assumptions: COGS {int(config.ROI_COST_ASSUMPTIONS['cogs_pct']*100)}% · "
               f"SG&A {int(config.ROI_COST_ASSUMPTIONS['sga_pct']*100)}% · launch investment "
               f"{usd(config.ROI_COST_ASSUMPTIONS['launch_investment_usd'])} (all editable).")

# 6. Risk -----------------------------------------------------------------------
with tabs[5]:
    st.markdown("### Enterprise risk register")
    rr = A["risk_register"]
    fig = go.Figure()
    tier_color = {"Critical": RED, "High": AMBER, "Moderate": NEON, "Low": LIME}
    for r in rr["risks"]:
        fig.add_trace(go.Scatter(x=[r["likelihood"]], y=[r["impact"]], mode="markers",
                                 marker=dict(size=18 + r["severity"], color=tier_color[r["tier"]],
                                             opacity=0.85, line=dict(color="white", width=1)),
                                 name=r["risk"], hovertext=f"{r['risk']} ({r['tier']}, sev {r['severity']})"))
    fig.update_layout(xaxis=dict(title="Likelihood", range=[0, 6], dtick=1),
                      yaxis=dict(title="Impact", range=[0, 6], dtick=1),
                      paper_bgcolor=INK, plot_bgcolor=INK, font_color="#eaf2ff", height=420,
                      showlegend=False, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    tbl = {"Risk": [], "Category": [], "L": [], "I": [], "Severity": [], "Tier": [], "Mitigation": []}
    for r in rr["risks"]:
        tbl["Risk"].append(r["risk"]); tbl["Category"].append(r["category"])
        tbl["L"].append(r["likelihood"]); tbl["I"].append(r["impact"])
        tbl["Severity"].append(r["severity"]); tbl["Tier"].append(r["tier"])
        tbl["Mitigation"].append(r["mitigation"])
    st.dataframe(tbl, use_container_width=True, hide_index=True)

# 7. Roadmap & KPIs -------------------------------------------------------------
with tabs[6]:
    st.markdown("### 30-60-90 day plan")
    cols = st.columns(3)
    for col, phase in zip(cols, A["roadmap_30_60_90"]):
        with col:
            st.markdown(f"**{phase['horizon']}** — {phase['focus']}")
            for fn, txt in phase["workstreams"].items():
                st.markdown(f"<span class='pill'>{fn}</span> {txt}", unsafe_allow_html=True)
    st.markdown("### 3-year roadmap")
    for yr in A["roadmap_3_year"]:
        st.markdown(f"**{yr['year']} — {yr['theme']}:** " + " · ".join(yr["objectives"]))
    st.markdown("### KPI framework")
    kcols = st.columns(len(A["kpi_framework"]))
    for col, (area, kpis) in zip(kcols, A["kpi_framework"].items()):
        with col:
            st.markdown(f"**{area}**")
            for k in kpis:
                tag = "🟢" if k["type"] == "Leading" else "🔵"
                st.markdown(f"{tag} {k['kpi']}")

# 8. Briefing -------------------------------------------------------------------
with tabs[7]:
    st.markdown("### Board-ready Go/No-Go briefing")
    src = "LLM (OpenRouter)" if result["used_llm"] else "Deterministic template (no LLM key)"
    st.caption(f"Narrative source: {src}")
    if result.get("llm_error"):
        st.warning(f"LLM call failed, using fallback: {result['llm_error']}")
    st.markdown(f"<div class='banner'>{config.COMPLIANCE_BANNER}</div>", unsafe_allow_html=True)
    st.markdown(result["narrative"])
    st.download_button("Download briefing (.md)", result["narrative"],
                       file_name="kisunla_launch_briefing.md", mime="text/markdown")

st.divider()
st.caption("Kisunla Launch Strategist · internal decision-support · not promotional, not medical advice. "
           "Built on the Antigravity-native + OpenRouter pattern.")
