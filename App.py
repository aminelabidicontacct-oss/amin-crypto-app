import streamlit as st
import pandas as pd
import requests
import ta
import time

st.set_page_config(layout="wide")

st.title("⚡ Stable Trading Terminal")

coins = ["BTC", "ETH", "SOL", "BNB", "SUI"]

# =========================
# SAFE REQUEST FUNCTION
# =========================
def safe_get(url):
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        return data
    except:
        return None

# =========================
# PRICE
# =========================
def get_price(coin):
    url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={coin}&tsyms=USD"
    data = safe_get(url)

    if not data or "RAW" not in data:
        return None

    return data["RAW"].get(coin, {}).get("USD")

# =========================
# CHART
# =========================
@st.cache_data(ttl=10)
def get_chart(coin):
    url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={coin}&tsym=USD&limit=120"
    data = safe_get(url)

    if not data or "Data" not in data:
        return None

    return pd.DataFrame(data["Data"]["Data"])

# =========================
# SIGNAL
# =========================
def analyze(df):
    df["rsi"] = ta.momentum.rsi(df["close"], 14)
    df["ema50"] = ta.trend.ema_indicator(df["close"], 50)
    df["ema200"] = ta.trend.ema_indicator(df["close"], 200)

    last = df.iloc[-1]

    if last["ema50"] > last["ema200"] and last["rsi"] < 40:
        return "🟢 BUY"
    elif last["ema50"] < last["ema200"] and last["rsi"] > 60:
        return "🔴 SELL"
    else:
        return "⚪ WAIT"

# =========================
# LOOP (STABLE VERSION)
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

            cols[i].metric(
                coin,
                f"${price['PRICE']:.4f}",
                signal
            )

    time.sleep(6)   # ⬅️ مهم جدًا
    st.rerun()
