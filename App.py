import streamlit as st
import ccxt
import pandas as pd
import ta
from streamlit_autorefresh import st_autorefresh

# 1. Page Config & Professional Theme
st.set_page_config(page_title="Amin Crypto Hub", layout="wide")

# 2. Sidebar for Navigation (Choose your coin)
st.sidebar.title("🚀 Control Center")
selected_coin = st.sidebar.selectbox(
    "Select Asset:",
    ['BTC/USDT', 'SUI/USDT', 'SOL/USDT', 'ANKR/USDT', 'ETH/USDT']
)

# 3. Fast Refresh Timer (1 second)
st_autorefresh(interval=1000, key="price_refresh")

# 4. Cached Data Logic (Heavy fetching)
@st.cache_data(ttl=60)
def fetch_analysis(symbol):
    try:
        exchange = ccxt.kucoin()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        return df
    except:
        return None

# 5. Fast Price Logic (Instant)
def get_live_data(symbol):
    try:
        ticker = ccxt.kucoin().fetch_ticker(symbol)
        return ticker['last'], ticker['change'] # Current price and 24h change
    except:
        return None, None

# --- Application Layout ---
st.title(f"📊 Tracking: {selected_coin}")
st.markdown("---")

# Main Placeholder for the numbers (Stops the flickering from 13598.jpg)
header_placeholder = st.empty()

# Fetch Data
live_price, price_change = get_live_data(selected_coin)
analysis_df = fetch_analysis(selected_coin)

if live_price and analysis_df is not None:
    # Logic for Green/Red color based on 24h change
    price_color = "green" if price_change >= 0 else "red"
    last_rsi = analysis_df['RSI'].iloc[-1]

    with header_placeholder.container():
        # Displaying only the numbers that change
        c1, c2, c3 = st.columns(3)
        
        # Big Price Display with Color
        c1.markdown(f"### Current Price\n <h2 style='color:{price_color};'>${live_price:,.4f}</h2>", unsafe_allow_html=True)
        
        # RSI Display
        c2.metric("RSI (14)", f"{last_rsi:.2f}")
        
        # Signal Box
        if last_rsi > 70:
            c3.error("🔥 OVERBOUGHT")
        elif last_rsi < 30:
            c3.success("💎 OVERSOLD")
        else:
            c3.info("⚖️ NEUTRAL")

    # Static Section (History and Data) - No flickering here
    st.subheader("Market History (Last 5 Hours)")
    st.dataframe(analysis_df.tail(5), use_container_width=True)
    
    st.subheader("Price Trend")
    st.line_chart(analysis_df['close'].tail(30))

st.caption(f"Connected to KuCoin API. User: Amin")
