import streamlit as st
import ccxt
import pandas as pd
import ta
import plotly.graph_objects as go

st.set_page_config(page_title="Amin Pro Radar", layout="wide")

# Professional UI Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stHorizontalBlock"] { background: #161a1d; padding: 15px; border-radius: 15px; }
    [data-testid="stMetricValue"] { font-size: 40px !important; color: #00ff88; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 1. Selection Interface
selected_coin = st.radio(
    "Asset Selection:", 
    ["BTC/USDT", "SUI/USDT", "SOL/USDT", "ANKR/USDT", "ETH/USDT"], 
    horizontal=True
)

@st.cache_data(ttl=60)
def get_market_data(symbol):
    try:
        ex = ccxt.kucoin()
        ohlcv = ex.fetch_ohlcv(symbol, timeframe='1h', limit=60)
        df = pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
        df['ts'] = pd.to_datetime(df['ts'], unit='ms')
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        return df
    except: return None

# 2. Live Update (Prevents Fading/Flickering)
@st.fragment(run_every="1s")
def render_dashboard(symbol, rsi_val, df_plot):
    try:
        t = ccxt.kucoin().fetch_ticker(symbol)
        price, change = t['last'], t['percentage']
        color = "#00ff88" if change >= 0 else "#ff4b4b"
        
        # Price Card
        st.markdown(f"""
            <div style="background: #161a1d; padding: 25px; border-radius: 20px; border-left: 10px solid {color}; text-align: center;">
                <h1 style="color: {color}; margin: 0;">${price:,.4f}</h1>
                <p style="color: {color}; font-weight: bold; font-size: 18px;">{change}%</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        c1, c2 = st.columns(2)
        c1.metric("RSI (14)", f"{rsi_val:.2f}")
        
        if rsi_val > 70: c2.error("SIGNAL: SELL")
        elif rsi_val < 30: c2.success("SIGNAL: BUY")
        else: c2.info("SIGNAL: NEUTRAL")

        # 3. Candlestick Chart
        fig = go.Figure(data=[go.Candlestick(
            x=df_plot['ts'], open=df_plot['open'], high=df_plot['high'],
            low=df_plot['low'], close=df_plot['close'],
            increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b'
        )])
        fig.update_layout(
            template='plotly_dark', 
            xaxis_rangeslider_visible=False, 
            margin=dict(l=5, r=5, t=5, b=5),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
    except: st.write("Syncing...")

# Execute
df = get_market_data(selected_coin)
if df is not None:
    render_dashboard(selected_coin, df['RSI'].iloc[-1], df)
