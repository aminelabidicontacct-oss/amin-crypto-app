import streamlit as st
import pandas as pd
import requests
import ta
import time

st.set_page_config(layout="wide")

st.title("⚡ Fast Trading Core (Ultra Light)")

coins = ["BTC", "ETH", "SOL", "BNB", "SUI"]

# =========================
# CACHE DATA
# =========================
@st.cache_data(ttl=5)
def get_price(coin):
    url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={coin}&tsyms=USD"
    r = requests.get(url, timeout=3).json()
    return r["RAW"][coin]["USD"]

@st.cache_data(ttl=10)
def get_chart(coin):
    url = f"https://min-api.cryptocompare.com/data/v2/histominute?fsym={coin}&tsym=USD&limit=120"
    r = requests.get(url, timeout=5).json()
    df = pd.DataFrame(r["Data"]["Data"])
    return df

# =========================
# SIGNAL ENGINE (FAST)
# =========================
def signal(df):
    df["rsi"] = ta.momentum.rsi(df["close"], 14)
    df["ema"] = ta.trend.ema_indicator(df["close"], 50)

    last = df.iloc[-1]

    if last["close"] > last["ema"] and last["rsi"] < 40:
        return "🟢 BUY"
    elif last["close"] < last["ema"] and last["rsi"] > 60:
        return "🔴 SELL"
    else:
        return "⚪ WAIT"

# =========================
# UI LOOP
# =========================
placeholder = st.empty()

while True:
    with placeholder.container():

        cols = st.columns(len(coins))

        for i, coin in enumerate(coins):

            try:
                price = get_price(coin)
                df = get_chart(coin)
                sig = signal(df)

                cols[i].metric(
                    label=coin,
                    value=f"${price['PRICE']:.4f}",
                    delta=sig
                )

            except:
                cols[i].error(f"{coin}")

    time.sleep(3)
    st.rerun()
