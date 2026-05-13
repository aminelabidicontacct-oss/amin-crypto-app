import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import ta
import numpy as np
from sklearn.linear_model import LinearRegression

# 1. UI & Theme Configuration
st.set_page_config(page_title="Amin Ultra AI", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #0b0e11; }
    [data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 28px !important; }
    .stMetric { background: #161a1e; padding: 15px; border-radius: 10px; border: 1px solid #2b2f36; }
    .modebar { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar Watchlist (Global Monitoring)
st.sidebar.title("Watchlist")
for coin in ["SUI", "ANKR", "SOL", "BTC"]:
    try:
        p = requests.get(f"https://min-api.cryptocompare.com/data/price?fsym={coin}&tsyms=USD").json()['USD']
        st.sidebar.markdown(f"**{coin}**: `${p:,.4f}`")
    except: pass

# 3. Core Engine & AI Logic
@st.cache_data(ttl=1)
def get_ultra_data(coin, interval):
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/histo{interval}?fsym={coin}&tsym=USD&limit=100"
        df = pd.DataFrame(requests.get(url).json()['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Technical Indicators
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        df['EMA_20'] = ta.trend.ema_indicator(df['close'], window=20)
        macd = ta.trend.MACD(df['close'])
        df['MACD'] = macd.macd_diff()
        
        # AI Prediction (Simple Linear Regression)
        y = df['close'].values.reshape(-1, 1)
        X = np.array(range(len(y))).reshape(-1, 1)
        model = LinearRegression().fit(X, y)
        next_index = np.array([[len(y) + 5]])
        prediction = model.predict(next_index)[0][0]
        
        live_p = requests.get(f"https://min-api.cryptocompare.com/data/price?fsym={coin}&tsyms=USD").json()['USD']
        return df, live_p, prediction
    except: return None, None, None

# 4. Main Interface
st.title("Amin Ultra AI Intelligence 🚀")
c1, c2 = st.columns([2, 1])
with c1: target = st.text_input("Asset:", "SUI").upper()
with c2: tf = st.selectbox("Timeframe:", ["minute", "hour", "day"])

df, live_p, pred = get_ultra_data(target, tf)

if df is not None:
    # AI Decision Logic
    last_rsi = df['RSI'].iloc[-1]
    last_macd = df['MACD'].iloc[-1]
    
    if last_rsi < 35 and last_macd > 0:
        advice, color = "STRONG BUY 🟢", "#00ff88"
    elif last_rsi > 65 and last_macd < 0:
        advice, color = "STRONG SELL 🔴", "#ff4b4b"
    else:
        advice, color = "WAIT / NEUTRAL 🟡", "#ffcc00"

    st.markdown(f"<h2 style='text-align: center; color: {color}; border: 2px solid {color}; padding: 10px; border-radius: 10px;'>AI DECISION: {advice}</h2>", unsafe_allow_html=True)

    # Professional Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Live Price", f"${live_p:,.4f}")
    m2.metric("AI Target", f"${pred:,.4f}")
    m3.metric("RSI (14)", f"{last_rsi:.2f}")
    m4.metric("24H High", f"${df['high'].max():,.2f}")

    # The Static Professional Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Price'))
    fig.add_trace(go.Scatter(x=df['time'], y=df['EMA_20'], name='EMA 20', line=dict(color='orange', width=1.5)))
    
    fig.update_layout(
        template='plotly_dark', height=600, margin=dict(l=0, r=10, t=0, b=0),
        xaxis_rangeslider_visible=False, dragmode=False, 
        yaxis=dict(side='right', fixedrange=False), xaxis=dict(fixedrange=True),
        paper_bgcolor='#0b0e11', plot_bgcolor='#0b0e11'
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.info(f"AI Insight: Current trend suggests price is moving towards ${pred:,.4f}. Based on RSI and MACD, the market is currently {advice.split()[0]}.")
else:
    st.error("Engine searching global nodes... Please check the symbol.")

st.caption("Amin V11 Ultra AI • The Professional Terminal • 2026")
