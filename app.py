import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, date, timedelta
import io
import re

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Options P&L Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Theme & CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:        #0a0e1a;
    --surface:   #111827;
    --surface2:  #1a2235;
    --border:    #1e3a5f;
    --accent:    #00d4ff;
    --accent2:   #7c3aed;
    --green:     #10b981;
    --red:       #f43f5e;
    --yellow:    #fbbf24;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --font-mono: 'Space Mono', monospace;
    --font-main: 'Syne', sans-serif;
}

html, body, [class*="css"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-main) !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* Main header */
.dashboard-title {
    font-family: var(--font-main);
    font-weight: 800;
    font-size: 2.2rem;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
}
.dashboard-sub {
    font-family: var(--font-mono);
    font-size: 0.75rem;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}

/* KPI Cards */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
}
.kpi-label {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.kpi-value {
    font-family: var(--font-mono);
    font-size: 1.6rem;
    font-weight: 700;
    line-height: 1;
}
.kpi-delta {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    margin-top: 0.3rem;
}
.pos { color: var(--green); }
.neg { color: var(--red); }
.neu { color: var(--muted); }

/* Trend badge */
.trend-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
}
.trend-badge {
    display: inline-block;
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    font-family: var(--font-mono);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
}
.badge-bull  { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid #10b981; }
.badge-bear  { background: rgba(244,63,94,0.15);  color: #f43f5e; border: 1px solid #f43f5e; }
.badge-side  { background: rgba(251,191,36,0.15); color: #fbbf24; border: 1px solid #fbbf24; }

.strat-card {
    background: var(--surface);
    border-left: 3px solid var(--accent);
    border-radius: 0 8px 8px 0;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.6rem;
    font-family: var(--font-mono);
    font-size: 0.78rem;
}
.strat-title { color: var(--accent); font-weight: 700; margin-bottom: 0.3rem; font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase; }
.strat-desc  { color: var(--text); line-height: 1.5; }

.primary-strat {
    background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(124,58,237,0.08));
    border: 1px solid var(--accent);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
.primary-label {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.5rem;
}
.primary-name {
    font-family: var(--font-mono);
    font-size: 1rem;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 0.3rem;
}
.credit-badge { display:inline-block; padding:0.15rem 0.5rem; border-radius:4px; font-family:var(--font-mono); font-size:0.6rem; font-weight:700; letter-spacing:0.08em; background:rgba(16,185,129,0.15); color:#10b981; border:1px solid #10b981; margin-right:0.4rem; }
.debit-badge  { display:inline-block; padding:0.15rem 0.5rem; border-radius:4px; font-family:var(--font-mono); font-size:0.6rem; font-weight:700; letter-spacing:0.08em; background:rgba(251,191,36,0.15); color:#fbbf24; border:1px solid #fbbf24; margin-right:0.4rem; }
.iv-high  { color: #f43f5e; }
.iv-mod   { color: #fbbf24; }
.iv-low   { color: #10b981; }

/* Section labels */
.section-label {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--accent);
    margin: 1.5rem 0 0.6rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

/* Dataframe styling */
.stDataFrame { border-radius: 8px; overflow: hidden; }
[data-testid="stDataFrame"] { background: var(--surface) !important; }

/* File uploader */
[data-testid="stFileUploader"] {
    background: var(--surface2) !important;
    border: 1px dashed var(--border) !important;
    border-radius: 8px !important;
}

/* Selectbox, multiselect */
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: var(--surface) !important; border-radius: 8px; }
.stTabs [data-baseweb="tab"] { color: var(--muted) !important; font-family: var(--font-mono); font-size: 0.75rem; letter-spacing: 0.05em; }
.stTabs [aria-selected="true"] { color: var(--accent) !important; }

/* Metric override */
[data-testid="metric-container"] { background: var(--surface) !important; border-radius: 8px; padding: 0.8rem !important; border: 1px solid var(--border) !important; }

div[data-testid="stMetricValue"] { font-family: var(--font-mono) !important; }
div[data-testid="stMetricLabel"] { font-family: var(--font-mono) !important; font-size: 0.65rem !important; text-transform: uppercase; letter-spacing: 0.08em; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Space Mono, monospace", color="#e2e8f0", size=11),
    xaxis=dict(gridcolor="#1e3a5f", linecolor="#1e3a5f", zerolinecolor="#1e3a5f"),
    yaxis=dict(gridcolor="#1e3a5f", linecolor="#1e3a5f", zerolinecolor="#1e3a5f"),
    margin=dict(l=40, r=20, t=40, b=40),
    colorway=["#00d4ff","#7c3aed","#10b981","#fbbf24","#f43f5e","#06b6d4","#8b5cf6","#34d399"],
)

# ── Helpers ────────────────────────────────────────────────────────────────
def parse_amount(val):
    if pd.isna(val): return 0.0
    s = str(val).replace('"','').replace(' ','')
    if s.startswith('(') and s.endswith(')'):
        return -float(s[1:-1].replace('$','').replace(',',''))
    return float(s.replace('$','').replace(',',''))

def extract_ticker(desc):
    tokens = str(desc).split()
    skip = {"SOLD","BOT","BOT+","SOLD-","Removed","due","to","Assignment","Expiration","Qualified","Dividend","-"}
    for t in tokens:
        t_clean = re.sub(r'[^A-Z]','', t.upper())
        if len(t_clean) >= 2 and len(t_clean) <= 5 and t_clean not in skip and t_clean.isalpha():
            return t_clean
    return "OTHER"

def extract_option_type(desc):
    d = str(desc).upper()
    if " CALL" in d: return "CALL"
    if " PUT" in d: return "PUT"
    return "STOCK"

def extract_action(desc):
    d = str(desc).upper()
    if d.startswith("SOLD") or "SOLD -" in d: return "SELL"
    if d.startswith("BOT") or "BOT +" in d: return "BUY"
    return "OTHER"

def load_sample_data():
    """Built-in sample data matching the uploaded TOS history."""
    rows = [
        ("2026-05-13","TRD","SOLD -3 PLTR 100 (Weeklys) 12 JUN 26 150 CALL @2.05 CBOE",615.00,-1.95,-0.06),
        ("2026-05-13","TRD","SOLD -1 PLTR 100 (Weeklys) 12 JUN 26 150 CALL @2.05 CBOE",205.00,-0.65,-0.02),
        ("2026-05-13","TRD","SOLD -1 PLTR 100 (Weeklys) 12 JUN 26 150 CALL @2.05 CBOE",205.00,-0.65,-0.02),
        ("2026-05-13","TRD","SOLD -3 PLTR 100 (Weeklys) 12 JUN 26 150 CALL @2.05 CBOE",615.00,-1.95,-0.06),
        ("2026-05-13","TRD","BOT +6 PLTR 100 (Weeklys) 5 JUN 26 152.5 CALL @1.26 CBOE",-756.00,-3.90,-0.07),
        ("2026-05-11","TRD","BOT +5 IONQ 100 (Weeklys) 5 JUN 26 33 PUT @.49 CBOE",-245.00,-3.25,-0.06),
        ("2026-05-11","TRD","SOLD -3 PLTR 100 (Weeklys) 12 JUN 26 122 PUT @3.30 CBOE",990.00,-1.95,-0.07),
        ("2026-05-11","TRD","SOLD -2 AMD 100 (Weeklys) 12 JUN 26 435 PUT @25.00 CBOE",5000.00,-1.30,-0.13),
        ("2026-04-28","TRD","SOLD -5 IONQ 100 (Weeklys) 5 JUN 26 33 PUT @1.27 CBOE",635.00,-3.25,-0.09),
        ("2026-04-27","TRD","SOLD -1 FTNT 100 (Weeklys) 29 MAY 26 90 CALL @3.51 CBOE",351.00,-0.65,-0.02),
        ("2026-04-27","TRD","SOLD -1 FTNT 100 (Weeklys) 29 MAY 26 90 CALL @3.51 CBOE",351.00,-0.65,-0.02),
        ("2026-04-27","TRD","SOLD -3 PLTR 100 (Weeklys) 5 JUN 26 152.5 CALL @6.95 CBOE",2085.00,-1.95,-0.09),
        ("2026-04-27","TRD","SOLD -2 PLTR 100 (Weeklys) 5 JUN 26 152.5 CALL @6.95 CBOE",1390.00,-1.30,-0.07),
        ("2026-04-27","TRD","SOLD -1 PLTR 100 (Weeklys) 5 JUN 26 152.5 CALL @6.95 CBOE",695.00,-0.65,-0.02),
        ("2026-04-27","TRD","BOT +8 SOFI 100 (Weeklys) 1 MAY 26 15 PUT @.06 CBOE",-48.00,-5.20,-0.10),
        ("2026-04-07","TRD","SOLD -8 SOFI 100 (Weeklys) 1 MAY 26 15 PUT @.66 CBOE",528.00,-5.20,-0.14),
        ("2026-03-31","TRD","SOLD -30 SOFI 100 18 SEP 26 20 CALL @1.46 BATS",4380.00,-19.50,-0.46),
        ("2026-03-31","TRD","SOLD -3 UNH 100 17 JUL 26 350 CALL @2.65",795.00,-1.95,-0.05),
        ("2026-03-31","TRD","SOLD -3 AVGO 100 (Weeklys) 8 MAY 26 325 CALL @9.50 CBOE",2850.00,-1.95,-0.05),
        ("2026-03-31","TRD","BOT +3 UNH 100 17 APR 26 350 CALL @.11 CBOE",-33.00,-1.95,-0.04),
        ("2026-03-31","TRD","BOT +3 AVGO 100 (Weeklys) 10 APR 26 350 CALL @.31 CBOE",-93.00,-1.95,-0.04),
        ("2026-03-31","TRD","BOT +1 SOFI 100 17 APR 26 26 CALL @.02 CBOE",-2.00,0.00,-0.01),
        ("2026-03-31","TRD","BOT +29 SOFI 100 17 APR 26 26 CALL @.03 CBOE",-87.00,0.00,-0.35),
        ("2026-03-09","TRD","SOLD -6 PLTR 100 (Weeklys) 10 APR 26 145 PUT @6.00",3600.00,-3.90,-0.09),
        ("2026-03-09","TRD","SOLD -8 OKLO 100 21 AUG 26 100 CALL @4.85 CBOE",3880.00,-5.20,-0.13),
        ("2026-03-09","TRD","BOT +8 OKLO 100 18 JUN 26 150 CALL @.70 CBOE",-560.00,-5.20,-0.10),
        ("2026-03-09","TRD","SOLD -1 AVGO 100 (Weeklys) 10 APR 26 350 CALL @11.55 CBOE",1155.00,-0.65,-0.02),
        ("2026-03-09","TRD","SOLD -1 AVGO 100 (Weeklys) 10 APR 26 350 CALL @11.55 CBOE",1155.00,-0.65,-0.02),
        ("2026-03-09","TRD","SOLD -1 AVGO 100 (Weeklys) 10 APR 26 350 CALL @11.00 CBOE",1100.00,-0.65,-0.01),
        ("2026-02-19","TRD","SOLD -6 PLTR 100 17 APR 26 160 CALL @3.15 CBOE",1890.00,-3.90,-0.09),
        ("2026-02-19","TRD","BOT +2 PLTR 100 (Weeklys) 27 FEB 26 180 CALL @.03 CBOE",-6.00,0.00,-0.03),
        ("2026-02-19","TRD","BOT +2 PLTR 100 (Weeklys) 27 FEB 26 180 CALL @.03 CBOE",-6.00,0.00,-0.02),
        ("2026-02-19","TRD","BOT +2 PLTR 100 (Weeklys) 27 FEB 26 180 CALL @.03 CBOE",-6.00,0.00,-0.02),
        ("2026-02-19","TRD","SOLD -3 UNH 100 17 APR 26 350 CALL @2.45 CBOE",735.00,-1.95,-0.04),
        ("2026-02-18","TRD","SOLD -1 SOFI 100 17 APR 26 26 CALL @.31 CBOE",31.00,-0.65,-0.01),
        ("2026-02-18","TRD","SOLD -8 SOFI 100 17 APR 26 26 CALL @.31 CBOE",248.00,-5.20,-0.12),
        ("2026-02-18","TRD","SOLD -9 SOFI 100 17 APR 26 26 CALL @.31 CBOE",279.00,-5.85,-0.13),
        ("2026-02-18","TRD","SOLD -12 SOFI 100 17 APR 26 26 CALL @.31 CBOE",372.00,-7.80,-0.17),
        ("2026-02-09","TRD","BOT +1 PG 100 15 JAN 27 170 CALL @7.55 CBOE",-755.00,-0.65,-0.01),
        ("2026-01-26","TRD","SOLD -1 SOFI 100 (Weeklys) 27 FEB 26 24 PUT @.97 CBOE",97.00,-0.65,-0.01),
        ("2026-01-26","TRD","SOLD -4 SOFI 100 (Weeklys) 27 FEB 26 24 PUT @.97 CBOE",388.00,-2.60,-0.07),
        ("2026-01-26","TRD","SOLD -3 SOFI 100 (Weeklys) 27 FEB 26 24 PUT @.97 CBOE",291.00,-1.95,-0.04),
        ("2026-01-26","TRD","SOLD -1 SOFI 100 (Weeklys) 27 FEB 26 24 PUT @.97 CBOE",97.00,-0.65,-0.01),
        ("2026-01-26","TRD","SOLD -1 MU 100 (Weeklys) 27 FEB 26 365 PUT @17.80 CBOE",1780.00,-0.65,-0.02),
        ("2026-01-26","TRD","SOLD -1 MU 100 (Weeklys) 27 FEB 26 365 PUT @17.80 CBOE",1780.00,-0.65,-0.01),
        ("2026-01-26","TRD","SOLD -7 U @44.00",308.00,0.00,0.00),
        ("2026-01-26","TRD","SOLD -3 AVGO 100 (Weeklys) 27 FEB 26 340 CALL @11.00 CBOE",3300.00,-1.95,-0.04),
        ("2026-01-26","TRD","SOLD -6 PLTR 100 (Weeklys) 27 FEB 26 180 CALL @7.60 CBOE",4560.00,-3.90,-0.09),
        ("2026-01-08","TRD","SOLD -14 SOFI 100 (Weeklys) 13 FEB 26 29 CALL @1.50 CBOE",2100.00,-9.10,-0.19),
        ("2026-01-07","TRD","SOLD -20 SOFI 100 (Weeklys) 13 FEB 26 30 CALL @1.07 CBOE",2140.00,-13.00,-0.28),
        ("2026-01-06","TRD","SOLD -1 UNH 100 (Weeklys) 13 FEB 26 370 CALL @9.08 CBOE",908.00,-0.65,-0.01),
        ("2026-01-06","TRD","SOLD -1 UNH 100 (Weeklys) 13 FEB 26 370 CALL @9.08 CBOE",908.00,-0.65,-0.02),
        ("2026-01-06","TRD","SOLD -1 UNH 100 (Weeklys) 13 FEB 26 370 CALL @9.05 CBOE",905.00,-0.65,-0.01),
        ("2026-01-06","TRD","SOLD -30 SOFI 100 (Weeklys) 13 FEB 26 26 PUT @1.00 CBOE",3000.00,-19.50,-0.41),
    ]
    df = pd.DataFrame(rows, columns=["Date","Type","Description","Amount","Commissions","MiscFees"])
    df["Date"] = pd.to_datetime(df["Date"])
    return df

def parse_tos_csv(uploaded_file):
    """Parse a TOS-exported CSV file."""
    try:
        content = uploaded_file.read().decode("utf-8", errors="replace")
        lines = content.splitlines()
        data_lines = []
        for line in lines:
            if line.strip() and not line.startswith("Date") and not line.startswith("//"):
                data_lines.append(line)

        header_line = None
        for line in lines:
            if line.strip().startswith("Date"):
                header_line = line
                break

        if header_line:
            from io import StringIO
            csv_text = header_line + "\n" + "\n".join(data_lines)
            df_raw = pd.read_csv(StringIO(csv_text))
        else:
            from io import StringIO
            df_raw = pd.read_csv(StringIO(content))

        # Normalise column names
        df_raw.columns = [c.strip() for c in df_raw.columns]
        col_map = {}
        for c in df_raw.columns:
            cl = c.lower()
            if "date" in cl: col_map[c] = "Date"
            elif "type" in cl: col_map[c] = "Type"
            elif "descr" in cl: col_map[c] = "Description"
            elif "amount" in cl and "net" not in cl: col_map[c] = "Amount"
            elif "commission" in cl: col_map[c] = "Commissions"
            elif "misc" in cl or "fee" in cl: col_map[c] = "MiscFees"
        df_raw.rename(columns=col_map, inplace=True)

        for col in ["Amount","Commissions","MiscFees"]:
            if col not in df_raw.columns:
                df_raw[col] = 0.0
            else:
                df_raw[col] = df_raw[col].apply(parse_amount)

        df_raw["Date"] = pd.to_datetime(df_raw["Date"], dayfirst=True, errors="coerce")
        df_raw = df_raw[df_raw["Type"] == "TRD"].dropna(subset=["Date"])
        return df_raw[["Date","Type","Description","Amount","Commissions","MiscFees"]]
    except Exception as e:
        st.error(f"Parse error: {e}")
        return None

def enrich(df):
    df = df.copy()
    df["Ticker"]      = df["Description"].apply(extract_ticker)
    df["OptionType"]  = df["Description"].apply(extract_option_type)
    df["Action"]      = df["Description"].apply(extract_action)
    df["NetAmount"]   = df["Amount"] + df["Commissions"] + df["MiscFees"]
    df["YearMonth"]   = df["Date"].dt.to_period("M").astype(str)
    df["Week"]        = df["Date"].dt.to_period("W").astype(str)
    df = df.sort_values("Date")
    df["CumPnL"]      = df["NetAmount"].cumsum()
    return df

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p style="font-family:\'Space Mono\',monospace;font-size:0.65rem;letter-spacing:0.15em;color:#00d4ff;text-transform:uppercase;margin-bottom:1rem;">⬡ IBOT TRADING SYSTEM</p>', unsafe_allow_html=True)
    st.markdown("### Data Source")

    data_source = st.radio("", ["Use Sample Data", "Upload TOS CSV"], label_visibility="collapsed")

    df_raw = None
    if data_source == "Upload TOS CSV":
        uploaded = st.file_uploader("Upload TOS transaction CSV", type=["csv","txt"], label_visibility="collapsed")
        if uploaded:
            df_raw = parse_tos_csv(uploaded)
            if df_raw is not None:
                st.success(f"✓ {len(df_raw)} trades loaded")
        else:
            st.info("Export from TOS: Account → History & Statements → Export CSV")
    else:
        df_raw = load_sample_data()
        st.info("Showing built-in transaction data. Upload your TOS CSV to use live data.")

    if df_raw is not None:
        df = enrich(df_raw)
        st.markdown("---")
        st.markdown("### Filters")

        all_tickers = sorted(df["Ticker"].unique())
        sel_tickers = st.multiselect("Tickers", all_tickers, default=all_tickers)

        min_date = df["Date"].min().date()
        max_date = df["Date"].max().date()
        date_range = st.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

        sel_type = st.multiselect("Option Type", ["CALL","PUT","STOCK"], default=["CALL","PUT","STOCK"])

        if len(date_range) == 2:
            df = df[
                (df["Ticker"].isin(sel_tickers)) &
                (df["Date"].dt.date >= date_range[0]) &
                (df["Date"].dt.date <= date_range[1]) &
                (df["OptionType"].isin(sel_type))
            ]
            df["CumPnL"] = df["NetAmount"].cumsum()

        st.markdown("---")

    st.markdown('<p style="font-family:\'Space Mono\',monospace;font-size:0.6rem;color:#64748b;">IBOT Options Dashboard v1.1<br>Thinkorswim · IBKR Compatible</p>', unsafe_allow_html=True)

# ── Main header ────────────────────────────────────────────────────────────
st.markdown('<h1 class="dashboard-title">OPTIONS P&L DASHBOARD</h1>', unsafe_allow_html=True)

has_data = df_raw is not None

if has_data:
    st.markdown(f'<p class="dashboard-sub">IBOT TRADING SYSTEM · {len(df)} TRADES · LAST UPDATED {df["Date"].max().strftime("%d %b %Y").upper()}</p>', unsafe_allow_html=True)
else:
    st.markdown('<p class="dashboard-sub">IBOT Trading System · Thinkorswim Integration</p>', unsafe_allow_html=True)

# ── KPI Row (only when data loaded) ───────────────────────────────────────
if has_data:
    total_net    = df["NetAmount"].sum()
    total_gross  = df[df["Amount"] > 0]["Amount"].sum()
    total_costs  = (df["Commissions"].sum() + df["MiscFees"].sum())
    win_trades   = (df["NetAmount"] > 0).sum()
    total_trades = len(df)
    win_rate     = win_trades / total_trades * 100 if total_trades > 0 else 0
    avg_per_trade = df["NetAmount"].mean()
    sell_trades  = df[df["Action"] == "SELL"]
    premium_collected = sell_trades["Amount"].sum()

    k1, k2, k3, k4, k5 = st.columns(5)

    def kpi(col, label, value, fmt="$"):
        color = "pos" if value >= 0 else "neg"
        if fmt == "$":
            val_str = f"${value:,.0f}"
        elif fmt == "%":
            val_str = f"{value:.1f}%"
        else:
            val_str = f"{value:.0f}"
        col.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value {color}">{val_str}</div>
        </div>""", unsafe_allow_html=True)

    with k1: kpi(k1, "NET P&L (incl. wire)", total_net + 10000, "$")
    with k2: kpi(k2, "GROSS PREMIUM COLLECTED", premium_collected, "$")
    with k3: kpi(k3, "TOTAL COMMISSIONS + FEES", total_costs, "$")
    with k4: kpi(k4, "WIN RATE", win_rate, "%")
    with k5: kpi(k5, "AVG NET / TRADE", avg_per_trade, "$")

    st.markdown("")

# ── Tabs ───────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈  CUMULATIVE P&L",
    "🎯  BY TICKER",
    "📅  MONTHLY VIEW",
    "📋  TRADE LOG",
    "🌐  LIVE MARKET",
])

# ── Tab 1: Cumulative P&L ──────────────────────────────────────────────────
with tab1:
    if not has_data:
        st.info("👈 Select a data source in the sidebar to view P&L analytics.")
    else:
        col_a, col_b = st.columns([2, 1])

        with col_a:
            st.markdown('<p class="section-label">Cumulative Net P&L Over Time</p>', unsafe_allow_html=True)
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df["Date"], y=df["CumPnL"],
                fill="tozeroy",
                fillcolor="rgba(0,212,255,0.07)",
                line=dict(color="#00d4ff", width=2),
                name="Cumulative P&L",
                hovertemplate="<b>%{x|%d %b %Y}</b><br>Cumulative P&L: $%{y:,.0f}<extra></extra>"
            ))

            fig.add_hline(y=0, line_color="#64748b", line_dash="dot", line_width=1)

            final_val = df["CumPnL"].iloc[-1]
            fig.add_annotation(
                x=df["Date"].iloc[-1], y=final_val,
                text=f" ${final_val:,.0f}",
                showarrow=False, font=dict(color="#00d4ff", size=12, family="Space Mono"),
                xanchor="left"
            )

            fig.update_layout(**PLOTLY_THEME, height=320, showlegend=False,
                              title=dict(text="", font=dict(size=12)))
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown('<p class="section-label">P&L Distribution</p>', unsafe_allow_html=True)
            fig2 = go.Figure(go.Histogram(
                x=df["NetAmount"],
                nbinsx=20,
                marker_color="#7c3aed",
                marker_line_color="#0a0e1a",
                marker_line_width=1,
            ))
            fig2.update_layout(**PLOTLY_THEME, height=320,
                               xaxis_title="Net Amount ($)", yaxis_title="Trades")
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<p class="section-label">Daily P&L</p>', unsafe_allow_html=True)
        daily = df.groupby("Date")["NetAmount"].sum().reset_index()
        colors = ["#10b981" if v >= 0 else "#f43f5e" for v in daily["NetAmount"]]
        fig3 = go.Figure(go.Bar(
            x=daily["Date"], y=daily["NetAmount"],
            marker_color=colors,
            hovertemplate="<b>%{x|%d %b %Y}</b><br>P&L: $%{y:,.0f}<extra></extra>"
        ))
        fig3.update_layout(**PLOTLY_THEME, height=220, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

# ── Tab 2: By Ticker ────────────────────────────────────────────────────────
with tab2:
    if not has_data:
        st.info("👈 Select a data source in the sidebar to view ticker analytics.")
    else:
        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown('<p class="section-label">Net P&L by Ticker</p>', unsafe_allow_html=True)
            by_ticker = df.groupby("Ticker")["NetAmount"].sum().sort_values(ascending=True).reset_index()
            colors = ["#10b981" if v >= 0 else "#f43f5e" for v in by_ticker["NetAmount"]]
            fig = go.Figure(go.Bar(
                x=by_ticker["NetAmount"], y=by_ticker["Ticker"],
                orientation="h",
                marker_color=colors,
                text=[f"${v:,.0f}" for v in by_ticker["NetAmount"]],
                textposition="outside",
                textfont=dict(family="Space Mono", size=10),
                hovertemplate="<b>%{y}</b><br>Net P&L: $%{x:,.0f}<extra></extra>"
            ))
            fig.update_layout(**PLOTLY_THEME, height=380, showlegend=False,
                              xaxis_title="Net P&L ($)")
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown('<p class="section-label">Premium Share by Ticker</p>', unsafe_allow_html=True)
            sell_by_ticker = df[df["Action"]=="SELL"].groupby("Ticker")["Amount"].sum().reset_index()
            sell_by_ticker = sell_by_ticker[sell_by_ticker["Amount"] > 0]
            fig2 = go.Figure(go.Pie(
                labels=sell_by_ticker["Ticker"],
                values=sell_by_ticker["Amount"],
                hole=0.55,
                textfont=dict(family="Space Mono", size=10),
                marker=dict(line=dict(color="#0a0e1a", width=2)),
            ))
            fig2.update_layout(**PLOTLY_THEME, height=380,
                               legend=dict(orientation="v", x=1.02, y=0.5))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<p class="section-label">CALL vs PUT vs STOCK — Net P&L</p>', unsafe_allow_html=True)
        type_ticker = df.groupby(["Ticker","OptionType"])["NetAmount"].sum().reset_index()
        fig3 = px.bar(type_ticker, x="Ticker", y="NetAmount", color="OptionType",
                      barmode="group",
                      color_discrete_map={"CALL":"#00d4ff","PUT":"#7c3aed","STOCK":"#fbbf24"})
        fig3.update_layout(**PLOTLY_THEME, height=260,
                           yaxis_title="Net P&L ($)", xaxis_title="")
        st.plotly_chart(fig3, use_container_width=True)

# ── Tab 3: Monthly View ─────────────────────────────────────────────────────
with tab3:
    if not has_data:
        st.info("👈 Select a data source in the sidebar to view monthly analytics.")
    else:
        col_a, col_b = st.columns([3, 2])

        with col_a:
            st.markdown('<p class="section-label">Monthly Net P&L</p>', unsafe_allow_html=True)
            monthly = df.groupby("YearMonth")["NetAmount"].sum().reset_index().sort_values("YearMonth")
            colors = ["#10b981" if v >= 0 else "#f43f5e" for v in monthly["NetAmount"]]
            fig = go.Figure(go.Bar(
                x=monthly["YearMonth"], y=monthly["NetAmount"],
                marker_color=colors,
                text=[f"${v:,.0f}" for v in monthly["NetAmount"]],
                textposition="outside",
                textfont=dict(family="Space Mono", size=9),
            ))
            fig.update_layout(**PLOTLY_THEME, height=320, showlegend=False,
                              xaxis_title="Month", yaxis_title="Net P&L ($)")
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown('<p class="section-label">Monthly Summary Table</p>', unsafe_allow_html=True)
            m_table = df.groupby("YearMonth").agg(
                Trades=("NetAmount","count"),
                Gross=("Amount","sum"),
                Net=("NetAmount","sum"),
                WinRate=("NetAmount", lambda x: f"{(x>0).sum()/len(x)*100:.0f}%")
            ).reset_index().sort_values("YearMonth", ascending=False)
            m_table["Net"] = m_table["Net"].apply(lambda x: f"${x:,.0f}")
            m_table["Gross"] = m_table["Gross"].apply(lambda x: f"${x:,.0f}")
            m_table.columns = ["Month","Trades","Gross","Net P&L","Win %"]
            st.dataframe(m_table, use_container_width=True, hide_index=True, height=300)

        st.markdown('<p class="section-label">P&L Heatmap — Ticker × Month</p>', unsafe_allow_html=True)
        pivot = df.pivot_table(index="Ticker", columns="YearMonth", values="NetAmount", aggfunc="sum", fill_value=0)
        fig4 = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0,"#f43f5e"],[0.5,"#1a2235"],[1,"#10b981"]],
            zmid=0,
            text=[[f"${v:,.0f}" for v in row] for row in pivot.values],
            texttemplate="%{text}",
            textfont=dict(family="Space Mono", size=9),
            hovertemplate="<b>%{y}</b> · %{x}<br>P&L: $%{z:,.0f}<extra></extra>",
            colorbar=dict(tickfont=dict(family="Space Mono", size=9)),
        ))
        fig4.update_layout(**PLOTLY_THEME, height=300)
        st.plotly_chart(fig4, use_container_width=True)

# ── Tab 4: Trade Log ────────────────────────────────────────────────────────
with tab4:
    if not has_data:
        st.info("👈 Select a data source in the sidebar to view the trade log.")
    else:
        st.markdown('<p class="section-label">Full Trade Log</p>', unsafe_allow_html=True)

        col_s, col_t, _ = st.columns([2, 2, 4])
        with col_s:
            search = st.text_input("Search description", placeholder="e.g. PLTR CALL", label_visibility="collapsed")
        with col_t:
            sort_col = st.selectbox("Sort by", ["Date","NetAmount","Ticker"], label_visibility="collapsed")

        log = df.copy()
        if search:
            log = log[log["Description"].str.contains(search, case=False, na=False)]
        log = log.sort_values(sort_col, ascending=(sort_col=="Date"))

        display = log[["Date","Ticker","OptionType","Action","Description","Amount","Commissions","MiscFees","NetAmount","CumPnL"]].copy()
        display["Date"] = display["Date"].dt.strftime("%d %b %Y")
        display.columns = ["Date","Ticker","Type","Action","Description","Gross ($)","Comm ($)","Misc ($)","Net ($)","Cum P&L ($)"]

        st.dataframe(
            display,
            use_container_width=True,
            height=480,
            hide_index=True,
            column_config={
                "Net ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Gross ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Comm ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Misc ($)": st.column_config.NumberColumn(format="$%.2f"),
                "Cum P&L ($)": st.column_config.NumberColumn(format="$%.2f"),
            }
        )

        csv_out = display.to_csv(index=False)
        st.download_button(
            "⬇ Export Filtered Trades CSV",
            data=csv_out,
            file_name=f"trades_export_{date.today()}.csv",
            mime="text/csv",
        )

# ── Tab 5: Live Market Analysis ─────────────────────────────────────────────
with tab5:
    st.markdown('<p class="section-label">Live Trend Analysis & Vertical Spread Selector</p>', unsafe_allow_html=True)

    # ── Preset quick-select buttons ────────────────────────────────────────
    PRESETS = {
        "Broad Market": ["SPY", "QQQ", "IWM", "TLT"],
        "Sectors":      ["XLF", "XLE", "SMH", "XLK"],
        "Mega-Cap":     ["AAPL", "MSFT", "NVDA", "TSLA"],
        "High-Beta":    ["PLTR", "AMD", "SOFI", "IONQ"],
    }

    st.markdown("**Quick Select:**")
    preset_cols = st.columns(len(PRESETS))
    selected_preset_ticker = None
    for i, (group, tickers) in enumerate(PRESETS.items()):
        with preset_cols[i]:
            st.markdown(f'<p style="font-family:\'Space Mono\',monospace;font-size:0.6rem;color:#64748b;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:4px;">{group}</p>', unsafe_allow_html=True)
            for t in tickers:
                if st.button(t, key=f"preset_{t}", use_container_width=True):
                    selected_preset_ticker = t

    st.markdown("")

    # ── Ticker input + lookback ────────────────────────────────────────────
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 4])
    with ctrl_col1:
        default_ticker = selected_preset_ticker if selected_preset_ticker else "SPY"
        live_ticker = st.text_input(
            "Ticker Symbol",
            value=st.session_state.get("live_ticker_input", default_ticker),
            key="live_ticker_input",
            placeholder="e.g. SPY",
        ).upper().strip()
    with ctrl_col2:
        lookback_days = st.slider("History (days)", min_value=120, max_value=500, value=365, step=30)

    if selected_preset_ticker:
        live_ticker = selected_preset_ticker

    if not live_ticker:
        st.info("Enter a ticker symbol above to begin live market analysis.")
        st.stop()

    # ── Fetch live data ────────────────────────────────────────────────────
    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_market_data(ticker: str, days: int):
        end = datetime.today()
        start = end - timedelta(days=days)
        raw = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        info = {}
        try:
            info = yf.Ticker(ticker).info
        except Exception:
            pass
        return raw, info

    @st.cache_data(ttl=300, show_spinner=False)
    def fetch_atm_iv(ticker: str, latest_px: float):
        """Pull ATM implied volatility from the nearest options expiry (≥7 days out)."""
        try:
            tk = yf.Ticker(ticker)
            exps = tk.options
            if not exps:
                return None
            today = datetime.today().date()
            valid = [e for e in exps
                     if (datetime.strptime(e, "%Y-%m-%d").date() - today).days >= 7]
            if not valid:
                return None
            chain = tk.option_chain(valid[0])
            ivs = []
            for side in (chain.calls, chain.puts):
                if side.empty:
                    continue
                idx = (side["strike"] - latest_px).abs().idxmin()
                v = side.loc[idx, "impliedVolatility"]
                if pd.notna(v) and float(v) > 0:
                    ivs.append(float(v) * 100)
            return round(sum(ivs) / len(ivs), 2) if ivs else None
        except Exception:
            return None

    with st.spinner(f"Fetching live data for {live_ticker}..."):
        try:
            mkt_data, ticker_info = fetch_market_data(live_ticker, lookback_days)
        except Exception as e:
            st.error(f"Failed to fetch data: {e}")
            st.stop()

    if mkt_data.empty:
        st.error(f"No data returned for **{live_ticker}**. Check the ticker symbol and try again.")
        st.stop()

    # Need at least 200 rows for SMA200
    if len(mkt_data) < 50:
        st.warning(f"Only {len(mkt_data)} trading days available — extend the history range for reliable signals.")

    # ── Calculate indicators ───────────────────────────────────────────────
    mkt_data = mkt_data.copy()
    mkt_data["SMA50"]  = mkt_data["Close"].rolling(window=50).mean()
    mkt_data["SMA200"] = mkt_data["Close"].rolling(window=200).mean()

    latest       = mkt_data["Close"].iloc[-1]
    prev         = mkt_data["Close"].iloc[-2]
    chg          = float(latest) - float(prev)
    pct_chg      = chg / float(prev) * 100
    sma50_val    = mkt_data["SMA50"].dropna().iloc[-1]  if not mkt_data["SMA50"].dropna().empty  else None
    sma200_val   = mkt_data["SMA200"].dropna().iloc[-1] if not mkt_data["SMA200"].dropna().empty else None
    latest_price = float(latest)

    # ── IV / HV computation ────────────────────────────────────────────────
    _close  = mkt_data["Close"].squeeze()
    _ret    = _close.pct_change().dropna()
    _hv_ser = (_ret.rolling(30).std() * np.sqrt(252) * 100).dropna()

    hv30     = float(_hv_ser.iloc[-1]) if not _hv_ser.empty else None
    hv_rank  = None
    hv_pct   = None
    if len(_hv_ser) > 1:
        _lo, _hi = _hv_ser.min(), _hv_ser.max()
        hv_rank = float((_hv_ser.iloc[-1] - _lo) / (_hi - _lo) * 100) if _hi != _lo else 50.0
        hv_pct  = float((_hv_ser < _hv_ser.iloc[-1]).mean() * 100)

    with st.spinner("Fetching IV from options chain…"):
        atm_iv = fetch_atm_iv(live_ticker, latest_price)

    # IV environment: use hv_rank as the rank signal (free-data proxy for IV Rank)
    if hv_rank is not None:
        if hv_rank >= 50:
            iv_env, iv_css = "HIGH",     "iv-high"
        elif hv_rank >= 25:
            iv_env, iv_css = "MODERATE", "iv-mod"
        else:
            iv_env, iv_css = "LOW",      "iv-low"
    else:
        iv_env, iv_css = "UNKNOWN", "neu"

    iv_hv_ratio = round(atm_iv / hv30, 2) if (atm_iv and hv30 and hv30 > 0) else None

    # ── Trend detection ────────────────────────────────────────────────────
    if sma50_val is not None and sma200_val is not None:
        s50 = float(sma50_val)
        s200 = float(sma200_val)
        if latest_price > s50 and s50 > s200:
            trend_key = "BULL"
            trend_label = "BULL MARKET — Uptrend"
            badge_class = "badge-bull"
            trend_color = "#10b981"
        elif latest_price < s50 and s50 < s200:
            trend_key = "BEAR"
            trend_label = "BEAR MARKET — Downtrend"
            badge_class = "badge-bear"
            trend_color = "#f43f5e"
        else:
            trend_key = "SIDE"
            trend_label = "SIDEWAYS — Consolidation"
            badge_class = "badge-side"
            trend_color = "#fbbf24"
    else:
        trend_key = "SIDE"
        trend_label = "INSUFFICIENT DATA"
        badge_class = "badge-side"
        trend_color = "#fbbf24"
        s50 = s200 = None

    # Combined trend + IV → primary strategy recommendation
    PRIMARY_REC = {
        ("BULL", "HIGH"):     ("Bull Put Spread",  "CREDIT", "Sell OTM Put / Buy lower Put. Collect inflated premium while trend provides a floor. IV will mean-revert, accelerating decay on the short leg."),
        ("BULL", "MODERATE"): ("Bull Put Spread",  "CREDIT", "Sell OTM Put / Buy lower Put. Balanced credit harvest with uptrend as a directional buffer. Solid risk/reward in a rising market."),
        ("BULL", "LOW"):      ("Bull Call Spread",  "DEBIT",  "Buy near-ATM Call / Sell higher Call. Debit is cheap when IV is compressed — ideal for capturing a continued upside move at low cost."),
        ("BEAR", "HIGH"):     ("Bear Call Spread",  "CREDIT", "Sell OTM Call / Buy higher Call. Harvest panicked call premium while the downtrend limits upside risk on your short leg."),
        ("BEAR", "MODERATE"): ("Bear Call Spread",  "CREDIT", "Sell OTM Call / Buy higher Call. Credit spread with downtrend tailwind — keep short strike well above key resistance."),
        ("BEAR", "LOW"):      ("Bear Put Spread",   "DEBIT",  "Buy near-ATM Put / Sell lower Put. Debit is affordable in a suppressed-IV environment — ideal for a swift, clean down-move."),
        ("SIDE", "HIGH"):     ("Iron Condor",       "CREDIT", "Sell OTM Put spread + OTM Call spread simultaneously. Elevated IV inflates both wings — collect maximum double premium while price stays inside the range."),
        ("SIDE", "MODERATE"): ("Iron Condor",       "CREDIT", "Sell OTM Put spread + OTM Call spread. Double premium on a consolidating asset — keep strikes outside the recent swing highs/lows."),
        ("SIDE", "LOW"):      ("Iron Condor",       "CREDIT", "Iron Condor viable but premiums are thin. Widen strikes to collect adequate credit, or wait for an IV expansion before entering."),
        ("BULL", "UNKNOWN"):  ("Bull Put Spread",   "CREDIT", "Uptrend detected — a Bull Put Spread is the default credit spread for bullish conditions."),
        ("BEAR", "UNKNOWN"):  ("Bear Call Spread",  "CREDIT", "Downtrend detected — a Bear Call Spread is the default credit spread for bearish conditions."),
        ("SIDE", "UNKNOWN"):  ("Iron Condor",       "CREDIT", "Consolidation detected — Iron Condor is the default double credit spread for sideways markets."),
    }
    primary_name, primary_type, primary_desc = PRIMARY_REC.get(
        (trend_key, iv_env), PRIMARY_REC[(trend_key, "UNKNOWN")]
    )

    # Secondary strategies listed for context
    STRATEGIES = {
        "BULL": [
            {"title": "Bull Call Spread (Debit) — when IV is LOW",
             "desc": "Buy a near-ATM Call, sell a higher-strike Call to cap cost. Profits from continued upward move at reduced premium outlay."},
            {"title": "Bull Put Spread (Credit) — when IV is HIGH",
             "desc": "Sell an OTM Put below current price, buy a further OTM Put as a hedge. Collect premium upfront during IV spikes on pullbacks."},
        ],
        "BEAR": [
            {"title": "Bear Call Spread (Credit) — when IV is HIGH",
             "desc": "Sell an OTM Call above current price, buy a further OTM Call as a cap. Best during panic-driven IV spikes."},
            {"title": "Bear Put Spread (Debit) — when IV is LOW",
             "desc": "Buy a near-ATM Put, sell a lower-strike Put to reduce cost. More efficient than a naked long put in stable environments."},
        ],
        "SIDE": [
            {"title": "Iron Condor (Double Credit) — ideal on index ETFs",
             "desc": "Bull Put spread below + Bear Call spread above simultaneously. Profit fully as long as price stays inside the channel."},
            {"title": "Single-side OTM Credit Spread — tighter margin",
             "desc": "Sell one spread far above or below the range. Lower margin requirement; use when you have a mild directional lean."},
        ],
    }

    # ── Metric strip ──────────────────────────────────────────────────────
    asset_name = ticker_info.get("shortName", live_ticker) if ticker_info else live_ticker
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Asset", asset_name)
    m2.metric("Last Close", f"${latest_price:,.2f}", f"{chg:+.2f} ({pct_chg:+.2f}%)")
    m3.metric("50-Day SMA", f"${s50:,.2f}" if s50 else "N/A",
              f"{((latest_price/s50)-1)*100:+.1f}% vs price" if s50 else "")
    m4.metric("200-Day SMA", f"${s200:,.2f}" if s200 else "N/A",
              f"{((latest_price/s200)-1)*100:+.1f}% vs price" if s200 else "")

    st.markdown("")

    iv1, iv2, iv3, iv4 = st.columns(4)
    iv1.metric(
        "ATM Implied Vol",
        f"{atm_iv:.1f}%" if atm_iv else "N/A",
        "from options chain" if atm_iv else "options chain unavailable",
    )
    iv2.metric(
        "HV30 (Realized)",
        f"{hv30:.1f}%" if hv30 else "N/A",
        f"IV/HV = {iv_hv_ratio:.2f}" if iv_hv_ratio else "",
    )
    iv3.metric(
        "IV Rank (HV proxy)",
        f"{hv_rank:.0f} / 100" if hv_rank is not None else "N/A",
        iv_env,
    )
    iv4.metric(
        "IV Percentile",
        f"{hv_pct:.0f}th pct" if hv_pct is not None else "N/A",
        f"over {len(_hv_ser)} sessions",
    )

    st.markdown("")

    # ── Trend + strategy panel ─────────────────────────────────────────────
    panel_col, gauge_col, chart_col = st.columns([2, 1, 3])

    with panel_col:
        badge_type = "credit-badge" if primary_type == "CREDIT" else "debit-badge"
        st.markdown(f"""
        <div class="trend-card">
            <div style="display:flex;gap:0.5rem;margin-bottom:0.8rem;flex-wrap:wrap;">
                <div class="trend-badge {badge_class}">{trend_label}</div>
                <div class="trend-badge badge-{'bear' if iv_env=='HIGH' else ('side' if iv_env=='MODERATE' else 'bull')}">IV {iv_env}</div>
            </div>
            <div class="primary-strat">
                <div class="primary-label">Primary Recommendation</div>
                <div class="primary-name">{primary_name}</div>
                <span class="{badge_type}">{primary_type}</span>
                <p style="font-family:\'Space Mono\',monospace;font-size:0.72rem;color:#94a3b8;margin-top:0.5rem;line-height:1.5;">{primary_desc}</p>
            </div>
            <p style="font-family:\'Space Mono\',monospace;font-size:0.6rem;color:#64748b;margin-bottom:0.5rem;letter-spacing:0.1em;text-transform:uppercase;">Alternative Structures</p>
        """, unsafe_allow_html=True)

        for s in STRATEGIES[trend_key]:
            st.markdown(f"""
            <div class="strat-card">
                <div class="strat-title">{s['title']}</div>
                <div class="strat-desc">{s['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── IV Rank gauge ──────────────────────────────────────────────────────
    with gauge_col:
        st.markdown('<p class="section-label">IV Rank</p>', unsafe_allow_html=True)
        gauge_val = hv_rank if hv_rank is not None else 0
        gauge_color = "#f43f5e" if gauge_val >= 50 else ("#fbbf24" if gauge_val >= 25 else "#10b981")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=gauge_val,
            number={"suffix": "", "font": {"family": "Space Mono", "color": gauge_color, "size": 28}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#1e3a5f",
                         "tickfont": {"family": "Space Mono", "size": 9, "color": "#64748b"}},
                "bar": {"color": gauge_color, "thickness": 0.25},
                "bgcolor": "#111827",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,  25], "color": "rgba(16,185,129,0.12)"},
                    {"range": [25, 50], "color": "rgba(251,191,36,0.12)"},
                    {"range": [50, 100], "color": "rgba(244,63,94,0.12)"},
                ],
                "threshold": {"line": {"color": gauge_color, "width": 2},
                              "thickness": 0.75, "value": gauge_val},
            },
        ))
        fig_gauge.update_layout(
            **{k: v for k, v in PLOTLY_THEME.items() if k not in ("xaxis", "yaxis")},
            height=220,
            margin=dict(l=20, r=20, t=10, b=10),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

        iv_note = "SELL PREMIUM" if iv_env == "HIGH" else ("NEUTRAL" if iv_env == "MODERATE" else "BUY PREMIUM")
        st.markdown(f"""
        <p style="font-family:'Space Mono',monospace;font-size:0.65rem;text-align:center;
                  color:{gauge_color};letter-spacing:0.1em;text-transform:uppercase;margin-top:-0.5rem;">
            {iv_note}
        </p>
        <p style="font-family:'Space Mono',monospace;font-size:0.58rem;text-align:center;
                  color:#64748b;margin-top:0.2rem;">
            {'ATM IV ' + str(atm_iv) + '% · ' if atm_iv else ''}HV30 {round(hv30,1) if hv30 else 'N/A'}%
        </p>
        """, unsafe_allow_html=True)

    # ── Price + SMA chart ──────────────────────────────────────────────────
    with chart_col:
        st.markdown('<p class="section-label">Price History with Moving Averages</p>', unsafe_allow_html=True)

        fig_live = go.Figure()

        # Candlestick (OHLC available from yfinance)
        if "Open" in mkt_data.columns and "High" in mkt_data.columns and "Low" in mkt_data.columns:
            fig_live.add_trace(go.Candlestick(
                x=mkt_data.index,
                open=mkt_data["Open"], high=mkt_data["High"],
                low=mkt_data["Low"],  close=mkt_data["Close"],
                name="Price",
                increasing_line_color="#10b981", decreasing_line_color="#f43f5e",
                increasing_fillcolor="rgba(16,185,129,0.4)",
                decreasing_fillcolor="rgba(244,63,94,0.4)",
                showlegend=True,
            ))
        else:
            fig_live.add_trace(go.Scatter(
                x=mkt_data.index, y=mkt_data["Close"],
                name="Close", line=dict(color="#00d4ff", width=1.5),
            ))

        fig_live.add_trace(go.Scatter(
            x=mkt_data.index, y=mkt_data["SMA50"],
            name="50 SMA", line=dict(color="#fbbf24", width=1.8, dash="dash"),
        ))
        fig_live.add_trace(go.Scatter(
            x=mkt_data.index, y=mkt_data["SMA200"],
            name="200 SMA", line=dict(color="#7c3aed", width=1.8, dash="dot"),
        ))

        # Shade the trend background subtly
        fig_live.add_hrect(
            y0=0, y1=1, xref="paper", yref="paper",
            fillcolor=trend_color, opacity=0.03, line_width=0,
        )

        fig_live.update_layout(
            **PLOTLY_THEME,
            height=400,
            hovermode="x unified",
            legend=dict(orientation="h", y=1.02, x=0, font=dict(size=10)),
            xaxis_rangeslider_visible=False,
            yaxis_title="Price ($)",
        )
        st.plotly_chart(fig_live, use_container_width=True)

    # ── Volume bar chart ───────────────────────────────────────────────────
    if "Volume" in mkt_data.columns and mkt_data["Volume"].sum() > 0:
        st.markdown('<p class="section-label">Volume</p>', unsafe_allow_html=True)
        vol_colors = [
            "#10b981" if mkt_data["Close"].iloc[i] >= mkt_data["Close"].iloc[i-1] else "#f43f5e"
            for i in range(len(mkt_data))
        ]
        fig_vol = go.Figure(go.Bar(
            x=mkt_data.index,
            y=mkt_data["Volume"],
            marker_color=vol_colors,
            name="Volume",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Volume: %{y:,.0f}<extra></extra>",
        ))
        fig_vol.update_layout(**PLOTLY_THEME, height=140, showlegend=False,
                              yaxis_title="Volume", margin=dict(l=40, r=20, t=10, b=40))
        st.plotly_chart(fig_vol, use_container_width=True)

    # ── Reference table: ETF & stock guide ────────────────────────────────
    with st.expander("📖  Vehicle Selection Reference Guide", expanded=False):
        st.markdown("""
<style>
.ref-table { width:100%; border-collapse:collapse; font-family:'Space Mono',monospace; font-size:0.72rem; }
.ref-table th { color:#00d4ff; border-bottom:1px solid #1e3a5f; padding:6px 10px; text-align:left; text-transform:uppercase; letter-spacing:0.08em; }
.ref-table td { padding:6px 10px; border-bottom:1px solid #1a2235; color:#e2e8f0; vertical-align:top; }
.ref-table tr:hover td { background:rgba(0,212,255,0.04); }
</style>
<table class="ref-table">
  <tr><th>Ticker</th><th>Category</th><th>Best For</th><th>Notes</th></tr>
  <tr><td>SPY</td><td>Broad Market ETF</td><td>All trends</td><td>Tightest spreads, weekly + daily expirations</td></tr>
  <tr><td>QQQ</td><td>Broad Market ETF</td><td>Tech-driven trends</td><td>Heavy FAANG/AI weighting, high liquidity</td></tr>
  <tr><td>IWM</td><td>Broad Market ETF</td><td>Sideways / Condors</td><td>Small-caps; ideal for Iron Condors</td></tr>
  <tr><td>TLT</td><td>Bond ETF</td><td>Rate-driven plays</td><td>Trade when Fed policy shifts dominate</td></tr>
  <tr><td>XLF</td><td>Sector ETF</td><td>Financials exposure</td><td>Banks + brokerages; reacts to rate moves</td></tr>
  <tr><td>XLE</td><td>Sector ETF</td><td>Energy / Oil plays</td><td>Follows crude oil; elevated IV after supply news</td></tr>
  <tr><td>SMH</td><td>Sector ETF</td><td>Semiconductor cycle</td><td>High-beta; fat premiums around earnings clusters</td></tr>
  <tr><td>AAPL / MSFT</td><td>Mega-Cap Stock</td><td>Low-IV debit spreads</td><td>Stable IV outside earnings windows</td></tr>
  <tr><td>NVDA / AMD</td><td>Mega-Cap Stock</td><td>High-IV credit spreads</td><td>Wide swings; sell spreads far OTM near earnings</td></tr>
  <tr><td>TSLA</td><td>Mega-Cap Stock</td><td>Aggressive directional</td><td>Very high IV; tight position sizing required</td></tr>
</table>
        """, unsafe_allow_html=True)
