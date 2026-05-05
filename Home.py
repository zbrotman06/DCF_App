"""
Finance Suite — Landing Page
Home.py — place this at the ROOT of your repo (same level as pages/)

Directory structure:
  Home.py
  pages/
    1_DCF_Engine.py      ← your dcf_app.py renamed
    2_Consulting.py      ← your dcf_consulting.py renamed
  requirements.txt
"""

import streamlit as st

st.set_page_config(
    page_title="Finance Suite",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════
# CSS — Refined dark luxury, geometric grid, editorial type
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist+Mono:wght@300;400;500;600&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Reset ── */
*, html, body, [class*="css"] {
    box-sizing: border-box;
    margin: 0; padding: 0;
}

/* ── Page ── */
.stApp {
    background-color: #050810;
    background-image:
        linear-gradient(rgba(30,45,80,0.18) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30,45,80,0.18) 1px, transparent 1px);
    background-size: 52px 52px;
    background-position: -1px -1px;
    min-height: 100vh;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stSidebarNav"],
[data-testid="collapsedControl"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── Wrapper ── */
.suite-wrap {
    max-width: 960px;
    margin: 0 auto;
    padding: 72px 32px 80px;
    position: relative;
}

/* ── Ambient glow ── */
.suite-wrap::before {
    content: '';
    position: fixed;
    top: -180px;
    left: 50%;
    transform: translateX(-50%);
    width: 700px;
    height: 400px;
    background: radial-gradient(ellipse at center,
        rgba(31,111,235,0.10) 0%,
        rgba(63,185,80,0.04) 50%,
        transparent 75%);
    pointer-events: none;
    z-index: 0;
}

/* ── Top badge ── */
.top-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 999px;
    padding: 7px 18px;
    font-family: 'Geist Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #58a6ff;
    margin-bottom: 40px;
}
.top-badge .dot {
    width: 6px; height: 6px;
    background: #3fb950;
    border-radius: 50%;
    animation: pulse 2.2s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.5; transform: scale(0.85); }
}

/* ── Headline ── */
.suite-headline {
    font-family: 'Instrument Serif', Georgia, serif;
    font-size: clamp(44px, 7vw, 72px);
    font-weight: 400;
    line-height: 1.06;
    letter-spacing: -1.5px;
    color: #e6edf3;
    margin-bottom: 20px;
}
.suite-headline em {
    font-style: italic;
    color: #3fb950;
}

/* ── Subheadline ── */
.suite-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 17px;
    font-weight: 400;
    color: #484f58;
    line-height: 1.65;
    max-width: 520px;
    margin-bottom: 44px;
}

/* ── Feature pills ── */
.pill-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 64px;
}
.pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 999px;
    padding: 6px 14px;
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: #7d8590;
    transition: border-color 0.2s, color 0.2s;
}
.pill:hover { border-color: rgba(88,166,255,0.3); color: #8b949e; }
.pill .p-icon { font-size: 14px; }

/* ── Section label ── */
.section-label {
    font-family: 'Geist Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #30363d;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

/* ── Module grid ── */
.module-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 64px;
}

/* ── Module card ── */
.mod-card {
    background: rgba(13,17,23,0.85);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 28px 26px 24px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: border-color 0.25s ease, transform 0.2s ease, box-shadow 0.25s ease;
    text-decoration: none;
    display: block;
    backdrop-filter: blur(12px);
}
.mod-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(63,185,80,0.04) 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.25s;
}
.mod-card:hover { 
    border-color: rgba(63,185,80,0.3);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(63,185,80,0.06), 0 0 0 1px rgba(63,185,80,0.1);
}
.mod-card:hover::before { opacity: 1; }

/* Coming soon cards */
.mod-card.soon {
    cursor: default;
    opacity: 0.45;
}
.mod-card.soon:hover {
    border-color: rgba(255,255,255,0.06);
    transform: none;
    box-shadow: none;
}
.mod-card.soon::before { display: none; }

/* Card top row */
.card-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 18px;
}
.card-icon {
    width: 44px; height: 44px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}
.card-status {
    font-family: 'Geist Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 999px;
}
.status-live {
    background: rgba(63,185,80,0.12);
    border: 1px solid rgba(63,185,80,0.25);
    color: #3fb950;
}
.status-soon {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    color: #30363d;
}
.status-beta {
    background: rgba(210,153,34,0.12);
    border: 1px solid rgba(210,153,34,0.25);
    color: #d29922;
}

