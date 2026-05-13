import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import ta

# 1. Dashboard Styling (Dark Mode Pro)
st.set_page_config(page_title="Amin TV Terminal", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #131722; } /* TradingView Dark Blue */
    [data-testid="stMetricValue"] { color: #2962ff !important; font-size: 25px !important; }
    .stMetric { background: #1e222d; padding: 10px; border-radius: 5px; }
    /* Hide scrollbars for clean look */
    ::-webkit-scrollbar { display: none; }
    </style>
    """, unsafe_allow_html=True)

# 2. Sidebar Watchlist (Like 13611.jpg)
st.sidebar.title("Watchlist")
watchlist = ["SUI", "ANKR", "SOL", "BTC", "ETH"]

def get_quick_price(symbol):
    try:
        url = f"https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USD"
        return requests.get(url).json()['USD']
    except: return 0

for coin in watchlist:
    price = get_quick_price(coin)
    st.sidebar.markdown(f"**{coin}** : `${price:,.4f}`")

# 3. Main Interface - Active Chart
c1, c2 = st.columns([3, 1])
with c1:
    target = st.text_input("Active Symbol:", "SUI").upper()
with c2:
    timeframe = st.selectbox("Interval:", ["minute", "hour", "day"])

# 4. Global Engine V10
@st.cache_data(ttl=1)
def fetch_tv_data(coin, interval):
    try:
        url = f"https://min-api.cryptocompare.com/data/v2/histo{interval}?fsym={coin}&tsym=USD&limit=50"
        data = requests.get(url).json()['Data']['Data']
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Tech Indicators
        df['EMA'] = ta.trend.ema_indicator(df['close'], window=20)
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        
        live = requests.get(f"https://min-api.cryptocompare.com/data/price?fsym={coin}&tsyms=USD").json()['USD']
        return df, live
    except: return None, None

df, current_price = fetch_tv_data(target, timeframe)

if df is not None:
    # Top Stats Bar
    col1, col2, col3 = st.columns(3)
    col1.metric(target, f"${current_price:,.4f}")
    col2.metric("RSI (14)", f"{df['RSI'].iloc[-1]:,.2f}")
    col3.metric("EMA (20)", f"{df['EMA'].iloc[-1]:,.4f}")

    # The TradingView Style Chart
    fig = go.Figure()
    # Candlesticks
    fig.add_trace(go.Candlestick(
        x=df['time'], open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name='Price'
    ))
    # Overlay EMA
    fig.add_trace(go.Scatter(x=df['time'], y=df['EMA'], name='EMA 20', line=dict(color='#ff9800', width=1.5)))

    fig.update_layout(
        template='plotly_dark', height=550,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis_rangeslider_visible=False,
        dragmode='pan', # Smooth mobile movement
        paper_bgcolor='#131722', plot_bgcolor='#131722',
        yaxis=dict(side='right') # Price on the right like TV
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
else:
    st.error("Connecting to global market...")

st.caption("Amin V10 • TradingView Experience • Powered by V8 Engine")
  
