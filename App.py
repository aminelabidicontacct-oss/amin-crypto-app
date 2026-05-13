import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.subplots as sp
import requests
import ta

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Pro Trading AI", layout="wide")

# ==============================
# SIDEBAR
# ==============================
st.sidebar.title("🤖 Pro Trading AI")

symbol = st.sidebar.text_input("Enter Symbol (e.g. BTC, ETH, SUI):", value="BTC").upper()
timeframe = st.sidebar.selectbox("Select Timeframe", ["day", "hour", "minute"])
limit = st.sidebar.slider("Candles", 50, 500, 200)

# ==============================
# FETCH DATA FUNCTION
# ==============================
@st.cache_data(ttl=300)
def fetch_data(symbol, timeframe, limit):
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/histo{timeframe}?fsym={symbol}&tsym=USD&limit={limit}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        if "Data" not in data or "Data" not in data["Data"]:
            return None

        df = pd.DataFrame(data["Data"]["Data"])
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.set_index("time", inplace=True)

        return df

    except Exception:
        return None


# ==============================
# INDICATORS
# ==============================
def add_indicators(df):

    # RSI
    df["RSI"] = ta.momentum.rsi(df["close"], window=14)

    # EMA
    df["EMA50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["EMA200"] = ta.trend.ema_indicator(df["close"], window=200)

    # MACD
    macd = ta.trend.MACD(df["close"])
    df["MACD"] = macd.macd()
    df["MACD_SIGNAL"] = macd.macd_signal()
    df["MACD_HIST"] = macd.macd_diff()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df["close"])
    df["BB_HIGH"] = bb.bollinger_hband()
    df["BB_LOW"] = bb.bollinger_lband()

    return df


# ==============================
# AI SIGNAL LOGIC
# ==============================
def generate_signal(df):

    latest = df.iloc[-1]

    trend = "Bullish" if latest["EMA50"] > latest["EMA200"] else "Bearish"

    if trend == "Bullish" and latest["RSI"] < 30 and latest["MACD"] > latest["MACD_SIGNAL"]:
        return "🔥 STRONG BUY"
    elif trend == "Bearish" and latest["RSI"] > 70 and latest["MACD"] < latest["MACD_SIGNAL"]:
        return "🚨 STRONG SELL"
    elif trend == "Bullish":
        return "📈 BUY BIAS"
    else:
        return "📉 SELL BIAS"


# ==============================
# MAIN APP
# ==============================

with st.spinner("Loading Market Data..."):
    df = fetch_data(symbol, timeframe, limit)

if df is None or df.empty:
    st.error("⚠️ Error fetching data. Check symbol or internet connection.")
    st.stop()

df = add_indicators(df)

signal = generate_signal(df)

# ==============================
# METRICS
# ==============================

st.title(f"🚀 {symbol} Advanced Trading Dashboard")

col1, col2, col3 = st.columns(3)

col1.metric("Last Price", f"${df['close'].iloc[-1]:.4f}")
col2.metric("RSI", f"{df['RSI'].iloc[-1]:.2f}")
col3.metric("Signal", signal)

# ==============================
# CREATE MULTI-CHART
# ==============================

fig = sp.make_subplots(
    rows=3, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    row_heights=[0.6, 0.2, 0.2]
)

# --- Candlestick ---
fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price"
    ),
    row=1, col=1
)

# EMA
fig.add_trace(go.Scatter(x=df.index, y=df["EMA50"], name="EMA50"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["EMA200"], name="EMA200"), row=1, col=1)

# Bollinger
fig.add_trace(go.Scatter(x=df.index, y=df["BB_HIGH"], name="BB High"), row=1, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["BB_LOW"], name="BB Low"), row=1, col=1)

# --- RSI ---
fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI"), row=2, col=1)

# --- MACD ---
fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD"), row=3, col=1)
fig.add_trace(go.Scatter(x=df.index, y=df["MACD_SIGNAL"], name="Signal"), row=3, col=1)
fig.add_trace(go.Bar(x=df.index, y=df["MACD_HIST"], name="Histogram"), row=3, col=1)

fig.update_layout(
    template="plotly_dark",
    height=900,
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

st.success("AI Engine Active ✅")
