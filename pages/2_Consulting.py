"""
DCF Consulting Suite
══════════════════════════════════════════════
Option A — M&A / Acquisition Screen
Option B — Strategic Scenario Value Analysis
Option C — Sector Valuation Dashboard

Run:  streamlit run dcf_consulting.py
Deps: pip install streamlit yfinance pandas numpy plotly openpyxl requests curl_cffi
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io, time, random, warnings, textwrap
warnings.filterwarnings("ignore")

# ── Optional Claude API for thesis generation ──────────────────
try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

# ══════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

*, html, body, [class*="css"] { font-family:'Inter',sans-serif; box-sizing:border-box; }
.stApp { background:#080c10; color:#cdd9e5; }

[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#0d1117 0%,#080c10 100%) !important;
    border-right:1px solid #1e2733;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] p { color:#8b949e !important; font-size:12px !important; }
[data-testid="stSidebar"] .stTextInput input {
    background:#161b22 !important; border:1px solid #30363d !important;
    color:#e6edf3 !important; border-radius:6px !important;
    font-family:'JetBrains Mono',monospace !important; font-size:13px !important;
}

.block-container { padding:1.5rem 2rem !important; max-width:100% !important; }

[data-testid="stTabs"] [role="tablist"] {
    border-bottom:1px solid #1e2733; gap:0; background:transparent;
}
[data-testid="stTabs"] [role="tab"] {
    font-family:'JetBrains Mono',monospace !important; font-size:11px !important;
    font-weight:500 !important; text-transform:uppercase; letter-spacing:1.2px;
    color:#484f58 !important; padding:10px 20px !important;
    border:none !important; background:transparent !important;
    border-bottom:2px solid transparent !important; transition:all 0.2s;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color:#58a6ff !important; border-bottom:2px solid #58a6ff !important;
}

/* Cards */
.card {
    background:#0d1117; border:1px solid #1e2733; border-radius:10px;
    padding:20px 22px; position:relative; overflow:hidden; margin-bottom:12px;
}
.card-accent { position:absolute; top:0; left:0; width:100%; height:2px; }
.card-title {
    font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:600;
    text-transform:uppercase; letter-spacing:1.8px; color:#484f58; margin-bottom:8px;
}
.card-value {
    font-family:'JetBrains Mono',monospace; font-size:24px; font-weight:700;
    color:#e6edf3; line-height:1;
}
.card-sub { font-family:'JetBrains Mono',monospace; font-size:10px; color:#484f58; margin-top:6px; }

/* Deal metric row */
.deal-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:8px; margin:14px 0; }
.sector-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:14px 0; }

/* Badges */
.badge { display:inline-flex; align-items:center; gap:4px; border-radius:5px;
    padding:3px 10px; font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:600; }
.badge-up { background:rgba(63,185,80,.12); border:1px solid rgba(63,185,80,.3); color:#3fb950; }
.badge-dn { background:rgba(248,81,73,.12); border:1px solid rgba(248,81,73,.3); color:#f85149; }
.badge-neu { background:rgba(88,166,255,.12); border:1px solid rgba(88,166,255,.3); color:#58a6ff; }
.badge-gold { background:rgba(210,153,34,.12); border:1px solid rgba(210,153,34,.3); color:#d29922; }

/* Info/warn boxes */
.info-box { background:rgba(88,166,255,.07); border:1px solid rgba(88,166,255,.2);
    border-radius:8px; padding:12px 16px; font-size:12px; color:#8b949e;
    margin:8px 0; font-family:'JetBrains Mono',monospace; line-height:1.7; }
.warn-box { background:rgba(210,153,34,.07); border:1px solid rgba(210,153,34,.25);
    border-radius:8px; padding:12px 16px; font-size:12px; color:#d29922;
    margin:8px 0; font-family:'JetBrains Mono',monospace; line-height:1.7; }
.accretive-box { background:rgba(63,185,80,.07); border:1px solid rgba(63,185,80,.25);
    border-radius:8px; padding:14px 18px; font-size:13px; color:#3fb950;
    margin:10px 0; font-family:'JetBrains Mono',monospace; line-height:1.8; }
.dilutive-box { background:rgba(248,81,73,.07); border:1px solid rgba(248,81,73,.25);
    border-radius:8px; padding:14px 18px; font-size:13px; color:#f85149;
    margin:10px 0; font-family:'JetBrains Mono',monospace; line-height:1.8; }

/* Tables */
.fin-table { width:100%; border-collapse:collapse; font-family:'JetBrains Mono',monospace; font-size:11px; }
.fin-table th { background:#0d1117; color:#484f58; font-size:9px; text-transform:uppercase;
    letter-spacing:1.2px; padding:9px 12px; text-align:right;
    border-bottom:1px solid #1e2733; font-weight:600; }
.fin-table th:first-child { text-align:left; }
.fin-table td { padding:7px 12px; text-align:right; border-bottom:1px solid #0d1117; color:#8b949e; }
.fin-table td:first-child { text-align:left; }
.fin-table .tot td { color:#e6edf3 !important; font-weight:600;
    border-top:1px solid #1e2733; background:#0d1117; }
.fin-table tr:hover td { background:#0d1117; }

/* Thesis block */
.thesis-block {
    background:#0d1117; border:1px solid #1e2733; border-left:3px solid #58a6ff;
    border-radius:0 8px 8px 0; padding:20px 24px; font-size:13px;
    color:#8b949e; line-height:1.9; margin:16px 0;
}
.thesis-block p { margin:0 0 12px 0; }
.thesis-block strong { color:#e6edf3; }

/* Waterfall label */
.sec-label { font-family:'JetBrains Mono',monospace; font-size:10px; font-weight:600;
    text-transform:uppercase; letter-spacing:2px; color:#30363d;
    padding:18px 0 8px 0; border-bottom:1px solid #0d1117; margin-bottom:12px; }

/* Sidebar buttons */
.stButton button {
    background:linear-gradient(135deg,#1158c7,#1f6feb) !important;
    border:1px solid #388bfd !important; color:#fff !important;
    border-radius:8px !important; font-family:'JetBrains Mono',monospace !important;
    font-size:12px !important; font-weight:600 !important;
    padding:10px !important; width:100% !important;
}
.stDownloadButton button {
    background:linear-gradient(135deg,#1a7f37,#238636) !important;
    border:1px solid #2ea043 !important; color:#fff !important;
    border-radius:8px !important; font-family:'JetBrains Mono',monospace !important;
    font-size:12px !important; font-weight:600 !important;
    padding:10px !important; width:100% !important;
}

.sb-section { font-family:'JetBrains Mono',monospace; font-size:9px; font-weight:600;
    text-transform:uppercase; letter-spacing:2px; color:#30363d;
    border-top:1px solid #1e2733; padding:14px 0 6px 0; margin-top:6px; }
.divider { border:none; border-top:1px solid #1e2733; margin:18px 0; }
.footer { font-family:'JetBrains Mono',monospace; font-size:10px; color:#21262d;
    text-align:center; padding:20px 0; letter-spacing:1px; }
#MainMenu, footer, header { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# CHART THEME
# ══════════════════════════════════════════════════════════════
CHART = dict(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="JetBrains Mono", color="#484f58", size=10),
    margin=dict(l=10, r=10, t=40, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10),
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    xaxis=dict(gridcolor="#0d1117", linecolor="#1e2733", tickfont=dict(size=10)),
    yaxis=dict(gridcolor="#1e2733", linecolor="#1e2733", tickfont=dict(size=10)),
)

# ══════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════
def fmt(v, style="$M", d=1):
    if v is None or (isinstance(v, float) and np.isnan(v)): return "N/A"
    if style == "$M":  return f"${v/1e6:,.{d}f}M"
    if style == "$B":  return f"${v/1e9:,.{d}f}B"
    if style == "%":   return f"{v*100:.{d}f}%"
    if style == "x":   return f"{v:.{d}f}x"
    if style == "$":   return f"${v:,.{d}f}"
    return str(v)

def safe_get(df, *keys):
    if df is None or df.empty: return pd.Series(dtype=float)
    for k in keys:
        if k in df.index:
            return pd.to_numeric(df.loc[k], errors="coerce")
    return pd.Series(dtype=float)

def badge(text, kind="neu"):
    return f"<span class='badge badge-{kind}'>{text}</span>"

# ══════════════════════════════════════════════════════════════
# DATA LAYER
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def fetch(ticker):
    time.sleep(random.uniform(0.8, 1.8))
    t = yf.Ticker(ticker)
    try:    info = t.info or {}
    except: info = {}
    try:
        inc  = t.financials
        bal  = t.balance_sheet
        cf   = t.cashflow
        hist = t.history(period="3y")
    except:
        return None, f"Could not fetch data for {ticker}"
    if inc is None or inc.empty:
        return None, f"No financial data for '{ticker}'"
    return {"info":info,"income":inc,"balance":bal,"cashflow":cf,"history":hist}, None

def extract_financials(data):
    """Pull key financials into a flat dict for easy use."""
    info = data["info"]
    inc  = data["income"]
    bal  = data["balance"]
    cf   = data["cashflow"]

    revenue   = safe_get(inc,"Total Revenue","Revenue")
    ebit      = safe_get(inc,"EBIT","Operating Income","Ebit")
    net_inc   = safe_get(inc,"Net Income","Net Income Common Stockholders")
    da        = safe_get(cf, "Depreciation","Depreciation And Amortization",
                             "Depreciation Amortization Depletion")
    capex     = safe_get(cf, "Capital Expenditures","Capital Expenditure","Purchase Of Ppe")
    sbc       = safe_get(cf, "Stock Based Compensation","Share Based Compensation")
    tax_prov  = safe_get(inc,"Tax Provision","Income Tax Expense")
    pretax    = safe_get(inc,"Pretax Income","Income Before Tax")
    interest  = safe_get(inc,"Interest Expense","Interest Expense Non Operating")
    chg_nwc   = safe_get(cf, "Change In Working Capital","Changes In Working Capital")
    total_debt= safe_get(bal,"Total Debt","Long Term Debt And Capital Lease Obligation","Long Term Debt")
    cash_bs   = safe_get(bal,"Cash And Cash Equivalents",
                             "Cash Cash Equivalents And Short Term Investments",
                             "Cash And Short Term Investments")
    shares_bs = safe_get(bal,"Ordinary Shares Number","Common Stock Shares Outstanding")

    # Most recent year values
    def r(s):
        try: return float(s.iloc[0])
        except: return np.nan

    eff_tax = np.clip(r(tax_prov)/r(pretax) if r(pretax) != 0 else 0.21, 0.10, 0.40)
    net_debt_val = r(total_debt) - r(cash_bs)

    return {
        "ticker":    info.get("symbol", ""),
        "name":      info.get("longName", info.get("shortName", "")),
        "sector":    info.get("sector",""),
        "industry":  info.get("industry",""),
        "price":     info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose") or np.nan,
        "mkt_cap":   info.get("marketCap", np.nan),
        "ev":        info.get("enterpriseValue", np.nan),
        "shares":    info.get("sharesOutstanding", np.nan),
        "beta":      info.get("beta", 1.0) or 1.0,
        "pe":        info.get("trailingPE", np.nan),
        "fwd_pe":    info.get("forwardPE", np.nan),
        "ev_ebitda": info.get("enterpriseToEbitda", np.nan),
        "ev_rev":    info.get("enterpriseToRevenue", np.nan),
        "rev_growth":info.get("revenueGrowth", np.nan),
        "ebitda_mg": info.get("ebitdaMargins", np.nan),
        "target":    info.get("targetMeanPrice", np.nan),
        "analyst_lo":info.get("targetLowPrice", np.nan),
        "analyst_hi":info.get("targetHighPrice", np.nan),
        "n_analysts":info.get("numberOfAnalystOpinions", np.nan),
        "52w_lo":    info.get("fiftyTwoWeekLow", np.nan),
        "52w_hi":    info.get("fiftyTwoWeekHigh", np.nan),
        # financials
        "revenue":   r(revenue),
        "ebit":      r(ebit),
        "ebitda":    r(ebit) + abs(r(da)),
        "net_income":r(net_inc),
        "da":        abs(r(da)),
        "capex":     abs(r(capex)),
        "sbc":       abs(r(sbc)) if not np.isnan(r(sbc)) else 0,
        "interest":  abs(r(interest)) if not np.isnan(r(interest)) else 0,
        "eff_tax":   eff_tax,
        "net_debt":  net_debt_val,
        "total_debt":r(total_debt),
        "cash":      r(cash_bs),
        "chg_nwc":   r(chg_nwc),
        "nopat":     r(ebit) * (1 - eff_tax),
        "ufcf":      r(ebit)*(1-eff_tax) + abs(r(da)) + r(chg_nwc) - abs(r(capex)),
        "history":   data["history"],
    }

def quick_dcf(fin, rev_growth, ebit_margin, da_pct, capex_pct, nwc_pct,
              wacc, tgr, exit_mult, n=5, mid_year=False):
    """Run a quick 5-year DCF from a financials dict."""
    base_rev = fin["revenue"]
    if np.isnan(base_rev) or base_rev <= 0: return None

    rows, rev, prev = [], base_rev, base_rev
    for i in range(n):
        rev    = prev * (1 + rev_growth)
        ebit   = rev * ebit_margin
        nopat  = ebit * (1 - fin["eff_tax"])
        da     = rev * da_pct
        capex  = rev * capex_pct
        d_nwc  = (rev - prev) * nwc_pct
        ufcf   = nopat + da - d_nwc - capex
        rows.append(ufcf)
        prev = rev

    offset = 0.5 if mid_year else 0
    disc   = [(1/(1+wacc))**(i+1-offset) for i in range(n)]
    pv_f   = [f*d for f,d in zip(rows,disc)]
    spv    = sum(pv_f)

    tv_g   = rows[-1]*(1+tgr)/(wacc-tgr) if wacc > tgr else np.nan
    pv_g   = tv_g/(1+wacc)**(n-offset) if not np.isnan(tv_g) else np.nan

    tv_e   = rev * ebit_margin * exit_mult
    pv_e   = tv_e/(1+wacc)**(n-offset)

    net_debt = fin["net_debt"] if not np.isnan(fin["net_debt"]) else 0
    shares   = fin["shares"]   if not np.isnan(fin["shares"])   else 1e9

    def price(pv_tv):
        ev  = spv + pv_tv
        eq  = ev - net_debt
        return eq / shares

    return {
        "pv_fcf":  spv,
        "tv_ggm":  tv_g if not np.isnan(tv_g) else 0,
        "pv_tv_g": pv_g if not np.isnan(pv_g) else 0,
        "ev_ggm":  spv + (pv_g if not np.isnan(pv_g) else 0),
        "price_ggm": price(pv_g) if not np.isnan(pv_g) else np.nan,
        "ev_em":   spv + pv_e,
        "price_em":price(pv_e),
        "pv_fcfs": pv_f,
        "ufcfs":   rows,
    }

def estimate_wacc(fin, rf=0.043, erp=0.055, tax=0.21):
    beta = fin.get("beta", 1.0) or 1.0
    ke   = rf + beta * erp
    kd   = np.clip(fin["interest"]/fin["total_debt"] if fin["total_debt"] > 0 else 0.05, 0.02, 0.15)
    mv   = fin["mkt_cap"] or 0
    D    = fin["total_debt"] or 0
    V    = mv + D
    we   = mv/V if V > 0 else 0.85
    wd   = 1 - we
    return we*ke + wd*kd*(1-tax), ke, kd, we, wd

# ══════════════════════════════════════════════════════════════
# ── OPTION A: M&A SCREEN ──────────────────────────────────────
# ══════════════════════════════════════════════════════════════
def run_ma_screen(acq_fin, tgt_fin, premium_pct, pct_cash, cost_synergy_pct,
                  rev_synergy_pct, financing_rate, tgt_dcf, acq_wacc):
    """
    Full M&A accretion/dilution model.
    Returns a dict with all deal metrics.
    """
    # ── Deal pricing ──────────────────────────────────────────
    tgt_price   = tgt_fin["price"]
    offer_price = tgt_price * (1 + premium_pct)
    tgt_shares  = tgt_fin["shares"] or 1e9
    deal_ev     = offer_price * tgt_shares + tgt_fin["net_debt"]

    # ── Funding ───────────────────────────────────────────────
    equity_val   = offer_price * tgt_shares
    cash_portion = equity_val * pct_cash
    stock_portion= equity_val * (1 - pct_cash)

    # New shares issued by acquirer
    acq_price    = acq_fin["price"]
    new_shares   = stock_portion / acq_price if acq_price > 0 else 0

    # Debt raised for cash portion
    new_debt     = cash_portion

    # ── Synergies ─────────────────────────────────────────────
    annual_cost_syn = tgt_fin["revenue"] * cost_synergy_pct
    annual_rev_syn  = (acq_fin["revenue"] + tgt_fin["revenue"]) * rev_synergy_pct
    # Tax-effect cost savings (they flow through as EBIT improvement)
    syn_after_tax   = annual_cost_syn * (1 - tgt_fin["eff_tax"])
    rev_syn_at      = annual_rev_syn  * tgt_fin["ebit"]/tgt_fin["revenue"] * (1 - tgt_fin["eff_tax"]) if tgt_fin["revenue"] > 0 else 0
    total_syn_at    = syn_after_tax + rev_syn_at

    # Integration costs (assume 1-year of cost synergies as one-time cost)
    integration_cost= annual_cost_syn * 1.0

    # ── Pro-forma combined P&L ────────────────────────────────
    combined_rev    = acq_fin["revenue"] + tgt_fin["revenue"] + annual_rev_syn
    combined_ebit   = acq_fin["ebit"]    + tgt_fin["ebit"]    + annual_cost_syn + annual_rev_syn
    combined_ebitda = acq_fin["ebitda"]  + tgt_fin["ebitda"]  + annual_cost_syn + annual_rev_syn

    # Interest on new debt
    incremental_int = new_debt * financing_rate
    combined_ebt    = combined_ebit - incremental_int
    combined_tax    = combined_ebt * acq_fin["eff_tax"]
    combined_net    = combined_ebt - combined_tax

    # Amortization of intangibles (assume 10% of deal premium goes to intangibles, amortized 10yr)
    purchase_price_premium = max(deal_ev - tgt_dcf["ev_ggm"], 0) if tgt_dcf else 0
    intangible_amort = purchase_price_premium * 0.10 / 10.0
    combined_net_adj = combined_net - intangible_amort

    # ── Accretion / Dilution ──────────────────────────────────
    acq_shares_before = acq_fin["shares"] or 1e9
    acq_shares_after  = acq_shares_before + new_shares
    acq_net_inc       = acq_fin["net_income"]
    acq_eps_before    = acq_net_inc / acq_shares_before if acq_shares_before > 0 else np.nan

    # Combined EPS
    pro_forma_eps     = combined_net_adj / acq_shares_after if acq_shares_after > 0 else np.nan
    eps_delta_pct     = (pro_forma_eps / acq_eps_before - 1) if (acq_eps_before and acq_eps_before != 0) else np.nan
    is_accretive      = eps_delta_pct > 0 if not np.isnan(eps_delta_pct) else False

    # ── FCF accretion ─────────────────────────────────────────
    acq_fcf_per_share     = acq_fin["ufcf"] / acq_shares_before if acq_shares_before > 0 else np.nan
    combined_ufcf         = acq_fin["ufcf"] + tgt_fin["ufcf"] + total_syn_at - incremental_int*(1-acq_fin["eff_tax"])
    pro_forma_fcf_per_sh  = combined_ufcf / acq_shares_after if acq_shares_after > 0 else np.nan
    fcf_delta_pct         = (pro_forma_fcf_per_sh/acq_fcf_per_share - 1) if (acq_fcf_per_share and acq_fcf_per_share != 0) else np.nan

    # ── Break-even premium ────────────────────────────────────
    # Find premium at which deal is exactly EPS-neutral
    # Pro-forma EPS = acq EPS before => solve for premium
    # Simplified: find where eps_delta = 0
    breakeven_premiums = []
    for p_test in np.linspace(0, 1.5, 300):
        op_test   = tgt_price * (1 + p_test)
        ev_test   = op_test * tgt_shares
        cash_t    = ev_test * pct_cash
        stock_t   = ev_test * (1-pct_cash)
        new_sh_t  = stock_t / acq_price if acq_price > 0 else 0
        new_int_t = cash_t * financing_rate
        comb_net_t= combined_ebt - (new_int_t - incremental_int) - combined_tax
        comb_net_t-= intangible_amort
        tot_sh_t  = acq_shares_before + new_sh_t
        eps_t     = comb_net_t / tot_sh_t if tot_sh_t > 0 else 0
        breakeven_premiums.append((p_test, eps_t))
    be_premium = None
    for i in range(1, len(breakeven_premiums)):
        e0 = breakeven_premiums[i-1][1]; e1 = breakeven_premiums[i][1]
        if (e0 - acq_eps_before) * (e1 - acq_eps_before) <= 0:
            be_premium = breakeven_premiums[i][0]
            break

    # ── Goodwill ──────────────────────────────────────────────
    book_value_tgt = tgt_fin["mkt_cap"] * 0.4 if not np.isnan(tgt_fin["mkt_cap"]) else 0
    goodwill       = max(equity_val - book_value_tgt, 0)

    # ── IRR estimate (simple) ─────────────────────────────────
    # If acquirer holds target for 5 years and exits at same EBITDA multiple
    exit_val    = tgt_fin["ebitda"] * (1.05**5) * (tgt_fin["ev_ebitda"] or 10)
    total_return= exit_val + total_syn_at * 5 - deal_ev
    irr_est     = (exit_val / deal_ev)**(1/5) - 1 if deal_ev > 0 else np.nan

    return {
        "offer_price":    offer_price,
        "premium_pct":    premium_pct,
        "deal_ev":        deal_ev,
        "equity_val":     equity_val,
        "cash_portion":   cash_portion,
        "stock_portion":  stock_portion,
        "new_shares":     new_shares,
        "new_debt":       new_debt,
        "cost_synergies": annual_cost_syn,
        "rev_synergies":  annual_rev_syn,
        "total_syn_at":   total_syn_at,
        "integration_cost": integration_cost,
        "combined_rev":   combined_rev,
        "combined_ebitda":combined_ebitda,
        "combined_ebit":  combined_ebit,
        "combined_net":   combined_net_adj,
        "acq_eps_before": acq_eps_before,
        "pro_forma_eps":  pro_forma_eps,
        "eps_delta_pct":  eps_delta_pct,
        "is_accretive":   is_accretive,
        "acq_fcf_ps":     acq_fcf_per_share,
        "pf_fcf_ps":      pro_forma_fcf_per_sh,
        "fcf_delta_pct":  fcf_delta_pct,
        "breakeven_premium": be_premium,
        "goodwill":       goodwill,
        "irr_est":        irr_est,
        "incremental_int":incremental_int,
        "intangible_amort": intangible_amort,
        "purchase_premium": purchase_price_premium,
    }

def ma_premium_sweep(acq_fin, tgt_fin, pct_cash, cost_syn_pct,
                     rev_syn_pct, financing_rate, tgt_dcf, acq_wacc):
    """Sweep premiums 0–80% and return accretion/dilution at each."""
    premiums = np.linspace(0, 0.80, 17)
    results  = []
    for p in premiums:
        r = run_ma_screen(acq_fin, tgt_fin, p, pct_cash, cost_syn_pct,
                          rev_syn_pct, financing_rate, tgt_dcf, acq_wacc)
        results.append({
            "Premium":       f"{p:.0%}",
            "Offer Price":   r["offer_price"],
            "Deal EV ($B)":  r["deal_ev"]/1e9,
            "EPS Δ":         r["eps_delta_pct"],
            "FCF/sh Δ":      r["fcf_delta_pct"],
            "Accretive":     r["is_accretive"],
        })
    return pd.DataFrame(results)

# ══════════════════════════════════════════════════════════════
# ── OPTION B: STRATEGY SCENARIOS ─────────────────────────────
# ══════════════════════════════════════════════════════════════
def build_strategy_scenarios(fin, scenarios, wacc, tgr, exit_mult):
    """
    scenarios: list of dicts with keys:
        name, description, rev_growth, ebit_margin, da_pct, capex_pct,
        nwc_pct, wacc_delta, tgr_delta
    Returns list of scenario results with DCF values.
    """
    results = []
    for sc in scenarios:
        sc_wacc = wacc + sc.get("wacc_delta", 0)
        sc_tgr  = tgr  + sc.get("tgr_delta",  0)
        dcf = quick_dcf(fin, sc["rev_growth"], sc["ebit_margin"],
                        sc.get("da_pct", fin["da"]/fin["revenue"] if fin["revenue"] > 0 else 0.04),
                        sc.get("capex_pct", fin["capex"]/fin["revenue"] if fin["revenue"] > 0 else 0.05),
                        sc.get("nwc_pct", 0.04),
                        sc_wacc, sc_tgr, exit_mult)
        if dcf:
            results.append({
                "name":        sc["name"],
                "description": sc["description"],
                "color":       sc["color"],
                "icon":        sc["icon"],
                "rev_growth":  sc["rev_growth"],
                "ebit_margin": sc["ebit_margin"],
                "wacc":        sc_wacc,
                "tgr":         sc_tgr,
                "dcf":         dcf,
                "price_ggm":   dcf["price_ggm"],
                "price_em":    dcf["price_em"],
                "avg_price":   (dcf["price_ggm"] + dcf["price_em"])/2,
                "ev_ggm":      dcf["ev_ggm"],
            })
    return results

def strategy_value_waterfall(base_price, scenarios, labels):
    """Waterfall showing value uplift/destruction from each scenario vs base."""
    base = base_price
    deltas = [s["avg_price"] - base for s in scenarios[1:]]
    measures = ["absolute"] + ["relative"]*len(deltas) + ["total"]
    x = [labels[0]] + labels[1:] + ["Strategy Range"]
    y = [base] + deltas + [0]
    colors = []
    for d in deltas:
        colors.append("#3fb950" if d >= 0 else "#f85149")

    fig = go.Figure(go.Waterfall(
        orientation="v", measure=measures,
        x=x, y=y,
        connector=dict(line=dict(color="#1e2733")),
        decreasing=dict(marker=dict(color="#f85149")),
        increasing=dict(marker=dict(color="#3fb950")),
        totals=dict(marker=dict(color="#58a6ff")),
        text=[f"${v:.2f}" for v in [base]+deltas+[base+sum(deltas)]],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=10),
    ))
    fig.update_layout(title="Value Impact by Strategic Scenario", height=350, **CHART)
    return fig

# ══════════════════════════════════════════════════════════════
# ── OPTION C: SECTOR DASHBOARD ────────────────────────────────
# ══════════════════════════════════════════════════════════════
def sector_dcf_bar(sector_results, cur_prices):
    """Side-by-side bar chart of DCF implied prices vs market."""
    tickers  = [r["ticker"] for r in sector_results]
    dcf_ggm  = [r["dcf"]["price_ggm"] if r["dcf"] else np.nan for r in sector_results]
    dcf_em   = [r["dcf"]["price_em"]  if r["dcf"] else np.nan for r in sector_results]
    market   = [r["fin"]["price"] for r in sector_results]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="Market Price",  x=tickers, y=market,
        marker_color="#484f58", opacity=0.8))
    fig.add_trace(go.Bar(name="DCF — GGM",     x=tickers, y=dcf_ggm,
        marker_color="#3fb950", opacity=0.85))
    fig.add_trace(go.Bar(name="DCF — Exit Mult",x=tickers,y=dcf_em,
        marker_color="#d29922", opacity=0.75))
    fig.update_layout(barmode="group", title="DCF Implied vs Market Price ($/share)",
                      height=360, **CHART)
    return fig

def sector_upside_hbar(sector_results):
    """Horizontal bar chart of upside/downside for each company."""
    tickers = [r["ticker"] for r in sector_results]
    upsides = []
    for r in sector_results:
        if r["dcf"] and r["fin"]["price"] and r["fin"]["price"] > 0:
            avg_dcf = (r["dcf"]["price_ggm"] + r["dcf"]["price_em"])/2
            upsides.append(avg_dcf/r["fin"]["price"] - 1)
        else:
            upsides.append(np.nan)
    colors = ["#3fb950" if u >= 0 else "#f85149" for u in upsides]
    fig = go.Figure(go.Bar(
        x=upsides, y=tickers, orientation="h",
        marker_color=colors, opacity=0.85,
        text=[f"{u:+.1%}" if not np.isnan(u) else "N/A" for u in upsides],
        textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11),
    ))
    fig.add_vline(x=0, line_color="#484f58", line_width=1, line_dash="dot")
    fig.update_layout(title="Avg DCF Upside / (Downside) vs Market",
                      height=280, **CHART, xaxis=dict(tickformat=".0%"))
    return fig

def sector_multiples_scatter(sector_results):
    """EV/EBITDA vs EBITDA Margin scatter."""
    tickers  = [r["ticker"] for r in sector_results]
    ev_ebitda= [r["fin"]["ev_ebitda"] or np.nan for r in sector_results]
    ebitda_mg= [r["fin"]["ebitda_mg"]  or np.nan for r in sector_results]
    colors   = ["#3fb950","#58a6ff","#d29922","#f85149","#8b949e","#388bfd"]

    fig = go.Figure()
    for i,(t,x,y) in enumerate(zip(tickers,ebitda_mg,ev_ebitda)):
        if np.isnan(x) or np.isnan(y): continue
        fig.add_trace(go.Scatter(
            x=[x], y=[y], mode="markers+text",
            name=t, text=[t],
            textposition="top center",
            textfont=dict(family="JetBrains Mono", size=10),
            marker=dict(size=16, color=colors[i%len(colors)]),
        ))
    fig.update_layout(title="EV/EBITDA vs EBITDA Margin — Relative Positioning",
                      height=340, showlegend=False, **CHART,
                      xaxis_title="EBITDA Margin", yaxis_title="EV/EBITDA",
                      xaxis=dict(tickformat=".1%"))
    return fig

def generate_thesis(sector_results, rf=0.043, api_key=None):
    """Generate a ~300-word sector thesis using Claude API if available."""
    # Build data summary for the prompt
    rows = []
    for r in sector_results:
        fin = r["fin"]
        dcf = r["dcf"]
        if dcf:
            avg_dcf = (dcf["price_ggm"] + dcf["price_em"])/2
            upside  = avg_dcf/fin["price"] - 1 if fin["price"] else np.nan
        else:
            upside = np.nan
        rows.append(
            f"  {fin['ticker']} ({fin['name']}): Price ${fin['price']:.2f}, "
            f"DCF avg ${avg_dcf:.2f}, implied upside {upside:+.1%}, "
            f"EV/EBITDA {fin['ev_ebitda']:.1f}x, EBITDA margin {fin['ebitda_mg']:.1%}" if dcf and not np.isnan(upside) else
            f"  {fin['ticker']}: insufficient data"
        )
    data_block = "\n".join(rows)
    sector_name = sector_results[0]["fin"]["sector"] if sector_results else "this sector"

    prompt = f"""You are an equity research analyst. Write a concise 280-320 word investment thesis 
