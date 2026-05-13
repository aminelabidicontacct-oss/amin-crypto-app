import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import ta

# 1. UI Configuration
st.set_page_config(page_title="Trading AI", layout="wide")
st.markdown("""
<style>
    .main { background-color: #0b0e11; color: white; }
    [data-testid="stMetricValue"] { color: #00ff88 !important; font-size: 26px !important; }
    .stMetric { background: #161a1e; padding: 15px; border-radius: 10px; border: 1px solid #2b2f36; }
    .modebar { display: none !important; }
    ::-webkit-scrollbar { display: none; }
</style>
""", unsafe_allow_html=True)

# 2. Sidebar Navigation - FIXED AUTO-VALUE
st.sidebar.title("🤖 Trading AI")
# جعلنا SUI هي القيمة الافتراضية هنا لتجنب الشاشة الصفراء
target = st.sidebar.text_input("Search Symbol:", value="SUI").upper()

tf_map = {
    "1 Minute": "minute", "5 Minutes": "minute&limit=500", 
    "15 Minutes": "minute&limit=1000", "30 Minutes": "minute&limit=2000",
    "1 Hour": "hour", "4 Hours": "hour&limit=500", 
    "1 Day": "day", "1 Week": "day&limit=1000"
}
selected_tf = st.sidebar.selectbox("Select Timeframe:", list(tf_map.keys()))

# 3. Enhanced Data Engine with Error Logs
def get_trading_data(coin):
    try:
        # Statistics
        url_stats = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={coin}&tsyms=USD"
        stat_res = requests.get(url_stats).json()
        
        if 'RAW' not in stat_res: return None, None
        res = stat_res['RAW'][coin]['USD']
        
        # History
        api_tf = tf_map[selected_tf]
        url_hist = f"https://min-api.cryptocompare.com/data/v2/histo{api_tf}&fsym={coin}&tsym=USD"
        hist_res = requests.get(url_hist).json()
        
        if 'Data' not in hist_res or 'Data' not in hist_res['Data']: return None, None
        df = pd.DataFrame(hist_res['Data']['Data'])
        
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df['EMA_20'] = ta.trend.ema_indicator(df['close'], window=20)
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        
        return df, res
    except Exception as e:
        return None, str(e)

df, stats = get_trading_data(target)

# 4. Interface Rendering
if df is not None and isinstance(df, pd.DataFrame):
    st.title(f"🚀 Trading AI: {target} Intelligence")
    
    # Top Stats Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Price", f"${stats['PRICE']:,.4f}")
    c2.metric("Market Cap", f"${stats['MKTCAP']:,.0f}")
    c3.metric("24h High", f"${stats['HIGH24HOUR']:,.4f}")
    c4.metric("24h Low", f"${stats['LOW24HOUR']:,.4f}")

    # Professional Chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df['time'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], name='Price'))
    fig.add_trace(go.Scatter(x=df['time'], y=df['EMA_20'], name='EMA 20', line=dict(color='#ff9800', width=1.5)))

    fig.update_layout(
        template='plotly_dark', height=600, margin=dict(l=0, r=10, t=0, b=0),
        xaxis_rangeslider_visible=False, dragmode=False,
        yaxis=dict(side='right'), paper_bgcolor='#0b0e11', plot_bgcolor='#0b0e11'
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # AI Section
    st.markdown("---")
    rsi_val = df['RSI'].iloc[-1]
    color = "#00ff88" if rsi_val < 35 else "#ff4b4b" if rsi_val > 65 else "#ffcc00"
    st.subheader(f"🤖 AI Analysis: {target}")
    st.markdown(f"Current RSI is **{rsi_val:.2f}**. Recommendation: <b style='color:{color};'>CHECK MARKET TREND</b>", unsafe_allow_html=True)

else:
    st.error(f"Waiting for Data... Try a different symbol or check your connection. (Target: {target})")
    st.info("Tip: Make sure you are using official symbols like BTC, SUI, or SOL.")

st.caption("Trading AI • V13 Stable Engine • 2026")
    
