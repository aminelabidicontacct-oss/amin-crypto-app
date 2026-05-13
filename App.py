import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import ta

# 1. Dashboard Core Setup
st.set_page_config(page_title="Trading AI", layout="wide")
st.markdown("""
<style>
    .main { background-color: #0b0e11; color: white; }
    [data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 26px !important; }
    .stMetric { background: #161a1e; padding: 15px; border-radius: 10px; border: 1px solid #2b2f36; }
    /* Hide Plotly Toolbar & Scrollbars */
    .modebar { display: none !important; }
    ::-webkit-scrollbar { display: none; }
</style>
""", unsafe_allow_html=True)

# 2. Global Navigation & Search
st.sidebar.title("🤖 Trading AI")
target = st.sidebar.text_input("Search Symbol (e.g. SUI, BTC, ETH):", "SUI").upper()

# Timeframe Map for full history coverage
tf_map = {
    "1 Minute": "minute", "5 Minutes": "minute&limit=500", 
    "15 Minutes": "minute&limit=1000", "30 Minutes": "minute&limit=2000",
    "1 Hour": "hour", "4 Hours": "hour&limit=500", 
    "1 Day": "day", "1 Week": "day&limit=1000"
}
selected_tf = st.sidebar.selectbox("Select Timeframe:", list(tf_map.keys()))

# 3. Master Data Engine
def get_trading_ai_data(coin):
    try:
        # Fetching Live Market Stats (Market Cap, Volume, Supply, High/Low)
        url_stats = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={coin}&tsyms=USD"
        res = requests.get(url_stats).json()['RAW'][coin]['USD']
        
        # Fetching Historical Data for Full View
        api_tf = tf_map[selected_tf]
        url_hist = f"https://min-api.cryptocompare.com/data/v2/histo{api_tf}&fsym={coin}&tsym=USD"
        hist_res = requests.get(url_hist).json()['Data']['Data']
        
        df = pd.DataFrame(hist_res)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Adding Professional Indicators
        df['EMA_20'] = ta.trend.ema_indicator(df['close'], window=20)
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        
        return df, res
    except: return None, None

df, stats = get_trading_ai_data(target)

# 4. Professional Interface Layout
if df is not None and stats is not None:
    st.title(f"🚀 Trading AI: {target} Intelligence")
    
    # Live Snapshot Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Live Price", f"${stats['PRICE']:,.4f}")
    c2.metric("Market Cap", f"${stats['MKTCAP']:,.0f}")
    c3.metric("24h High", f"${stats['HIGH24HOUR']:,.4f}")
    c4.metric("24h Low", f"${stats['LOW24HOUR']:,.4f}")

    # Liquidity & Volume Metrics
    v1, v2, v3 = st.columns(3)
    v1.metric("24h Trading Volume", f"${stats['VOLUME24HOURTO']:,.0f}")
    v2.metric("Circulating Supply", f"{stats['SUPPLY']:,.0f}")
    v3.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")

    # 5. Trading AI Professional Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['time'], open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name='Price Action'
    ))
    fig.add_trace(go.Scatter(x=df['time'], y=df['EMA_20'], name='EMA 20', line=dict(color='#ff9800', width=1.5)))

    fig.update_layout(
        template='plotly_dark', height=650,
        margin=dict(l=0, r=10, t=0, b=0),
        xaxis_rangeslider_visible=False,
        dragmode=False, # Stabilized View for Phone Users
        yaxis=dict(side='right', title="Price (USD)", fixedrange=False),
        xaxis=dict(fixedrange=True),
        paper_bgcolor='#0b0e11', plot_bgcolor='#0b0e11'
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # 6. AI Decision Engine Result
    st.markdown("---")
    st.subheader("🤖 AI Market Analysis")
    rsi_now = df['RSI'].iloc[-1]
    if rsi_now < 30: 
        decision, d_color = "OVERSOLD (BUY OPPORTUNITY) 🟢", "#00ff88"
    elif rsi_now > 70: 
        decision, d_color = "OVERBOUGHT (SELL RISK) 🔴", "#ff4b4b"
    else: 
        decision, d_color = "NEUTRAL / HOLD 🟡", "#ffcc00"
    
    st.markdown(f"**Current Recommendation:** <span style='color:{d_color}; font-size:20px;'>{decision}</span>", unsafe_allow_html=True)
    st.write(f"Trend Observation: {target} is showing active data across {len(df)} candles on the {selected_tf} chart.")

else:
    st.warning("Please enter a valid symbol in the sidebar (e.g. BTC) to activate Trading AI.")

st.caption(f"Trading AI • V12 Engine • Global Data Active • 2026 Edition")
    
