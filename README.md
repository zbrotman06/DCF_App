# DCF_App
# Professional DCF Valuation Engine

A production-grade Streamlit app for discounted cash flow analysis with real-time market data.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the app
streamlit run dcf_app.py
```

## Features

| Module | Details |
|---|---|
| **Live Data** | Pulls income statement, balance sheet & cash flow via `yfinance` (refreshes every 5 min) |
| **UFCF Build-up** | Full transparency: EBIT → NOPAT → +D&A → ΔWC → −CapEx |
| **Dual Terminal Value** | Gordon Growth Model + EV/EBITDA Exit Multiple, side-by-side |
| **Live Controls** | WACC, growth rates, margins, CapEx%, NWC% all update instantly via sliders |
| **Sensitivity Tables** | 7×7 WACC × TGR and WACC × Exit Multiple heatmaps with color coding vs. current price |
| **Tornado Chart** | Visual ranking of which assumptions move the needle most |
| **WACC Decomposition** | CAPM cost of equity + cost of debt waterfall, auto-pulled from financials |
| **Excel Export** | 6-sheet workbook: Summary, Historical UFCF, Projected UFCF, DCF Bridge, 2× Sensitivity |

## Architecture

```
dcf_app.py
├── fetch_data()          — yfinance pull, 5-min cache
├── build_historical_ufcf() — parse raw financials → UFCF bridge
├── project_ufcf()        — forward projections with per-year growth
├── dcf_valuation()       — dual TV methods, PV calculations
├── sensitivity_table()   — 7×7 WACC × param grid
├── build_wacc()          — CAPM + cost of debt from balance sheet
├── export_excel()        — openpyxl multi-sheet workbook
└── Plotly charts         — price history, FCF bars, bridge waterfall, heatmaps
```

## Tickers

Works with any US equity ticker: `AAPL`, `MSFT`, `GOOGL`, `AMZN`, `NVDA`, `META`, `TSLA`, etc.
International tickers may have limited financial data from `yfinance`.

## Notes
- Data sourced from Yahoo Finance via `yfinance` — may have minor discrepancies from SEC filings
- For production use, consider adding FactSet/Bloomberg data feeds
- Not financial advice
