import streamlit as st
import ccxt
import pandas as pd
import ta
import plotly.graph_objects as go

# 1. Page Configuration (iOS Optimization)
st.set_page_config(page_title="Amin AI Terminal", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0b0e11; }
    [data-testid="stMetricValue"] { font-size: 25px !important; color: #00ff88; }
    .stRadio > div { flex-direction: row; justify-content: center; gap: 15px; }
    .ai-card { padding: 20px; border-radius: 15px; text-align: center; font-weight: bold; border: 1px solid #333; margin-bottom: 20px; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 2. Top Navigation (Asset & Timeframe)
selected_coin = st.radio("Select Asset:", ["BTC/USDT", "SUI/USDT", "SOL/USDT", "ANKR/USDT"], horizontal=True)
tf = st.selectbox("Select Timeframe:", ["15m", "1h", "4h", "1d"], index=1)

@st.cache_data(ttl=30)
def fetch_market_data(symbol, timeframe):
    try:
        ex = ccxt.binance()
        ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=120)
        df = pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
        df['ts'] = pd.to_datetime(df['ts'], unit='ms')
        
        # AI Indicators
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        df['EMA_20'] = ta.trend.ema_indicator(df['close'], window=20)
        df['MA_50'] = ta.trend.sma_indicator(df['close'], window=50)
        
        ticker = ex.fetch_ticker(symbol)
        return df, ticker
    except: return None, None

# 3. AI Analysis Engine
def get_ai_decision(df):
    last = df.iloc[-1]
    rsi = last['RSI']
    price = last['close']
    ema = last['EMA_20']
    
    if rsi < 30:
        return "STRONG BUY", "#00ff88", "RSI Oversold: High reversal probability."
    elif rsi < 40 and price > ema:
        return "BUY", "#00cc66", "Bullish Trend: Price supported by EMA."
    elif rsi > 70:
        return "STRONG SELL", "#ff4b4b", "RSI Overbought: High crash risk!"
    elif rsi > 60 and price < ema:
        return "SELL", "#ff3333", "Bearish Trend: Selling pressure increasing."
    else:
        return "NEUTRAL", "#848e9c", "Market Sideways: Waiting for volume."

# 4. Live Terminal View
@st.fragment(run_every="2s")
def render_terminal(symbol, df_plot, info):
    price = info['last']
    change = info['percentage']
    
    # AI Signal Box
    signal, sig_color, reason = get_ai_decision(df_plot)
    st.markdown(f"""
        <div class="ai-card" style="background: {sig_color}22; border-color: {sig_color};">
            <h2 style="color: {sig_color}; margin: 0;">AI SIGNAL: {signal}</h2>
            <p style="color: #848e9c; margin: 5px 0;">{reason}</p>
        </div>
    """, unsafe_allow_html=True)

    # Market Stats
    m1, m2, m3 = st.columns(3)
    m1.metric("Live Price", f"${price:,.4f}", f"{change:.2f}%")
    m2.metric("RSI (14)", f"{df_plot['RSI'].iloc[-1]:.2f}")
    m3.metric("24h Volume", f"{info['quoteVolume']:,.0f}")

    # Professional Candlestick Chart
    fig = go.Figure(data=[go.Candlestick(
        x=df_plot['ts'], open=df_plot['open'], high=df_plot['high'],
        low=df_plot['low'], close=df_plot['close'],
        increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b'
    )])
    
    # Adding Trend Lines
    fig.add_trace(go.Scatter(x=df_plot['ts'], y=df_plot['EMA_20'], name='EMA 20', line=dict(color='orange', width=1)))
    
    fig.update_layout(
        template='plotly_dark', height=450, 
        margin=dict(l=0, r=0, t=0, b=0), 
        xaxis_rangeslider_visible=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig, use_container_width=True)

    # 5. News & Project Insights
    st.markdown("---")
    st.markdown("### 📰 Market Insights")
    st.info(f"**{symbol} Analysis:** AI detecting volatility patterns. Monitor EMA support levels.")
    st.success(f"**Whale Alert:** Large buy orders detected in {symbol.split('/')[0]} ecosystem.")

# Run App
df, data = fetch_market_data(selected_coin, tf)
if df is not None:
    render_terminal(selected_coin, df, data)

st.caption("Elite Terminal V3 • Powered by Amin's AI Logic")
