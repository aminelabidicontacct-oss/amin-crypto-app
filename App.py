import streamlit as st
import pandas as pd
import requests
import ta
import time

st.set_page_config(layout="wide")

st.title("⚡ Smart Trading AI (Light Version)")

coins = st.multiselect(
    "Select Coins",
    ["BTC", "ETH", "BNB", "SOL", "SUI", "XRP"],
    default=["BTC"]
)

timeframe = st.selectbox("Timeframe", ["minute", "hour"])

# =========================
# CACHE (VERY IMPORTANT)
# =========================
@st.cache_data(ttl=10)  # cache 10 sec
def get_price(symbol):
    url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbol}&tsyms=USD"
    r = requests.get(url, timeout=5).json()
    return r["RAW"][symbol]["USD"]

@st.cache_data(ttl=10)
def get_chart(symbol, tf):
    url = f"https://min-api.cryptocompare.com/data/v2/histo{tf}?fsym={symbol}&tsym=USD&limit=100"
    r = requests.get(url, timeout=5).json()
    df = pd.DataFrame(r["Data"]["Data"])
    return df

# =========================
# SIGNAL ENGINE
# =========================
def analyze(df):
    df["rsi"] = ta.momentum.rsi(df["close"], window=14)
    df["ema"] = ta.trend.ema_indicator(df["close"], window=50)

    last = df.iloc[-1]

    trend = "UP" if last["close"] > last["ema"] else "DOWN"

    if trend == "UP" and last["rsi"] < 40:
        return "🟢 BUY (High probability)"
    elif trend == "DOWN" and last["rsi"] > 60:
        return "🔴 SELL (High probability)"
    else:
        return "⚪ WAIT"

# =========================
# AUTO REFRESH
# =========================
st.caption("Auto refresh every 10 seconds")

for coin in coins:

    try:
        price_data = get_price(coin)
        df = get_chart(coin, timeframe)

        signal = analyze(df)

        st.subheader(f"{coin}")

        col1, col2, col3 = st.columns(3)

        col1.metric("Price", f"${price_data['PRICE']:.4f}")
        col2.metric("24h High", f"${price_data['HIGH24HOUR']:.4f}")
        col3.metric("Signal", signal)

    except:
        st.warning(f"Error loading {coin}")

st.rerun()
