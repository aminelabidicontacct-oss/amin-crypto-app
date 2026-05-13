import streamlit as st
import ccxt
import pandas as pd
import ta
import plotly.graph_objects as go

# 1. إعدادات الصفحة الأساسية
st.set_page_config(page_title="Amin AI Terminal", layout="wide")

# تنسيق الواجهة لتكون مريحة للعين (Dark Mode)
st.markdown("""
    <style>
    .main { background-color: #0b0e11; }
    h1, h2, h3 { color: #f0b90b !important; text-align: center; }
    .stMetric { background-color: #1e2329; padding: 10px; border-radius: 10px; border: 1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚀 رادار أمين الذكي V3")

# 2. لوحة التحكم (العملة والفريم)
col_nav1, col_nav2 = st.columns(2)
with col_nav1:
    coin = st.selectbox("إختر العملة:", ["BTC/USDT", "SUI/USDT", "SOL/USDT", "ANKR/USDT"], index=1)
with col_nav2:
    tf = st.selectbox("إختر الفريم (Timeframe):", ["15m", "1h", "4h", "1d"], index=1)

# 3. جلب البيانات مع "كاش" (Caching) لتجنب التعليق
@st.cache_data(ttl=30)
def get_market_data(symbol, timeframe):
    try:
        ex = ccxt.binance()
        ohlcv = ex.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
        df = pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'vol'])
        df['ts'] = pd.to_datetime(df['ts'], unit='ms')
        # حساب المؤشرات للذكاء الاصطناعي
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        df['EMA_20'] = ta.trend.ema_indicator(df['close'], window=20)
        ticker = ex.fetch_ticker(symbol)
        return df, ticker
    except:
        return None, None

# تنفيذ الجلب
df, ticker_info = get_market_data(coin, tf)

if df is not None:
    # 4. محرك قرار الذكاء الاصطناعي
    rsi_val = df['RSI'].iloc[-1]
    current_price = ticker_info['last']
    ema_val = df['EMA_20'].iloc[-1]
    
    if rsi_val < 35:
        decision, color = "فرصة شراء قوية (BUY) 📈", "green"
    elif rsi_val > 65:
        decision, color = "فرصة بيع قوية (SELL) 📉", "red"
    else:
        decision, color = "إنتظر - وضع محايد (WAIT) ⚖️", "gray"

    # عرض قرار الذكاء الاصطناعي
    st.markdown(f"""
        <div style="background-color: {color}; padding: 20px; border-radius: 15px; text-align: center;">
            <h2 style="color: white !important; margin: 0;">توصية الذكاء الاصطناعي: {decision}</h2>
            <p style="color: white;">قوة مؤشر الـ RSI حالياً: {rsi_val:.2f}</p>
        </div>
    """, unsafe_allow_html=True)

    st.write("---")

    # 5. عرض إحصائيات السوق
    m1, m2, m3 = st.columns(3)
    m1.metric("السعر الحالي", f"${current_price:,.4f}", f"{ticker_info['percentage']}%")
    m2.metric("أعلى سعر (24h)", f"${ticker_info['high']:,.2f}")
    m3.metric("حجم التداول", f"{ticker_info['quoteVolume']:,.0f}")

    # 6. الشارت التفاعلي (Candlesticks)
    fig = go.Figure(data=[go.Candlestick(
        x=df['ts'], open=df['open'], high=df['high'],
        low=df['low'], close=df['close'],
        increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b'
    )])
    
    fig.add_trace(go.Scatter(x=df['ts'], y=df['EMA_20'], name='خط الاتجاه (EMA 20)', line=dict(color='orange', width=1.5)))
    
    fig.update_layout(template='plotly_dark', height=500, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("فشل في جلب البيانات.. تأكد من اتصال الإنترنت!")

st.caption("تم التطوير بواسطة أمين - محلل الكريبتو الذكي 2026")
