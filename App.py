import streamlit as st
import pandas as pd
import requests
import ta
import time

st.set_page_config(layout="wide")

st.title("⚡ Stable Pro Trading Terminal")

coins = ["BTC", "ETH", "SOL", "BNB", "SUI", "XRP"]

# =========================
# SAFE REQUEST
# =========================
def safe_get(url):
    try:
        r = requests.get(url, timeout=5)
        return r.json()
    except:
        return None

# =========================
# PRICE DATA
# =========================
def get_price(coin):
    url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={coin}&tsyms=USD"
    data = safe_get(url)

    if not data:
        return None

    try:
        return data["RAW"][coin]["USD"]
    except:
        return None

# =========================
# CHART DATA (FIXED)
# =========================
@st.cache_data(ttl=10)
def get_chart(coin):
    url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={coin}&tsym=USD&limit=120"
    data = safe_get(url)

    if not data:
        return None

    try:
        if "Data" not in data:
            return None

        if "Data" not in data["Data"]:
            return None

        df = pd.DataFrame(data["Data"]["Data"])

        if df.empty:
            return None

        return df

    except:
        return None

# =========================
# SIGNAL ENGINE
# =========================
def analyze(df):
    try:
        df["rsi"] = ta.momentum.rsi(df["close"], 14)
        df["ema50"] = ta.trend.ema_indicator(df["close"], 50)
        df["ema200"] = ta.trend.ema_indicator(df["close"], 200)

        df = df.dropna()

        if len(df) < 2:
            return "⚪ WAIT"

        last = df.iloc[-1]

        if last["ema50"] > last["ema200"] and last["rsi"] < 40:
            return "🟢 BUY"
        elif last["ema50"] < last["ema200"] and last["rsi"] > 60:
            return "🔴 SELL"
        else:
            return "⚪ WAIT"

    except:
        return "⚪ WAIT"

# =========================
# MAIN LOOP (STABLE)
# =========================
placeholder = st.empty()

while True:

    with placeholder.container():

        cols = st.columns(len(coins))

        for i, coin in enumerate(coins):

            price = get_price(coin)
            df = get_chart(coin)

            if price is None or df is None:
                cols[i].warning(f"{coin} loading...")
                continue

            signal = analyze(df)

            try:
                cols[i].metric(
                    coin,
                    f"${price['PRICE']:.4f}",
                    signal
                )
            except:
                cols[i].error(f"{coin} error")

    time.sleep(6)
    st.rerun()
