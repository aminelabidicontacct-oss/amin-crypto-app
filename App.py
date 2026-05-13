import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import ta

# 1. Global Setup (High Performance)
st.set_page_config(page_title="Amin Global AI", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e11; }
    [data-testid="stMetricValue"] { color: #00ff88; font-weight: bold; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("Amin Global Intelligence V5")

# 2. Fast Input Section
c1, c2 = st.columns(2)
with c1:
    symbol = st.text_input("Enter Asset (e.g. BTC, SUI, SOL):", "SUI").upper()
with c2:
    timeframe = st.selectbox("Interval:", ["hour", "day", "minute"], index=0)

# 3. Multi-Source Global Data Engine
@st.cache_data(ttl=10)
def fetch_global_market(coin, interval):
    try:
        # Aggregating from fastest global nodes
        url = f"https://min-api.cryptocompare.com/data/v2/histo{interval}?fsym={coin}&tsym=USD&limit=100"
        response = requests.get(url).json()
        raw_data = response['Data']['Data']
        
        df = pd.DataFrame(raw_data)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Technical Analysis (AI Indicators)
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        df['EMA'] = ta.trend.ema_indicator(df['close'], window=20)
        
        # Latest Live Price
        price_url = f"https://min-api.cryptocompare.com/data/price?fsym={coin}&tsyms=USD"
        live_price = requests.get(price_url).json()['USD']
        
        return df, live_price
    except:
        return None, None

# 4. AI Decision & Rendering
df, current_p = fetch_global_market(symbol, timeframe)

if df is not None:
    last_rsi = df['RSI'].iloc[-1]
    
    # AI Signal Display
    if last_rsi < 35:
        st.success(f"AI SIGNAL: STRONG BUY (RSI: {last_rsi:.2f})")
    elif last_rsi > 65:
        st.error(f"AI SIGNAL: STRONG SELL (RSI: {last_rsi:.2f})")
    else:
        st.warning(f"AI SIGNAL: NEUTRAL (RSI: {last_rsi:.2f})")

    # Metrics Row
    m1, m2, m3 = st.columns(3)
    m1.metric("Live Price", f"${current_p:,.4f}")
    m2.metric("24h High", f"${df['high'].max():,.2f}")
    m3.metric("Global Vol", f"{df['volumeto'].sum():,.0f}")

    # Professional Charting
    fig = go.Figure(data=[go.Candlestick(
        x=df['time'], open=df['open'], high=df['high'],
        low=df['low'], close=df['close'],
        increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b'
    )])
    
    fig.add_trace(go.Scatter(x=df['time'], y=df['EMA'], name='EMA 20', line=dict(color='orange', width=1)))
    
    fig.update_layout(template='plotly_dark', height=480, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.error("Connection Failed. Check Symbol or Internet.")

st.caption("Terminal V5 • No-Limit Global Data • 2026 Edition")
    
