import streamlit as st
import ccxt
import pandas as pd
import ta
from streamlit_autorefresh import st_autorefresh

# 1. Page Config (Must be first)
st.set_page_config(page_title="Crypto Analysis Tool", layout="wide")

# 2. Real-time Refresh (1 second)
st_autorefresh(interval=1000, key="price_update_timer")

st.title("Crypto Technical Radar")
st.markdown("---")

# 3. Cached Data Fetching
@st.cache_data(ttl=60)
def fetch_crypto_data(symbol):
    try:
        exchange = ccxt.kucoin()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        # Calculations inside cache for performance
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        df['SMA_20'] = ta.trend.sma_indicator(df['close'], window=20)
        return df
    except:
        return None

# 4. Symbols and Display
symbols = ['BTC/USDT', 'SOL/USDT', 'SUI/USDT', 'ANKR/USDT']

for symbol in symbols:
    # Placeholder to prevent flickering
    placeholder = st.empty()
    df = fetch_crypto_data(symbol)
    
    if df is not None:
        last_price = df['close'].iloc[-1]
        last_rsi = df['RSI'].iloc[-1]
        
        with placeholder.container():
            col1, col2, col3 = st.columns(3)
            col1.metric(f"Symbol: {symbol}", f"${last_price:,.4f}")
            col2.metric("RSI (14)", f"{last_rsi:.2f}")
            
            if last_rsi > 70:
                col3.error("SIGNAL: OVERBOUGHT")
            elif last_rsi < 30:
                col3.success("SIGNAL: OVERSOLD")
            else:
                col3.info("SIGNAL: NEUTRAL")
                
            st.dataframe(df.tail(3), use_container_width=True)
            st.markdown("---")

st.caption("Data provided by kucoin via CCXT library.")
