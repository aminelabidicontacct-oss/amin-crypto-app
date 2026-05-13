import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
import numpy as np

st.set_page_config(page_title="Amin Pro Analyzer", layout="wide")
st.title("Amin Professional Crypto Analyzer")

symbol = st.sidebar.selectbox("Select Symbol", ["SUI/USDT", "BTC/USDT", "ETH/USDT", "SOL/USDT", "ANKR/USDT"])
timeframe = st.sidebar.selectbox("Timeframe", ["1h", "4h", "1d"])

exchange = ccxt.binance()

@st.cache_data(ttl=60)
def get_data(coin, tf):
    bars = exchange.fetch_ohlcv(coin, timeframe=tf, limit=200)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'vol'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    return df

df = get_data(symbol, timeframe)

df['RSI'] = ta.rsi(df['close'], length=14)
df['MA50'] = ta.sma(df['close'], length=50)
df['MA200'] = ta.sma(df['close'], length=200)

macd = ta.macd(df['close'])
df = pd.concat([df, macd], axis=1)

bbands = ta.bbands(df['close'], length=20)
df = pd.concat([df, bbands], axis=1)

highest_high = df['high'].tail(100).max()
lowest_low = df['low'].tail(100).min()
diff = highest_high - lowest_low
fibo_levels = {
    '0.0%': highest_high,
    '23.6%': highest_high - 0.236 * diff,
    '38.2%': highest_high - 0.382 * diff,
    '50.0%': highest_high - 0.5 * diff,
    '61.8%': highest_high - 0.618 * diff,
    '100.0%': lowest_low
}

last_price = df['close'].iloc[-1]
last_rsi = df['RSI'].iloc[-1]
last_macd_h = df.iloc[-1]['MACDh_12_26_9']

score = 0
reasons = []

if last_rsi < 35: 
    score += 1; reasons.append("RSI Oversold")
if last_price > df['MA200'].iloc[-1]: 
    score += 1; reasons.append("Price Above MA200")
if last_macd_h > 0: 
    score += 1; reasons.append("Positive MACD Momentum")
if last_price <= fibo_levels['61.8%'] * 1.01:
    score += 1; reasons.append("Price at Fibonacci 61.8%")

col1, col2 = st.columns([1, 1])

with col1:
    st.header(f"{symbol} Price: ${last_price}")
    if score >= 3:
        st.success(f"STRONG BUY SIGNAL! ({score}/4)")
    elif score == 2:
        st.warning("NEUTRAL - Wait")
    else:
        st.error("NO ENTRY SIGNAL")
    
    for r in reasons: st.write(f"- {r}")

with col2:
    st.write("### Fibonacci Levels")
    st.table(pd.DataFrame(fibo_levels.items(), columns=['Level', 'Price']))

st.subheader("Price Action")
st.line_chart(df.set_index('time')[['close', 'BBM_20_2.0', 'BBU_20_2.0', 'BBL_20_2.0']])

st.subheader("RSI Indicator")
st.line_chart(df.set_index('time')['RSI'])
