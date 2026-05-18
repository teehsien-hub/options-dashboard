import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, date
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
        st.markdown('<p style="font-family:\'Space Mono\',monospace;font-size:0.6rem;color:#64748b;">IBOT Options Dashboard v1.0<br>Thinkorswim · IBKR Compatible</p>', unsafe_allow_html=True)

# ── Main ───────────────────────────────────────────────────────────────────
if df_raw is None:
    st.markdown('<h1 class="dashboard-title">OPTIONS P&L DASHBOARD</h1>', unsafe_allow_html=True)
    st.markdown('<p class="dashboard-sub">IBOT Trading System · Thinkorswim Integration</p>', unsafe_allow_html=True)
    st.info("👈 Select a data source in the sidebar to begin.")
    st.stop()

# Header
st.markdown('<h1 class="dashboard-title">OPTIONS P&L DASHBOARD</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="dashboard-sub">IBOT TRADING SYSTEM · {len(df)} TRADES · LAST UPDATED {df["Date"].max().strftime("%d %b %Y").upper()}</p>', unsafe_allow_html=True)

# ── KPI Row ────────────────────────────────────────────────────────────────
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

def kpi(col, label, value, fmt="$", is_pct=False):
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
tab1, tab2, tab3, tab4 = st.tabs(["📈  CUMULATIVE P&L", "🎯  BY TICKER", "📅  MONTHLY VIEW", "📋  TRADE LOG"])

# ── Tab 1: Cumulative P&L ──────────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.markdown('<p class="section-label">Cumulative Net P&L Over Time</p>', unsafe_allow_html=True)
        fig = go.Figure()

        # Shaded area
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["CumPnL"],
            fill="tozeroy",
            fillcolor="rgba(0,212,255,0.07)",
            line=dict(color="#00d4ff", width=2),
            name="Cumulative P&L",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Cumulative P&L: $%{y:,.0f}<extra></extra>"
        ))

        # Zero line
        fig.add_hline(y=0, line_color="#64748b", line_dash="dot", line_width=1)

        # Annotation for final value
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

    # Daily P&L bars
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

    # CALL vs PUT breakdown
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

    # Heatmap: P&L by ticker × month
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

    # Export
    csv_out = display.to_csv(index=False)
    st.download_button(
        "⬇ Export Filtered Trades CSV",
        data=csv_out,
        file_name=f"trades_export_{date.today()}.csv",
        mime="text/csv",
    )