on {sector_name} based on the following DCF analysis output. 

Data:
{data_block}

Structure:
1. One sentence sector backdrop (macro/industry context).
2. Which company is most undervalued on DCF and why the spread to market is notable.
3. Which company is most overvalued or fairly valued.
4. Key risks to the DCF assumptions (growth, margin, cost of capital).
5. One-sentence bottom line recommendation (most attractive vs avoid).

Write in a professional equity research tone. Use specific numbers from the data. 
Do NOT use bullet points — write in paragraphs. Approximately 300 words."""

    if CLAUDE_AVAILABLE and api_key:
        try:
            client   = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=600,
                messages=[{"role":"user","content":prompt}]
            )
            return response.content[0].text
        except Exception as e:
            return f"[Claude API error: {e}]\n\nFallback prompt:\n{prompt}"
    else:
        # Fallback: template-based thesis
        if not sector_results: return "No data available."
        valid = [r for r in sector_results if r["dcf"] and r["fin"]["price"]]
        if not valid: return "Insufficient data to generate thesis."

        upsides = []
        for r in valid:
            avg = (r["dcf"]["price_ggm"]+r["dcf"]["price_em"])/2
            upsides.append((r["fin"]["ticker"], avg/r["fin"]["price"]-1, avg, r["fin"]["price"]))
        upsides.sort(key=lambda x: x[1], reverse=True)

        best   = upsides[0]
        worst  = upsides[-1]
        sector = valid[0]["fin"]["sector"]

        return f"""The {sector} sector is navigating a period of shifting fundamentals — 
