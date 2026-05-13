import streamlit as st
import pandas as pd
import requests
import ta
import time

st.set_page_config(layout="wide")

st.title("⚡ Pro Trading Terminal (Fast + Smart)")

coins = ["BTC", "ETH", "SOL", "BNB", "SUI", "XRP"]

# =========================
# CACHE (IMPORTANT FOR SPEED)
# =========================
@st.cache_data(ttl=3)
def get_price(coin):
    url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={coin}&tsyms=USD"
    r = requests.get(url, timeout=3).json()
    return r["RAW"][coin]["USD"]

@st.cache_data(ttl=5)
def get_chart(coin):
    url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={coin}&tsym=USD&limit=120"
    r = requests.get(url, timeout=5).json()
    df = pd.DataFrame(r["Data"]["Data"])
    return df

# =========================
# SMART SIGNAL ENGINE
# =========================
def analyze(df):
    df["rsi"] = ta.momentum.rsi(df["close"], 14)
    df["ema50"] = ta.trend.ema_indicator(df["close"], 50)
    df["ema200"] = ta.trend.ema_indicator(df["close"], 200)

    last = df.iloc[-1]

    trend_up = last["ema50"] > last["ema200"]

    if trend_up and last["rsi"] < 40:
        return "🟢 BUY (Trend + Pullback)"
    elif not trend_up and last["rsi"] > 60:
        return "🔴 SELL (Trend Down)"
    else:
        return "⚪ WAIT"

# =========================
# LIVE LOOP
# =========================
placeholder = st.empty()

while True:
    with placeholder.container():

        cols = st.columns(len(coins))

        for i, coin in enumerate(coins):

            try:
                price = get_price(coin)
                df = get_chart(coin)

                signal = analyze(df)

                change = price["CHANGEPCT24HOUR"]

                cols[i].metric(
                    label=coin,
                    value=f"${price['PRICE']:.4f}",
                    delta=f"{signal} | {change:.2f}%"
                )

            except:
                cols[i].error(f"{coin} error")

    time.sleep(3)
    st.rerun()
