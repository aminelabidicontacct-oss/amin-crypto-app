import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import ta

# 1. Pro UI Setup
st.set_page_config(page_title="Amin Live", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #000000; }
    [data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 35px !important; }
    div.stButton > button { width: 100%; border-radius: 5px; }
    /* Hide Plotly Toolbar */
    .modebar { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. Top Controls
c1, c2 = st.columns([2, 1])
with c1: symbol = st.text_input("ASSET:", "SUI").upper()
with c2: tf = st.selectbox("TF:", ["minute", "hour", "day"], index=0)

# 3. Fast Engine
@st.cache_data(ttl=1) # Update every second
def get_amin_data(coin, interval):
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/histo{interval}?fsym={coin}&tsym=USD&limit=40"
        r = requests.get(url).json()
        df = pd.DataFrame(r['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calculate Indicators
        df['MA'] = ta.trend.sma_indicator(df['close'], window=10)
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        
        p_url = f"https://min-api.cryptocompare.com/data/price?fsym={coin}&tsyms=USD"
        price = requests.get(p_url).json()['USD']
        return df, price
    except: return None, None

# 4. Logic & Locked Chart
df, live_p = get_amin_data(symbol, tf)

if df is not None:
    # Live Metric
    st.metric(f"{symbol} LIVE PRICE", f"${live_p:,.4f}")

    # Build The Locked Chart
    fig = go.Figure()

    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df['time'], open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name='Price'
    ))

    # LOCK THE VIEW (No Zoom, No Pan)
    fig.update_layout(
        template='plotly_dark',
        height=500,
        margin=dict(l=10, r=10, t=0, b=0),
        xaxis_rangeslider_visible=False,
        dragmode=False, # Disable dragging/zooming
        yaxis=dict(fixedrange=False), # Auto-scale price
        xaxis=dict(fixedrange=True),  # Lock time axis
        paper_bgcolor='black',
        plot_bgcolor='black'
    )

    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': False, 'displayModeBar': False})

    # 5. Bottom Quick Options
    st.write("---")
    ind_choice = st.radio("INDICATOR:", ["OFF", "MA", "RSI"], horizontal=True)
    
    if ind_choice == "MA":
        st.info(f"Moving Average (10): {df['MA'].iloc[-1]:,.4f}")
    elif ind_choice == "RSI":
        st.info(f"RSI (14): {df['RSI'].iloc[-1]:,.2f}")

else:
    st.error("Searching global nodes...")

st.caption("Amin V8 • Pure Live Feed • No Zoom")