/* Card body */
.card-name {
    font-family: 'DM Sans', sans-serif;
    font-size: 17px;
    font-weight: 600;
    color: #e6edf3;
    margin-bottom: 7px;
    letter-spacing: -0.2px;
}
.card-desc {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 400;
    color: #484f58;
    line-height: 1.55;
    margin-bottom: 20px;
}

/* Card tags */
.card-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}
.tag {
    font-family: 'Geist Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    color: #30363d;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 4px;
    padding: 3px 7px;
}

/* Card CTA */
.card-cta {
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: #3fb950;
    margin-top: 18px;
    opacity: 0;
    transform: translateX(-4px);
    transition: opacity 0.2s, transform 0.2s;
}
.mod-card:hover .card-cta {
    opacity: 1;
    transform: translateX(0);
}

/* ── Stats row ── */
.stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 64px;
}
.stat-cell {
    background: rgba(13,17,23,0.9);
    padding: 20px 24px;
    text-align: center;
}
.stat-value {
    font-family: 'Geist Mono', monospace;
    font-size: 26px;
    font-weight: 600;
    color: #e6edf3;
    font-variant-numeric: tabular-nums;
    line-height: 1;
    margin-bottom: 5px;
}
.stat-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    color: #30363d;
    font-weight: 400;
}

