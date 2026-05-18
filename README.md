# Options P&L Dashboard
### IBOT Trading System · Thinkorswim Integration

A real-time options P&L dashboard built with Streamlit. Parses your Thinkorswim
transaction CSV and visualises cumulative P&L, per-ticker breakdown, monthly trends,
and a full searchable trade log.

---

## Quick Start (Local)

### 1. Prerequisites
- Python 3.9+
- pip

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the dashboard
```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## Exporting from Thinkorswim

1. Log into Thinkorswim (desktop or web)
2. Go to **Monitor → Account Statement**
3. Set the date range you want
4. Click **Export to File** (top right)
5. Save as CSV
6. Upload in the dashboard sidebar → "Upload TOS CSV"

---

## Deploy to Streamlit Cloud (Free, Online Access)

1. Push this folder to a **GitHub repo** (public or private)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app**
4. Select your repo, branch, and set `app.py` as the main file
5. Click **Deploy** — your dashboard will be live at a public URL in ~2 minutes

### Streamlit Cloud tips
- Free tier: unlimited public apps, 1GB RAM
- Auto-redeploys when you push to GitHub
- Add `secrets.toml` for any API keys (not needed for this app)

---

## Adding New Trades

**Option A (Manual):** Export a fresh CSV from TOS and re-upload.

**Option B (Cumulative):** Keep a master CSV and append new rows in the TOS format:
```
Date, Type, Description, Ref Num, Misc Fees, Commissions, Amount, Balance
13/5/26 23:20,TRD,SOLD -3 PLTR 100 (Weeklys) 12 JUN 26 150 CALL @2.05 CBOE,...
```

---

## Dashboard Features

| Tab | Contents |
|---|---|
| Cumulative P&L | Equity curve, daily bars, distribution histogram |
| By Ticker | Horizontal bar chart, premium share pie, CALL/PUT breakdown |
| Monthly View | Monthly bars, summary table, P&L heatmap (ticker × month) |
| Trade Log | Searchable/sortable full log with CSV export |

**KPI Strip:**
- Grand Total Net P&L
- Gross Premium Collected
- Total Commissions + Fees
- Win Rate
- Avg Net per Trade

---

## Filters (Sidebar)
- **Tickers** — multi-select
- **Date Range** — date picker
- **Option Type** — CALL / PUT / STOCK

All charts and KPIs update dynamically with filters applied.

---

## Tech Stack
- `streamlit` — UI framework
- `pandas` — data processing
- `plotly` — interactive charts
- `yfinance` — (available for future live price integration)
