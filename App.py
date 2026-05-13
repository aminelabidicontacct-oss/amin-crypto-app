import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import ta

# 1. High-Speed Setup
st.set_page_config(page_title="Amin Pro Terminal", layout="wide")
st.markdown("""<style> .main { background-color: #000; } [data-testid="stMetricValue"] { color: #00ff88 !important; } </style>""", unsafe_allow_html=True)

st.title("Amin Pro Intelligence V7")

# 2. Controls
col_a, col_b = st.columns(2)
with col_a:
    symbol = st.text_input("Asset:", "SUI").upper()
with col_b:
    tf = st.selectbox("Interval:", ["hour", "day", "minute"], index=0)

# 3. Data Engine
@st.cache_data(ttl=5)
def get_pro_data(coin, interval):
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/histo{interval}?fsym={coin}&tsym=USD&limit=100"
        r = requests.get(url).json()
        df = pd.DataFrame(r['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calculate All Indicators
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        df['MA'] = ta.trend.sma_indicator(df['close'], window=20)
        df['EMA'] = ta.trend.ema_indicator(df['close'], window=20)
        macd = ta.trend.MACD(df['close'])
        df['MACD'] = macd.macd()
        df['MACD_S'] = macd.macd_signal()
        
        p_url = f"https://min-api.cryptocompare.com/data/price?fsym={coin}&tsyms=USD"
        price = requests.get(p_url).json()['USD']
        return df, price
    except: return None, None

# 4. Logic & Display
df, live_p = get_pro_data(symbol, tf)

if df is not None:
    # Header Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric(f"LIVE {symbol}", f"${live_p:,.4f}")
    m2.metric("24H HIGH", f"${df['high'].max():,.2f}")
    m3.metric("RSI", f"{df['RSI'].iloc[-1]:,.2f}")

    # Main Chart (Candlesticks)
    fig = go.Figure(data=[go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Price')])
    
    # 5. USER OPTIONS (Below Chart Selection)
    st.write("---")
    option = st.radio("SELECT INDICATOR TO OVERLAY/SHOW:", ["NONE", "MA", "EMA", "RSI", "MACD"], horizontal=True)

    if option == "MA":
        fig.add_trace(go.Scatter(x=df['time'], y=df['MA'], name='MA 20', line=dict(color='cyan', width=1.5)))
    elif option == "EMA":
        fig.add_trace(go.Scatter(x=df['time'], y=df['EMA'], name='EMA 20', line=dict(color='orange', width=1.5)))
    
    fig.update_layout(template='plotly_dark', height=450, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # Secondary Chart for RSI/MACD (if selected)
    if option in ["RSI", "MACD"]:
        fig_ind = go.Figure()
        if option == "RSI":
            fig_ind.add_trace(go.Scatter(x=df['time'], y=df['RSI'], name='RSI', line=dict(color='yellow')))
            fig_ind.add_hline(y=70, line_dash="dash", line_color="red")
            fig_ind.add_hline(y=30, line_dash="dash", line_color="green")
        else:
            fig_ind.add_trace(go.Scatter(x=df['time'], y=df['MACD'], name='MACD', line=dict(color='blue')))
            fig_ind.add_trace(go.Scatter(x=df['time'], y=df['MACD_S'], name='Signal', line=dict(color='orange')))
        
        fig_ind.update_layout(template='plotly_dark', height=200, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_ind, use_container_width=True)

else:
    st.error("Connecting to Global Nodes...")

st.caption("Turbo V7 • Dynamic Indicator Engine • 2026")