/* ── Footer ── */
.suite-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-top: 1px solid rgba(255,255,255,0.05);
    padding-top: 28px;
}
.footer-brand {
    font-family: 'Geist Mono', monospace;
    font-size: 12px;
    color: #21262d;
    letter-spacing: 1px;
}
.footer-links {
    display: flex;
    gap: 20px;
}
.footer-link {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    color: #21262d;
    text-decoration: none;
    transition: color 0.2s;
}
.footer-link:hover { color: #484f58; }

/* ── Staggered fade-in ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.suite-wrap > * {
    animation: fadeUp 0.5s ease both;
}
.top-badge    { animation-delay: 0.05s; }
.suite-headline{ animation-delay: 0.12s; }
.suite-sub    { animation-delay: 0.18s; }
.pill-row     { animation-delay: 0.22s; }
.section-label{ animation-delay: 0.28s; }
.module-grid  { animation-delay: 0.32s; }
.stats-row    { animation-delay: 0.38s; }
.suite-footer { animation-delay: 0.44s; }

/* ── Streamlit button override (nav buttons) ── */
.stButton > button {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# PAGE CONTENT
# ══════════════════════════════════════════════════════════════

# Navigation handler
if "nav" not in st.session_state:
    st.session_state.nav = None

# Hidden nav buttons (triggered by JS click)
col_dcf, col_con = st.columns(2)
with col_dcf:
    if st.button("GO_DCF", key="go_dcf"):
        st.switch_page("pages/1_DCF_Engine.py")
with col_con:
    if st.button("GO_CON", key="go_con"):
        st.switch_page("pages/2_Consulting.py")

# ── Main HTML ─────────────────────────────────────────────────
st.markdown("""
<div class="suite-wrap">

  <!-- Badge -->
  <div class="top-badge">
    <span class="dot"></span>
    Professional Finance Suite
  </div>

  <!-- Headline -->
  <h1 class="suite-headline">
    Institutional-grade<br>
    analysis, <em>built for you.</em>
  </h1>

  <!-- Sub -->
  <p class="suite-sub">
    DCF valuation, M&amp;A accretion/dilution, sector dashboards,
    and strategic scenario analysis — all live, all transparent,
    all exportable.
  </p>

  <!-- Pills -->
  <div class="pill-row">
    <span class="pill"><span class="p-icon">📡</span> Live market data</span>
    <span class="pill"><span class="p-icon">🔢</span> Full UFCF transparency</span>
    <span class="pill"><span class="p-icon">📊</span> One-click Excel export</span>
    <span class="pill"><span class="p-icon">🎯</span> Sensitivity analysis</span>
    <span class="pill"><span class="p-icon">⚡</span> Instant recalculation</span>
  </div>

  <!-- Module section label -->
  <div class="section-label">Modules — Select to Launch</div>

  <!-- Module grid -->
  <div class="module-grid">

  <!-- DCF Engine -->
  <a class="mod-card" href="/DCF_Engine" target="_self">
    <div class="card-top">
      <div class="card-icon">◈</div>
      <span class="card-status status-live">Live</span>
    </div>
    <div class="card-name">DCF Engine</div>
    <div class="card-desc">
      Full discounted cash flow model with dual terminal value methods,
      WACC decomposition, and 7×7 sensitivity tables.
    </div>
    <div class="card-tags">
      <span class="tag">UFCF</span>
      <span class="tag">GGM</span>
      <span class="tag">Exit Mult</span>
      <span class="tag">Scenarios</span>
      <span class="tag">Excel Export</span>
    </div>
    <div class="card-cta">Launch Engine →</div>
  </a>

  <!-- Consulting Suite -->
  <a class="mod-card" href="/Consulting" target="_self">
    <div class="card-top">
      <div class="card-icon">⬡</div>
      <span class="card-status status-live">Live</span>
    </div>
    <div class="card-name">Consulting Suite</div>
    <div class="card-desc">
      M&amp;A accretion/dilution screen, strategic scenario value analysis,
      and sector dashboard with auto-generated equity research thesis.
    </div>
    <div class="card-tags">
      <span class="tag">M&amp;A</span>
      <span class="tag">Synergies</span>
      <span class="tag">Sector Comps</span>
      <span class="tag">AI Thesis</span>
    </div>
    <div class="card-cta">Launch Suite →</div>
  </a>

  <!-- LBO Model — Coming Soon -->
  <div class="mod-card soon">
    <div class="card-top">
      <div class="card-icon">🔒</div>
      <span class="card-status status-soon">Soon</span>
    </div>
    <div class="card-name">LBO Model</div>
    <div class="card-desc">
      Leveraged buyout analysis with debt waterfall, IRR bridge,
      and returns attribution across multiple exit scenarios.
    </div>
    <div class="card-tags">
      <span class="tag">IRR</span>
      <span class="tag">MOIC</span>
      <span class="tag">Debt Sched.</span>
      <span class="tag">PE</span>
    </div>
  </div>

  <!-- Credit / Fixed Income -->
  <div class="mod-card soon">
    <div class="card-top">
      <div class="card-icon">🔒</div>
      <span class="card-status status-soon">Soon</span>
    </div>
    <div class="card-name">Credit Analysis</div>
    <div class="card-desc">
      Bond valuation, yield-to-maturity calculator, credit spread
      analysis, and covenant coverage ratios for fixed income.
    </div>
    <div class="card-tags">
      <span class="tag">YTM</span>
      <span class="tag">Duration</span>
      <span class="tag">Spreads</span>
      <span class="tag">Covenants</span>
    </div>
  </div>

  <!-- Portfolio Analytics -->
  <div class="mod-card soon">
    <div class="card-top">
      <div class="card-icon">🔒</div>
      <span class="card-status status-soon">Soon</span>
    </div>
    <div class="card-name">Portfolio Analytics</div>
    <div class="card-desc">
      Multi-asset portfolio construction with factor exposure,
      risk attribution, and efficient frontier visualization.
    </div>
    <div class="card-tags">
      <span class="tag">Sharpe</span>
      <span class="tag">Beta</span>
      <span class="tag">Drawdown</span>
      <span class="tag">AM</span>
    </div>
  </div>

  <!-- Real Estate -->
  <div class="mod-card soon">
    <div class="card-top">
      <div class="card-icon">🔒</div>
      <span class="card-status status-soon">Soon</span>
    </div>
    <div class="card-name">Real Estate Model</div>
    <div class="card-desc">
      Property-level cash flow model with cap rate analysis,
      debt service coverage, and equity multiple returns.
    </div>
    <div class="card-tags">
      <span class="tag">Cap Rate</span>
      <span class="tag">DSCR</span>
      <span class="tag">NOI</span>
      <span class="tag">RE PE</span>
    </div>
  </div>

  </div>

  <!-- Stats row -->
  <div class="stats-row">
    <div class="stat-cell">
      <div class="stat-value">2</div>
      <div class="stat-label">Modules Live</div>
    </div>
    <div class="stat-cell">
      <div class="stat-value">7×7</div>
      <div class="stat-label">Sensitivity Tables</div>
    </div>
    <div class="stat-cell">
      <div class="stat-value">8</div>
      <div class="stat-label">Excel Sheets Exported</div>
    </div>
    <div class="stat-cell">
      <div class="stat-value">3</div>
      <div class="stat-label">Valuation Methods</div>
    </div>
  </div>

  <!-- Footer -->
  <div class="suite-footer">
    <div class="footer-brand">⬡ FINANCE SUITE · FOR EDUCATIONAL USE</div>
    <div class="footer-links">
      <a class="footer-link" href="https://github.com/zbrotman06/DCF_App" target="_blank">GitHub</a>
      <a class="footer-link" href="/DCF_Engine" target="_self">DCF Engine</a>
      <a class="footer-link" href="/Consulting" target="_self">Consulting</a>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)
