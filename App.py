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
# BATCH PRICE (FASTER FIX)
# =========================
def get_prices_batch(coins):
    symbols = ",".join(coins)
    url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={symbols}&tsyms=USD"
    data = safe_get(url)

    if not data or "RAW" not in data:
        return {}

    return data["RAW"]

# =========================
# CHART DATA
# =========================
@st.cache_data(ttl=10)
def get_chart(coin):
    url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={coin}&tsym=USD&limit=120"
    data = safe_get(url)

    if not data or "Data" not in data or "Data" not in data["Data"]:
        return None

    df = pd.DataFrame(data["Data"]["Data"])

    if df.empty:
        return None

    return df

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
# MAIN LOOP (NO LOADING FIX)
# =========================
placeholder = st.empty()

while True:

    with placeholder.container():

        prices = get_prices_batch(coins)

        cols = st.columns(len(coins))

        for i, coin in enumerate(coins):

            try:
                price_data = prices.get(coin, {}).get("USD", {})
                price = price_data.get("PRICE", None)

                df = get_chart(coin)

                if price is None or df is None:
                    # NO LOADING TEXT ANYMORE
                    cols[i].empty()
                    continue

                signal = analyze(df)

                cols[i].metric(
                    coin,
                    f"${price:.4f}",
                    signal
                )

            except:
                cols[i].empty()

    time.sleep(6)
    st.rerun()