evolving commodity cycles, cost pressures, and capital allocation discipline are 
driving divergence in intrinsic value across the peer group.

Our DCF analysis identifies **{best[0]}** as the most compelling opportunity, 
trading at ${best[3]:.2f} against a blended DCF value of ${best[2]:.2f} — 
implying {best[1]:+.1%} upside. This discount likely reflects near-term 
sentiment overhang rather than fundamental deterioration; our model suggests 
the market is underpricing the company's normalized free cash flow generation 
relative to peers.

At the other end, **{worst[0]}** screens as the most fully priced, 
trading at ${worst[3]:.2f} with our DCF implying ${worst[2]:.2f} 
({worst[1]:+.1%}). This premium may be justified by superior capital 
returns or balance sheet quality, but it limits the margin of safety 
for new investors.

Key risks to our analysis include the sensitivity of terminal value assumptions 
to WACC and long-run growth rates — given that TV represents 65–80% of 
enterprise value in most names, a 100bps change in WACC shifts implied prices 
materially. Additionally, near-term revenue growth projections assume stable 
volume trends; any macro deterioration would compress multiples and erode 
our upside cases.

**Bottom line:** {best[0]} offers the most attractive risk/reward in the group 
based on DCF fundamentals. Investors seeking sector exposure should overweight 
{best[0]} and treat {worst[0]} as a trim candidate at current levels."""

# ══════════════════════════════════════════════════════════════
# PLOTS FOR M&A
# ══════════════════════════════════════════════════════════════
def plot_accretion_sweep(sweep_df):
    prems  = sweep_df["Premium"].tolist()
    eps_d  = sweep_df["EPS Δ"].tolist()
    fcf_d  = sweep_df["FCF/sh Δ"].tolist()
    colors = ["#3fb950" if v >= 0 else "#f85149" for v in eps_d]

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["EPS Accretion / (Dilution) by Premium",
                                        "FCF/Share Accretion / (Dilution) by Premium"])
    fig.add_trace(go.Bar(x=prems, y=[v*100 for v in eps_d],
                         marker_color=colors, name="EPS Δ%",
                         text=[f"{v:+.1%}" for v in eps_d], textposition="outside",
                         textfont=dict(family="JetBrains Mono", size=9)), row=1, col=1)
    fig.add_trace(go.Bar(x=prems, y=[v*100 if v else 0 for v in fcf_d],
                         marker_color=["#58a6ff" if (v or 0) >= 0 else "#d29922" for v in fcf_d],
                         name="FCF/sh Δ%",
                         text=[f"{v:+.1%}" if v else "N/A" for v in fcf_d],
                         textposition="outside",
                         textfont=dict(family="JetBrains Mono", size=9)), row=1, col=2)
    for col in [1,2]:
        fig.add_hline(y=0, line_dash="dot", line_color="#484f58", row=1, col=col)
    fig.update_layout(height=340, showlegend=False, **CHART)
    return fig

def plot_deal_funding(cash_pct, deal_ev):
    labels = ["Cash / Debt", "Stock Consideration"]
    values = [cash_pct, 1-cash_pct]
    colors = ["#388bfd","#3fb950"]
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.6,
        marker=dict(colors=colors),
        textfont=dict(family="JetBrains Mono", size=11),
        texttemplate="%{label}<br>%{percent:.0%}",
    ))
    fig.update_layout(
        title=f"Deal Funding Mix — ${deal_ev/1e9:.1f}B Total EV",
        height=280, **CHART,
        annotations=[dict(text=f"${deal_ev/1e9:.1f}B", x=0.5, y=0.5,
                          font=dict(size=16, color="#e6edf3", family="JetBrains Mono"),
                          showarrow=False)]
    )
    return fig

def plot_pro_forma_pnl(acq_fin, tgt_fin, deal):
    cats = ["Revenue","EBITDA","Net Income"]
    acq  = [acq_fin["revenue"]/1e9, acq_fin["ebitda"]/1e9, acq_fin["net_income"]/1e9]
    tgt  = [tgt_fin["revenue"]/1e9, tgt_fin["ebitda"]/1e9, tgt_fin["net_income"]/1e9]
    comb = [deal["combined_rev"]/1e9, deal["combined_ebitda"]/1e9, deal["combined_net"]/1e9]

    fig = go.Figure()
    fig.add_trace(go.Bar(name=acq_fin["ticker"], x=cats, y=acq, marker_color="#388bfd", opacity=0.8))
    fig.add_trace(go.Bar(name=tgt_fin["ticker"], x=cats, y=tgt, marker_color="#d29922", opacity=0.8))
    fig.add_trace(go.Bar(name="Pro-forma Combined", x=cats, y=comb, marker_color="#3fb950", opacity=0.9))
    fig.update_layout(barmode="group", title="Standalone vs Pro-forma Financials ($B)",
                      height=320, **CHART)
    return fig

def plot_strategy_bars(scenario_results, cur_price, fin_name):
    names    = [s["name"] for s in scenario_results]
    ggm_vals = [s["price_ggm"] for s in scenario_results]
    em_vals  = [s["price_em"]  for s in scenario_results]
    colors   = [s["color"] for s in scenario_results]

    fig = go.Figure()
    fig.add_trace(go.Bar(name="GGM Price",  x=names, y=ggm_vals,
        marker_color=[c+"aa" for c in ["#3fb95099","#388bfd99","#f8514999"]],
        text=[f"${v:.2f}" for v in ggm_vals], textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11)))
    fig.add_trace(go.Bar(name="Exit Mult",  x=names, y=em_vals,
        marker_color=colors, opacity=0.6,
        text=[f"${v:.2f}" for v in em_vals], textposition="outside",
        textfont=dict(family="JetBrains Mono", size=11)))
    fig.add_hline(y=cur_price, line_dash="dot", line_color="#484f58",
                  annotation_text=f"Market ${cur_price:.2f}",
                  annotation_font=dict(color="#484f58", family="JetBrains Mono", size=10))
    fig.update_layout(barmode="group", title=f"{fin_name} — Implied Value by Strategy",
                      height=340, **CHART)
    return fig

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 6px 0;'>
      <div style='font-family:"JetBrains Mono",monospace;font-size:17px;font-weight:700;
           color:#e6edf3;'>⬡ Consulting Suite</div>
      <div style='font-size:10px;color:#30363d;font-family:"JetBrains Mono",monospace;
           text-transform:uppercase;letter-spacing:2px;margin-top:3px;'>
           M&A · Strategy · Sector</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sb-section">Module</div>', unsafe_allow_html=True)
    module = st.radio("", ["A — M&A Screen", "B — Strategy Scenarios", "C — Sector Dashboard"],
                      label_visibility="collapsed")

    # ── Module A inputs ───────────────────────────────────────
    if module == "A — M&A Screen":
        st.markdown('<div class="sb-section">Companies</div>', unsafe_allow_html=True)
        acq_ticker = st.text_input("Acquirer Ticker", value="MSFT").upper().strip()
        tgt_ticker = st.text_input("Target Ticker",   value="ATVI").upper().strip()

        st.markdown('<div class="sb-section">Deal Structure</div>', unsafe_allow_html=True)
        premium_pct    = st.slider("Offer Premium",     0.0, 0.80, 0.30, 0.05, format="%.0f%%")
        pct_cash       = st.slider("% Cash Funding",    0.0, 1.00, 0.50, 0.05, format="%.0f%%")
        financing_rate = st.slider("Debt Financing Rate",0.02,0.10,0.05,0.005,format="%.2f%%")

        st.markdown('<div class="sb-section">Synergies</div>', unsafe_allow_html=True)
        cost_syn_pct = st.slider("Cost Synergies (% of target rev)", 0.0, 0.20, 0.05, 0.005, format="%.1f%%",
                                  help="Annual cost savings as % of target revenue. "
                                       "Typically 3-10% for strategic acquirers.")
        rev_syn_pct  = st.slider("Revenue Synergies (% of combined rev)", 0.0, 0.10, 0.02, 0.005, format="%.1f%%",
                                  help="Cross-sell/upsell synergies. Be conservative — "
                                       "revenue synergies are harder to achieve than cost cuts.")

        st.markdown('<div class="sb-section">DCF Assumptions (Target)</div>', unsafe_allow_html=True)
        tgt_growth  = st.slider("Target Rev Growth", -0.05, 0.30, 0.08, 0.005, format="%.1f%%")
        tgt_margin  = st.slider("Target EBIT Margin",  0.0, 0.50, 0.20, 0.005, format="%.1f%%")
        tgt_wacc    = st.slider("Target WACC",          0.04, 0.18, 0.09, 0.005, format="%.2f%%")
        tgt_tgr     = st.slider("Terminal Growth Rate", 0.005,0.04, 0.025,0.005, format="%.2f%%")
        tgt_mult    = st.slider("Exit EV/EBITDA",        5.0, 25.0,  12.0,  0.5, format="%.1fx")

    # ── Module B inputs ───────────────────────────────────────
    elif module == "B — Strategy Scenarios":
        st.markdown('<div class="sb-section">Company</div>', unsafe_allow_html=True)
        base_ticker = st.text_input("Ticker", value="AAPL").upper().strip()

        st.markdown('<div class="sb-section">Base WACC</div>', unsafe_allow_html=True)
        b_wacc = st.slider("WACC",  0.04, 0.16, 0.09, 0.005, format="%.2f%%")
        b_tgr  = st.slider("Terminal Growth", 0.005, 0.04, 0.025, 0.005, format="%.2f%%")
        b_mult = st.slider("Exit Multiple",     5.0,  25.0,  12.0,   0.5, format="%.1fx")

        st.markdown('<div class="sb-section">Scenario 1 — Base Case</div>', unsafe_allow_html=True)
        s1_growth  = st.slider("Rev Growth", -0.05, 0.30, 0.08, 0.005, format="%.1f%%", key="s1g")
        s1_margin  = st.slider("EBIT Margin",  0.0, 0.50, 0.20, 0.005, format="%.1f%%", key="s1m")

        st.markdown('<div class="sb-section">Scenario 2 — Market Expansion</div>', unsafe_allow_html=True)
        s2_name    = st.text_input("Scenario Name", value="Market Expansion", key="s2n")
        s2_growth  = st.slider("Rev Growth (higher)",  0.0, 0.50, 0.18, 0.005, format="%.1f%%", key="s2g",
                                help="Higher growth from entering new markets, but with heavier reinvestment.")
        s2_margin  = st.slider("EBIT Margin (lower)",  0.0, 0.50, 0.16, 0.005, format="%.1f%%", key="s2m",
                                help="Margin compresses due to expansion opex and higher CapEx.")
        s2_capex   = st.slider("CapEx % Rev (higher)", 0.01,0.20, 0.10, 0.005, format="%.1f%%", key="s2c")
        s2_wacc_d  = st.slider("WACC Δ (expansion risk)", -0.02, 0.03, 0.01, 0.005, format="%.2f%%", key="s2w")
        s2_tgr_d   = st.slider("TGR Δ (larger TAM)",  -0.01, 0.02, 0.005,0.005, format="%.2f%%", key="s2t")

        st.markdown('<div class="sb-section">Scenario 3 — Cost Restructuring</div>', unsafe_allow_html=True)
        s3_name    = st.text_input("Scenario Name", value="Cost Restructuring", key="s3n")
        s3_growth  = st.slider("Rev Growth (lower)",    -0.05,0.20, 0.04, 0.005, format="%.1f%%", key="s3g",
                                help="Slower growth as the business prioritizes margin over volume.")
        s3_margin  = st.slider("EBIT Margin (higher)",  0.0,  0.60, 0.28, 0.005, format="%.1f%%", key="s3m",
                                help="Margin expands from headcount reduction and efficiency gains.")
        s3_capex   = st.slider("CapEx % Rev (lower)",   0.01, 0.15, 0.04, 0.005, format="%.1f%%", key="s3c")
        s3_wacc_d  = st.slider("WACC Δ (lower risk)",  -0.02, 0.02,-0.005,0.005, format="%.2f%%", key="s3w")
        s3_tgr_d   = st.slider("TGR Δ",               -0.01, 0.01, -0.005,0.005, format="%.2f%%", key="s3t")

    # ── Module C inputs ───────────────────────────────────────
    else:
        st.markdown('<div class="sb-section">Sector</div>', unsafe_allow_html=True)
        sector_label = st.text_input("Sector Label", value="Canadian Energy")
        sector_tickers_raw = st.text_area(
            "Tickers (one per line)", value="CVE\nSU\nTOU\nBTE\nCNQ",
            height=130, help="Enter 3–6 tickers. Each will be individually DCF'd and compared.")

        st.markdown('<div class="sb-section">Shared DCF Assumptions</div>', unsafe_allow_html=True)
        sec_growth  = st.slider("Revenue Growth",      -0.05, 0.30, 0.06,  0.005, format="%.1f%%")
        sec_margin  = st.slider("EBIT Margin",           0.0,  0.50, 0.22,  0.005, format="%.1f%%")
        sec_da_pct  = st.slider("D&A % Rev",            0.01,  0.20, 0.07,  0.005, format="%.1f%%")
        sec_capex   = st.slider("CapEx % Rev",          0.01,  0.30, 0.12,  0.005, format="%.1f%%")
        sec_tgr     = st.slider("Terminal Growth Rate", 0.005, 0.04, 0.02,  0.005, format="%.2f%%")
        sec_mult    = st.slider("Exit EV/EBITDA",         4.0,  20.0,  7.0,   0.5, format="%.1fx")

        st.markdown('<div class="sb-section">Thesis Generation</div>', unsafe_allow_html=True)
        claude_key = st.text_input("Claude API Key (optional)",
                                    type="password",
                                    help="Paste your Anthropic API key to auto-generate "
                                         "a 300-word equity research thesis. "
                                         "Leave blank to use the template version.")

    st.markdown("<div style='margin:12px 0 4px 0;'></div>", unsafe_allow_html=True)
    run = st.button("▶  Run Analysis", use_container_width=True, type="primary")
    st.markdown("<div style='margin:8px 0 0;'></div>", unsafe_allow_html=True)
    if st.button("← Home", use_container_width=True):
        st.switch_page("Home.py")
# ══════════════════════════════════════════════════════════════
# LANDING
# ══════════════════════════════════════════════════════════════
if not run:
    st.markdown("""
    <div style='display:flex;flex-direction:column;align-items:center;justify-content:center;
         height:75vh;text-align:center;gap:14px;'>
      <div style='font-family:"JetBrains Mono",monospace;font-size:52px;color:#1e2733;'>⬡</div>
      <div style='font-family:"JetBrains Mono",monospace;font-size:28px;font-weight:700;
           color:#e6edf3;letter-spacing:-1px;'>DCF Consulting Suite</div>
      <div style='display:flex;gap:10px;flex-wrap:wrap;justify-content:center;margin-top:4px;'>
        <span class='badge badge-up'>A — M&A Accretion / Dilution</span>
        <span class='badge badge-neu'>B — Strategic Value Analysis</span>
        <span class='badge badge-gold'>C — Sector Valuation Dashboard</span>
      </div>
      <div style='color:#484f58;font-size:13px;max-width:500px;line-height:1.8;margin-top:4px;'>
        Professional-grade consulting outputs built on live DCF data.
        Select a module in the sidebar and click Run Analysis.
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════
# MODULE A — M&A SCREEN
# ══════════════════════════════════════════════════════════════
if module == "A — M&A Screen":
    with st.spinner(f"Fetching data for {acq_ticker} and {tgt_ticker}…"):
        acq_data, acq_err = fetch(acq_ticker)
        tgt_data, tgt_err = fetch(tgt_ticker)

    if acq_err: st.error(f"Acquirer: {acq_err}"); st.stop()
    if tgt_err: st.error(f"Target: {tgt_err}");   st.stop()

    acq_fin  = extract_financials(acq_data)
    tgt_fin  = extract_financials(tgt_data)
    acq_wacc, acq_ke, acq_kd, acq_ew, acq_dw = estimate_wacc(acq_fin)

    # DCF on target
    tgt_da_pct    = tgt_fin["da"]/tgt_fin["revenue"]    if tgt_fin["revenue"] > 0 else 0.04
    tgt_capex_pct = tgt_fin["capex"]/tgt_fin["revenue"] if tgt_fin["revenue"] > 0 else 0.05
    tgt_nwc_pct   = abs(tgt_fin["chg_nwc"])/tgt_fin["revenue"] if tgt_fin["revenue"] > 0 else 0.03

    tgt_dcf = quick_dcf(tgt_fin, tgt_growth, tgt_margin,
                         tgt_da_pct, tgt_capex_pct, tgt_nwc_pct,
                         tgt_wacc, tgt_tgr, tgt_mult)

    # Run deal model
    deal = run_ma_screen(acq_fin, tgt_fin, premium_pct, pct_cash,
                          cost_syn_pct, rev_syn_pct, financing_rate,
                          tgt_dcf, acq_wacc)

    # Premium sweep
    with st.spinner("Running premium sweep…"):
        sweep_df = ma_premium_sweep(acq_fin, tgt_fin, pct_cash, cost_syn_pct,
                                     rev_syn_pct, financing_rate, tgt_dcf, acq_wacc)

    # ── Header ────────────────────────────────────────────────
    acc_cls  = "badge-up" if deal["is_accretive"] else "badge-dn"
    acc_text = f"{'▲ ACCRETIVE' if deal['is_accretive'] else '▼ DILUTIVE'} {deal['eps_delta_pct']:+.1%} to EPS" if not np.isnan(deal["eps_delta_pct"]) else "EPS Impact N/A"
    be_str   = f"${deal['breakeven_premium']:.0%}" if deal["breakeven_premium"] else "N/A"

    st.markdown(f"""
    <div style='padding:8px 0 18px 0;'>
      <div style='font-family:"JetBrains Mono",monospace;font-size:32px;font-weight:700;
           color:#e6edf3;line-height:1;'>
        {acq_fin["ticker"]} acquires {tgt_fin["ticker"]}
      </div>
      <div style='font-size:13px;color:#484f58;margin:4px 0 12px 0;'>
        {acq_fin["name"]} &nbsp;·&nbsp; {tgt_fin["name"]}
      </div>
      <span class='{acc_cls} badge'>{acc_text}</span>
      &nbsp;
      <span class='badge badge-gold'>Offer ${deal['offer_price']:.2f} · {deal['premium_pct']:.0%} premium</span>
      &nbsp;
      <span class='badge badge-neu'>Break-even premium: {be_str}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI row ───────────────────────────────────────────────
    def card(title, val, sub="", accent="#3fb950"):
        return f"""<div class='card'>
          <div class='card-accent' style='background:{accent};'></div>
          <div class='card-title'>{title}</div>
          <div class='card-value'>{val}</div>
          <div class='card-sub'>{sub}</div>
        </div>"""

    k1,k2,k3,k4,k5 = st.columns(5)
    with k1: st.markdown(card("Deal EV",       fmt(deal["deal_ev"],"$B"),    f"{deal['premium_pct']:.0%} premium"), unsafe_allow_html=True)
    with k2: st.markdown(card("EPS Impact",    f"{deal['eps_delta_pct']:+.1%}" if not np.isnan(deal['eps_delta_pct']) else "N/A",
                               "Accretive" if deal["is_accretive"] else "Dilutive",
                               "#3fb950" if deal["is_accretive"] else "#f85149"), unsafe_allow_html=True)
    with k3: st.markdown(card("FCF/sh Impact", f"{deal['fcf_delta_pct']:+.1%}" if not np.isnan(deal['fcf_delta_pct']) else "N/A",
                               "Pro-forma vs standalone", "#58a6ff"), unsafe_allow_html=True)
    with k4: st.markdown(card("Cost Synergies",fmt(deal["cost_synergies"],"$M"),
                               f"{cost_syn_pct:.1%} of target rev", "#d29922"), unsafe_allow_html=True)
    with k5: st.markdown(card("Goodwill",      fmt(deal["goodwill"],"$B"),
                               "Estimated at close", "#8b949e"), unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Tabs ──────────────────────────────────────────────────
    t1, t2, t3, t4, t5 = st.tabs([
        "Deal Summary", "Accretion / Dilution", "Pro-forma Financials",
        "Target DCF", "Deal Thesis"])

    with t1:
        # Accretion verdict box
        if deal["is_accretive"]:
            st.markdown(f"""<div class='accretive-box'>
            ✓ &nbsp; Deal is <strong>EPS accretive</strong> at {deal['premium_pct']:.0%} premium
            with {cost_syn_pct:.1%} cost synergies and {pct_cash:.0%} cash funding.
            Pro-forma EPS of <strong>${deal['pro_forma_eps']:.2f}</strong>
            vs standalone ${deal['acq_eps_before']:.2f} ({deal['eps_delta_pct']:+.1%}).
            Break-even premium before dilution: <strong>{be_str}</strong>.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class='dilutive-box'>
            ✗ &nbsp; Deal is <strong>EPS dilutive</strong> at {deal['premium_pct']:.0%} premium.
            Pro-forma EPS of <strong>${deal['pro_forma_eps']:.2f}</strong>
            vs standalone ${deal['acq_eps_before']:.2f} ({deal['eps_delta_pct']:+.1%}).
            Break-even premium: <strong>{be_str}</strong> —
            reduce premium or increase synergies to reach accretion.
            </div>""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(plot_deal_funding(pct_cash, deal["deal_ev"]), use_container_width=True)
        with c2:
            # Deal metrics table
            st.markdown("<div class='sec-label'>Deal Summary</div>", unsafe_allow_html=True)
            deal_tbl = {
                "Metric": ["Offer Price","Market Price","Premium Paid","Deal Equity Value",
                           "Target Net Debt","Total Deal EV","Cash Funded",
                           "Stock Funded (new shares issued)","New Debt Raised",
                           "Annual Cost Synergies","Annual Revenue Synergies",
                           "Integration Cost (est.)","Goodwill Created",
                           "Intangible Amortization (annual)"],
                "Value":  [f"${deal['offer_price']:.2f}",
                           f"${tgt_fin['price']:.2f}",
                           f"{deal['premium_pct']:.1%}",
                           fmt(deal["equity_val"],"$B"),
                           fmt(tgt_fin["net_debt"],"$B"),
                           fmt(deal["deal_ev"],"$B"),
                           fmt(deal["cash_portion"],"$B"),
                           f"{deal['new_shares']/1e6:.1f}M shares",
                           fmt(deal["new_debt"],"$B"),
                           fmt(deal["cost_synergies"],"$M"),
                           fmt(deal["rev_synergies"],"$M"),
                           fmt(deal["integration_cost"],"$M"),
                           fmt(deal["goodwill"],"$B"),
                           fmt(deal["intangible_amort"],"$M")],
            }
            rows_html = ""
            for k, v in zip(deal_tbl["Metric"], deal_tbl["Value"]):
                rows_html += f"<tr><td>{k}</td><td>{v}</td></tr>"
            st.markdown(f"""<table class='fin-table'>
              <thead><tr><th>Metric</th><th>Value</th></tr></thead>
              <tbody>{rows_html}</tbody></table>""", unsafe_allow_html=True)

    with t2:
        st.markdown("""<div class='info-box'>
        Each bar shows EPS and FCF/share accretion (green) or dilution (red) at the given offer premium,
        assuming the same synergy and funding structure. The break-even premium is where the bar crosses zero.
        </div>""", unsafe_allow_html=True)
        st.plotly_chart(plot_accretion_sweep(sweep_df), use_container_width=True)

        # Sweep table
        display_cols = ["Premium","Offer Price","Deal EV ($B)","EPS Δ","FCF/sh Δ","Accretive"]
        sweep_show = sweep_df.copy()
        sweep_show["EPS Δ"]   = sweep_show["EPS Δ"].map(lambda x: f"{x:+.1%}" if not pd.isna(x) else "N/A")
        sweep_show["FCF/sh Δ"]= sweep_show["FCF/sh Δ"].map(lambda x: f"{x:+.1%}" if not pd.isna(x) else "N/A")
        sweep_show["Offer Price"] = sweep_show["Offer Price"].map(lambda x: f"${x:.2f}")
        sweep_show["Deal EV ($B)"]= sweep_show["Deal EV ($B)"].map(lambda x: f"${x:.1f}B")
        sweep_show["Accretive"]   = sweep_show["Accretive"].map(lambda x: "✓" if x else "✗")
        st.dataframe(sweep_show[display_cols], use_container_width=True, hide_index=True)

    with t3:
        st.plotly_chart(plot_pro_forma_pnl(acq_fin, tgt_fin, deal), use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='sec-label'>Acquirer Standalone</div>", unsafe_allow_html=True)
            for k,v in [("Revenue",fmt(acq_fin["revenue"],"$B")),
                        ("EBITDA", fmt(acq_fin["ebitda"],"$B")),
                        ("EBIT",   fmt(acq_fin["ebit"],"$B")),
                        ("Net Income",fmt(acq_fin["net_income"],"$B")),
                        ("EPS",    f"${deal['acq_eps_before']:.2f}"),
                        ("UFCF",   fmt(acq_fin["ufcf"],"$B")),
                        ("EBIT Margin",f"{acq_fin['ebit']/acq_fin['revenue']:.1%}" if acq_fin['revenue'] else "N/A"),]:
                ca,cb = st.columns([2,1])
                ca.markdown(f"<span style='color:#8b949e;font-size:13px;'>{k}</span>",unsafe_allow_html=True)
                cb.markdown(f"<code style='color:#e6edf3;'>{v}</code>",unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='sec-label'>Pro-forma Combined</div>", unsafe_allow_html=True)
            for k,v in [("Revenue",  fmt(deal["combined_rev"],"$B")),
                        ("EBITDA",   fmt(deal["combined_ebitda"],"$B")),
                        ("EBIT",     fmt(deal["combined_ebit"],"$B")),
                        ("Net Income",fmt(deal["combined_net"],"$B")),
                        ("EPS",      f"${deal['pro_forma_eps']:.2f}"),
                        ("Incr. Interest Expense", fmt(deal["incremental_int"],"$M")),
                        ("Intangible Amort.", fmt(deal["intangible_amort"],"$M")),]:
                ca,cb = st.columns([2,1])
                ca.markdown(f"<span style='color:#8b949e;font-size:13px;'>{k}</span>",unsafe_allow_html=True)
                clr = "#3fb950" if k == "EPS" and deal["is_accretive"] else ("#f85149" if k == "EPS" else "#e6edf3")
                cb.markdown(f"<code style='color:{clr};'>{v}</code>",unsafe_allow_html=True)

    with t4:
        if tgt_dcf:
            tgt_price_ggm = tgt_dcf["price_ggm"]
            tgt_price_em  = tgt_dcf["price_em"]
            tgt_avg       = (tgt_price_ggm + tgt_price_em)/2 if not np.isnan(tgt_price_ggm) else tgt_price_em
            premium_to_dcf= deal["offer_price"]/tgt_avg - 1 if tgt_avg > 0 else np.nan

            badge_vs_dcf = "badge-up" if deal["offer_price"] > tgt_avg else "badge-dn"
            st.markdown(f"""
            <div class='info-box'>
            Offer of <strong>${deal['offer_price']:.2f}</strong> vs target DCF avg of
            <strong>${tgt_avg:.2f}</strong> &nbsp;
            <span class='{badge_vs_dcf} badge'>{'▲' if deal['offer_price']>tgt_avg else '▼'}
            {premium_to_dcf:+.1%} vs intrinsic</span>
            &nbsp;·&nbsp; GGM: ${tgt_price_ggm:.2f} &nbsp;·&nbsp; Exit Mult: ${tgt_price_em:.2f}
            </div>""", unsafe_allow_html=True)

            # Waterfall
            spv = tgt_dcf["pv_fcf"]; tv  = tgt_dcf["pv_tv_g"]
            ev  = tgt_dcf["ev_ggm"]; nd  = tgt_fin["net_debt"]
            eq  = ev - nd; sh = tgt_fin["shares"] or 1e9
            fig_b = go.Figure(go.Waterfall(
                orientation="v", measure=["relative","relative","total","relative","total"],
                x=["PV FCFs","PV TV","EV","Net Debt","Equity"],
                y=[spv/1e9, tv/1e9, 0, -nd/1e9, 0],
                connector=dict(line=dict(color="#1e2733")),
                decreasing=dict(marker=dict(color="#f85149")),
                increasing=dict(marker=dict(color="#3fb950")),
                totals=dict(marker=dict(color="#58a6ff")),
                text=[f"${x:.1f}B" for x in [spv/1e9, tv/1e9, ev/1e9, -nd/1e9, eq/1e9]],
                textposition="outside",
            ))
            fig_b.update_layout(title=f"{tgt_fin['ticker']} DCF Bridge ($B)", height=320, **CHART)
            st.plotly_chart(fig_b, use_container_width=True)

            # Implied multiples
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("DCF GGM",       f"${tgt_price_ggm:.2f}")
            with c2: st.metric("DCF Exit Mult",  f"${tgt_price_em:.2f}")
            with c3: st.metric("Offer Price",    f"${deal['offer_price']:.2f}")
            with c4: st.metric("Offer / DCF",    f"{premium_to_dcf:+.1%}" if not np.isnan(premium_to_dcf) else "N/A")
        else:
            st.warning("Could not compute target DCF — check revenue and EBIT data.")

    with t5:
        st.markdown("<div class='sec-label'>Deal Thesis</div>", unsafe_allow_html=True)
        direction = "accretive" if deal["is_accretive"] else "dilutive"
        syn_value = deal["total_syn_at"]*8  # rough 8x multiple on after-tax synergies
        prem_over = deal["deal_ev"] - (tgt_dcf["ev_ggm"] if tgt_dcf else deal["deal_ev"])

        thesis = f"""At the proposed {deal['premium_pct']:.0%} premium, **{acq_fin['ticker']}**'s acquisition 
of **{tgt_fin['ticker']}** is **{direction}** at the EPS level, with pro-forma EPS of 
${deal['pro_forma_eps']:.2f} versus the standalone ${deal['acq_eps_before']:.2f} 
({deal['eps_delta_pct']:+.1%} impact). The deal is funded {pct_cash:.0%} in cash (financed 
at {financing_rate:.2%}), with the remainder in stock consideration requiring {deal['new_shares']/1e6:.1f}M 
new {acq_fin['ticker']} shares.

**Synergy Case:** Management can justify the {deal['premium_pct']:.0%} premium through 
${deal['cost_synergies']/1e6:.0f}M in annual cost synergies ({cost_syn_pct:.1%} of target revenue) and 
${deal['rev_synergies']/1e6:.0f}M in revenue synergies ({rev_syn_pct:.1%} of combined revenue). 
At an 8x multiple, these synergies are worth approximately {fmt(syn_value, '$B')} — 
{"more than sufficient to justify" if syn_value > prem_over else "partially justifying"} the 
{fmt(prem_over, "$B")} premium paid over {tgt_fin['ticker']}'s DCF intrinsic value.

**Risk Factors:** The break-even premium before dilution is {be_str} — 
{"above the proposed offer, providing buffer" if deal['breakeven_premium'] and deal['breakeven_premium'] > deal['premium_pct'] else "below the proposed offer, meaning execution risk directly threatens EPS accretion"}. 
Revenue synergies are the most uncertain input; stripping them out moves the EPS impact by 
approximately {rev_syn_pct:.0%} of combined revenue divided across {deal['new_shares']/1e6:.0f}M+ diluted shares. 
Integration costs of {fmt(deal['integration_cost'],'$M')} will create a Year 1 earnings drag.

**Bottom Line:** {acq_fin['ticker']} should {"proceed at this premium structure, as the synergy case is credible and the deal strengthens FCF per share" if deal["is_accretive"] else f"renegotiate to below {be_str} premium or increase the cash synergy target above {cost_syn_pct*100:.0f}% of target revenue before proceeding"}.
"""
        # Format as thesis block
        paras = [p.strip() for p in thesis.strip().split("\n\n") if p.strip()]
        thesis_html = "".join(f"<p>{p}</p>" for p in paras)
        st.markdown(f"<div class='thesis-block'>{thesis_html}</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MODULE B — STRATEGY SCENARIOS
# ══════════════════════════════════════════════════════════════
elif module == "B — Strategy Scenarios":
    with st.spinner(f"Fetching data for {base_ticker}…"):
        b_data, b_err = fetch(base_ticker)
    if b_err: st.error(b_err); st.stop()
    b_fin = extract_financials(b_data)

    b_da_pct    = b_fin["da"]/b_fin["revenue"]    if b_fin["revenue"] > 0 else 0.04
    b_capex_pct = b_fin["capex"]/b_fin["revenue"] if b_fin["revenue"] > 0 else 0.05

    # Define scenarios
    scenario_defs = [
        {
            "name":        "Base Case",
            "description": "Current trajectory. Management guidance, no strategic change.",
            "rev_growth":  s1_growth,
            "ebit_margin": s1_margin,
            "da_pct":      b_da_pct,
            "capex_pct":   b_capex_pct,
            "nwc_pct":     0.04,
            "wacc_delta":  0.0,
            "tgr_delta":   0.0,
            "color":       "#58a6ff",
            "icon":        "◈",
        },
        {
            "name":        s2_name,
            "description": "Accelerated revenue growth by entering new markets, "
                           "offset by heavier reinvestment and elevated execution risk.",
            "rev_growth":  s2_growth,
            "ebit_margin": s2_margin,
            "da_pct":      b_da_pct,
            "capex_pct":   s2_capex,
            "nwc_pct":     0.05,
            "wacc_delta":  s2_wacc_d,
            "tgr_delta":   s2_tgr_d,
            "color":       "#3fb950",
            "icon":        "▲",
        },
        {
            "name":        s3_name,
            "description": "Slowing topline in exchange for structurally higher margins "
                           "via cost reduction, headcount optimization, and portfolio pruning.",
            "rev_growth":  s3_growth,
            "ebit_margin": s3_margin,
            "da_pct":      b_da_pct,
            "capex_pct":   s3_capex,
            "nwc_pct":     0.03,
            "wacc_delta":  s3_wacc_d,
            "tgr_delta":   s3_tgr_d,
            "color":       "#d29922",
            "icon":        "⟳",
        },
    ]

    sc_results = build_strategy_scenarios(b_fin, scenario_defs, b_wacc, b_tgr, b_mult)

    base_price  = b_fin["price"]
    base_sc_avg = sc_results[0]["avg_price"] if sc_results else base_price

    # ── Header ────────────────────────────────────────────────
    st.markdown(f"""
    <div style='padding:8px 0 18px 0;'>
      <div style='font-family:"JetBrains Mono",monospace;font-size:32px;font-weight:700;
           color:#e6edf3;line-height:1;'>{base_ticker}</div>
      <div style='font-size:13px;color:#484f58;margin:4px 0 12px 0;'>
        {b_fin["name"]} &nbsp;·&nbsp; {b_fin["sector"]} &nbsp;·&nbsp; {b_fin["industry"]}
      </div>
      <span class='badge badge-neu'>Current: ${base_price:.2f}</span>
      &nbsp;
      <span class='badge badge-neu'>Base DCF avg: ${base_sc_avg:.2f}</span>
      &nbsp;
      <span class='badge badge-gold'>{len(sc_results)} scenarios computed</span>
    </div>""", unsafe_allow_html=True)

    # ── KPI cards ─────────────────────────────────────────────
    def s_card(sc, cur):
        avg = sc["avg_price"]; up = avg/cur - 1 if cur else 0
        cls = "#3fb950" if up >= 0 else "#f85149"
        return f"""<div class='card' style='border-color:{sc["color"]}33;'>
          <div class='card-accent' style='background:{sc["color"]};'></div>
          <div class='card-title'>{sc["icon"]} {sc["name"]}</div>
          <div class='card-value' style='color:{sc["color"]};'>${avg:.2f}</div>
          <div class='card-sub' style='color:{cls};'>{up:+.1%} vs market</div>
        </div>"""

    cols = st.columns(len(sc_results))
    for i, (sc, col) in enumerate(zip(sc_results, cols)):
        with col: st.markdown(s_card(sc, base_price), unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    stabs = st.tabs(["Strategy Overview","Value Waterfall","Scenario Detail","Assumptions","Consulting Output"])

    with stabs[0]:
        st.plotly_chart(plot_strategy_bars(sc_results, base_price, b_fin["name"]),
                        use_container_width=True)

        # Summary table
        st.markdown("<div class='sec-label'>Scenario Comparison</div>", unsafe_allow_html=True)
        tbl_data = {
            "Scenario":      [s["name"] for s in sc_results],
            "Rev Growth":    [f"{s['rev_growth']:.1%}" for s in sc_results],
            "EBIT Margin":   [f"{s['ebit_margin']:.1%}" for s in sc_results],
            "WACC":          [f"{s['wacc']:.2%}" for s in sc_results],
            "TGR":           [f"{s['tgr']:.2%}" for s in sc_results],
            "GGM Price":     [f"${s['price_ggm']:.2f}" for s in sc_results],
            "Exit Price":    [f"${s['price_em']:.2f}"  for s in sc_results],
            "Avg Price":     [f"${s['avg_price']:.2f}" for s in sc_results],
            "vs Market":     [f"{s['avg_price']/base_price-1:+.1%}" if base_price else "N/A" for s in sc_results],
        }
        st.dataframe(pd.DataFrame(tbl_data), use_container_width=True, hide_index=True)

    with stabs[1]:
        st.markdown("""<div class='info-box'>
        The waterfall shows how each strategic choice <strong>adds or destroys value</strong>
        relative to the base case. Green bars = value-creating strategy. Red bars = value-destroying.
        This is the standard consulting output for strategic option valuation.
        </div>""", unsafe_allow_html=True)
        fig_wf = strategy_value_waterfall(
            base_sc_avg,
            sc_results,
            [s["name"] for s in sc_results]
        )
        st.plotly_chart(fig_wf, use_container_width=True)

        # Value attribution
        st.markdown("<div class='sec-label'>Value Creation / Destruction</div>", unsafe_allow_html=True)
        for sc in sc_results[1:]:
            delta = sc["avg_price"] - base_sc_avg
            pct   = delta/base_sc_avg if base_sc_avg != 0 else 0
            cls   = "accretive-box" if delta >= 0 else "dilutive-box"
            sym   = "▲" if delta >= 0 else "▼"
            st.markdown(f"""<div class='{cls}'>
            {sym} &nbsp; <strong>{sc["name"]}</strong>: implied value of ${sc["avg_price"]:.2f}
            vs base of ${base_sc_avg:.2f} — a <strong>{delta:+.2f} ({pct:+.1%})</strong>
            per share swing. {sc["description"]}
            </div>""", unsafe_allow_html=True)

    with stabs[2]:
        for sc in sc_results:
            with st.expander(f"{sc['icon']}  {sc['name']} — ${sc['avg_price']:.2f}"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("GGM Price",   f"${sc['price_ggm']:.2f}")
                c2.metric("Exit Price",  f"${sc['price_em']:.2f}")
                c3.metric("EV (GGM)",    fmt(sc["ev_ggm"],"$B"))
                c4.metric("PV of FCFs",  fmt(sc["dcf"]["pv_fcf"],"$B"))

                # FCF bar chart
                yrs  = [f"Y+{i+1}" for i in range(len(sc["dcf"]["ufcfs"]))]
                ufcf = [v/1e9 for v in sc["dcf"]["ufcfs"]]
                pv   = [v/1e9 for v in sc["dcf"]["pv_fcfs"]]
                fig_sc = go.Figure()
                fig_sc.add_trace(go.Bar(x=yrs, y=ufcf, name="UFCF",   marker_color=sc["color"], opacity=0.8))
                fig_sc.add_trace(go.Bar(x=yrs, y=pv,   name="PV FCF", marker_color="#484f58",  opacity=0.6))
                fig_sc.update_layout(barmode="group", title=f"{sc['name']} — Annual UFCF ($B)",
                                     height=250, **CHART)
                st.plotly_chart(fig_sc, use_container_width=True)

    with stabs[3]:
        st.markdown("<div class='sec-label'>Base Company Financials (LTM)</div>", unsafe_allow_html=True)
        fin_rows = [
            ("Revenue",      fmt(b_fin["revenue"],"$B")),
            ("EBIT",         fmt(b_fin["ebit"],"$B")),
            ("EBITDA",       fmt(b_fin["ebitda"],"$B")),
            ("Net Income",   fmt(b_fin["net_income"],"$B")),
            ("D&A",          fmt(b_fin["da"],"$M")),
            ("CapEx",        fmt(b_fin["capex"],"$M")),
            ("SBC",          fmt(b_fin["sbc"],"$M")),
            ("UFCF",         fmt(b_fin["ufcf"],"$B")),
            ("Net Debt",     fmt(b_fin["net_debt"],"$B")),
            ("Shares (M)",   f"{b_fin['shares']/1e6:,.0f}" if b_fin["shares"] else "N/A"),
            ("EBIT Margin",  f"{b_fin['ebit']/b_fin['revenue']:.1%}" if b_fin["revenue"] else "N/A"),
        ]
        rows_html = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k,v in fin_rows)
        st.markdown(f"""<table class='fin-table'>
          <thead><tr><th>Metric</th><th>Value</th></tr></thead>
          <tbody>{rows_html}</tbody></table>""", unsafe_allow_html=True)

    with stabs[4]:
        st.markdown("<div class='sec-label'>Consulting Output — Strategic Value Analysis</div>", unsafe_allow_html=True)

        # Generate consulting-style output
        best_sc  = max(sc_results, key=lambda s: s["avg_price"])
        worst_sc = min(sc_results, key=lambda s: s["avg_price"])
        rng      = best_sc["avg_price"] - worst_sc["avg_price"]

        output = f"""**Subject:** {b_fin["name"]} ({base_ticker}) — Strategic Scenario Valuation

**Date:** {pd.Timestamp.now().strftime("%B %d, %Y")} &nbsp;&nbsp; **Prepared by:** DCF Consulting Suite

---

**Executive Summary**

Our three-scenario DCF analysis of {b_fin["name"]} reveals a ${rng:.2f} per share valuation 
range driven primarily by the trade-off between growth investment and margin improvement. 
The market currently prices the stock at ${base_price:.2f}, which implies the market is 
pricing in approximately the **{min(sc_results, key=lambda s: abs(s['avg_price']-base_price))['name']}** trajectory.

**Scenario Analysis**
"""
        for sc in sc_results:
            up = sc["avg_price"]/base_price - 1 if base_price else 0
            output += f"""
**{sc['icon']} {sc['name']} — ${sc['avg_price']:.2f} ({up:+.1%} vs market)**

Assumes {sc['rev_growth']:.1%} revenue growth and {sc['ebit_margin']:.1%} EBIT margin. 
DCF GGM: ${sc['price_ggm']:.2f} · Exit Multiple: ${sc['price_em']:.2f}. 
{sc['description']}
"""

        output += f"""
**Key Insight**

The highest-value path is **{best_sc['name']}** at ${best_sc['avg_price']:.2f}, 
but it requires {best_sc['rev_growth']:.1%} sustained revenue growth — 
{'above' if best_sc['rev_growth'] > b_fin['rev_growth'] else 'below'} the company's current 
trailing growth rate of {b_fin['rev_growth']:.1%}. The spread between best and worst 
scenario is ${rng:.2f}/share — meaning execution on the strategic choice is worth 
{rng/base_price:.0%} of market cap.

**Recommendation**

{best_sc['name']} creates the most value in absolute terms. However, given the execution 
risk and elevated reinvestment requirements, we recommend monitoring two leading indicators: 
(1) EBIT margin trajectory over the next 2 quarters, and (2) revenue growth vs. company guidance. 
If both track toward the {best_sc['name']} path, the current market price 
of ${base_price:.2f} represents a compelling entry point.
"""
        paras = [p.strip() for p in output.strip().split("\n\n") if p.strip()]
        thesis_html = "".join(
            f"<p><strong>{p.split('**')[1]}</strong>{p.split('**')[2] if len(p.split('**'))>2 else ''}</p>"
            if p.startswith("**") and p.count("**") >= 2 else f"<p>{p}</p>"
            for p in paras
        )
        st.markdown(f"<div class='thesis-block'>{output.replace('**','<strong>',1).replace('**','</strong>',1)}</div>",
                    unsafe_allow_html=True)

        # Export
        export_text = "\n\n".join(paras)
        st.download_button("⬇  Download Consulting Output (.txt)",
                           data=export_text.encode(),
                           file_name=f"{base_ticker}_strategy_scenarios.txt",
                           mime="text/plain", use_container_width=False)

# ══════════════════════════════════════════════════════════════
# MODULE C — SECTOR DASHBOARD
# ══════════════════════════════════════════════════════════════
else:
    sector_tickers = [t.strip().upper() for t in sector_tickers_raw.strip().split("\n")
                      if t.strip()][:6]

    if len(sector_tickers) < 2:
        st.warning("Enter at least 2 tickers in the sidebar.")
        st.stop()

    # Fetch all companies
    sector_data = []
    with st.spinner(f"Fetching data for {', '.join(sector_tickers)}…"):
        for ticker in sector_tickers:
            d, err = fetch(ticker)
            if err:
                st.warning(f"⚠ {ticker}: {err}")
                continue
            fin = extract_financials(d)
            sec_wacc, _, _, _, _ = estimate_wacc(fin)
            da_pct_i   = fin["da"]   /fin["revenue"] if fin["revenue"] > 0 else sec_da_pct
            capex_pct_i= fin["capex"]/fin["revenue"] if fin["revenue"] > 0 else sec_capex
            dcf = quick_dcf(fin, sec_growth, sec_margin, da_pct_i, capex_pct_i,
                            0.04, sec_wacc, sec_tgr, sec_mult)
            sector_data.append({"ticker":ticker, "fin":fin, "dcf":dcf, "wacc":sec_wacc})

    if not sector_data:
        st.error("Could not load any company data."); st.stop()

    cur_prices = {r["ticker"]: r["fin"]["price"] for r in sector_data}

    # ── Header ────────────────────────────────────────────────
    st.markdown(f"""
    <div style='padding:8px 0 18px 0;'>
      <div style='font-family:"JetBrains Mono",monospace;font-size:32px;font-weight:700;
           color:#e6edf3;line-height:1;'>{sector_label} &nbsp; Sector</div>
      <div style='font-size:13px;color:#484f58;margin:4px 0 12px 0;'>
        {' &nbsp;·&nbsp; '.join([r['ticker'] for r in sector_data])}
      </div>
      <span class='badge badge-neu'>{len(sector_data)} companies</span>
      &nbsp;
      <span class='badge badge-gold'>WACC range: {min(r["wacc"] for r in sector_data):.1%} – {max(r["wacc"] for r in sector_data):.1%}</span>
    </div>""", unsafe_allow_html=True)

    # ── KPI cards per company ─────────────────────────────────
    cols = st.columns(len(sector_data))
    for i, (r, col) in enumerate(zip(sector_data, cols)):
        fin = r["fin"]; dcf = r["dcf"]
        avg_dcf = (dcf["price_ggm"]+dcf["price_em"])/2 if dcf and not np.isnan(dcf["price_ggm"]) else (dcf["price_em"] if dcf else np.nan)
        upside  = avg_dcf/fin["price"]-1 if (fin["price"] and not np.isnan(avg_dcf)) else np.nan
        clr     = "#3fb950" if (not np.isnan(upside) and upside >= 0) else "#f85149"
        with col:
            st.markdown(f"""<div class='card'>
              <div class='card-accent' style='background:{clr};'></div>
              <div class='card-title'>{r["ticker"]}</div>
              <div class='card-value'>${fin["price"]:.2f}</div>
              <div class='card-sub' style='color:{clr};'>
                DCF: ${avg_dcf:.2f} &nbsp; {upside:+.1%}
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    ctabs = st.tabs(["Valuation Charts","Multiples & Positioning","Peer Table","Equity Research Thesis"])

    with ctabs[0]:
        st.plotly_chart(sector_dcf_bar(sector_data, cur_prices), use_container_width=True)
        st.plotly_chart(sector_upside_hbar(sector_data), use_container_width=True)

    with ctabs[1]:
        st.plotly_chart(sector_multiples_scatter(sector_data), use_container_width=True)

        # Price performance chart
        st.markdown("<div class='sec-label'>Relative Price Performance (3Y, rebased to 100)</div>", unsafe_allow_html=True)
        fig_perf = go.Figure()
        colors_r  = ["#3fb950","#58a6ff","#d29922","#f85149","#8b949e","#388bfd"]
        for i, r in enumerate(sector_data):
            hist = r["fin"]["history"]
            if hist.empty: continue
            rebased = (hist["Close"] / hist["Close"].iloc[0]) * 100
            fig_perf.add_trace(go.Scatter(
                x=hist.index, y=rebased, name=r["ticker"],
                line=dict(color=colors_r[i%len(colors_r)], width=2),
            ))
        fig_perf.add_hline(y=100, line_dash="dot", line_color="#484f58")
        fig_perf.update_layout(title="Relative Performance (rebased 100)", height=320, **CHART)
        st.plotly_chart(fig_perf, use_container_width=True)

    with ctabs[2]:
        st.markdown("<div class='sec-label'>Peer Comparison Table</div>", unsafe_allow_html=True)
        table_rows = []
        for r in sector_data:
            fin = r["fin"]; dcf = r["dcf"]
            avg = (dcf["price_ggm"]+dcf["price_em"])/2 if dcf and not np.isnan(dcf["price_ggm"]) else (dcf["price_em"] if dcf else np.nan)
            up  = f"{avg/fin['price']-1:+.1%}" if (fin["price"] and not np.isnan(avg)) else "N/A"
            table_rows.append({
                "Ticker":       r["ticker"],
                "Company":      fin["name"][:28],
                "Price":        f"${fin['price']:.2f}"    if fin["price"] else "N/A",
                "DCF (avg)":    f"${avg:.2f}"             if not np.isnan(avg) else "N/A",
                "Upside":       up,
                "Mkt Cap":      fmt(fin["mkt_cap"],"$B")  if fin["mkt_cap"] else "N/A",
                "EV/EBITDA":    f"{fin['ev_ebitda']:.1f}x" if not np.isnan(fin['ev_ebitda']) else "N/A",
                "EV/Rev":       f"{fin['ev_rev']:.1f}x"   if not np.isnan(fin['ev_rev'])    else "N/A",
                "EBITDA Mg":    f"{fin['ebitda_mg']:.1%}" if not np.isnan(fin['ebitda_mg']) else "N/A",
                "Rev Growth":   f"{fin['rev_growth']:.1%}"if not np.isnan(fin['rev_growth'])else "N/A",
                "Beta":         f"{fin['beta']:.2f}"      if fin["beta"] else "N/A",
                "Analyst Tgt":  f"${fin['target']:.2f}"   if not np.isnan(fin['target'])    else "N/A",
                "WACC":         f"{r['wacc']:.2%}",
            })
        st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)

        # Download
        csv_out = pd.DataFrame(table_rows).to_csv(index=False).encode()
        st.download_button("⬇  Download Peer Table (CSV)", data=csv_out,
                            file_name=f"{sector_label.replace(' ','_')}_peer_table.csv",
                            mime="text/csv")

    with ctabs[3]:
        st.markdown("<div class='sec-label'>Equity Research Thesis — Auto-Generated</div>", unsafe_allow_html=True)

        api_key = claude_key if claude_key.strip() else None
        with st.spinner("Generating thesis…"):
            thesis_text = generate_thesis(sector_data, api_key=api_key)

        st.markdown(f"<div class='thesis-block'>{thesis_text.replace(chr(10),'<br>')}</div>",
                    unsafe_allow_html=True)

        if not api_key:
            st.markdown("""<div class='info-box'>
            ℹ &nbsp; This thesis was generated from a template. For a fully AI-written,
            context-aware 300-word equity research thesis, paste your Claude API key
            in the sidebar (get one free at console.anthropic.com).
            </div>""", unsafe_allow_html=True)

        # Export
        st.download_button(
            "⬇  Download Thesis (.txt)",
            data=thesis_text.encode(),
            file_name=f"{sector_label.replace(' ','_')}_thesis_{pd.Timestamp.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("""
<div class='footer'>
⬡ DCF CONSULTING SUITE &nbsp;·&nbsp; DATA VIA YFINANCE &nbsp;·&nbsp;
FOR INFORMATIONAL USE ONLY &nbsp;·&nbsp; NOT FINANCIAL ADVICE
</div>""", unsafe_allow_html=True)
