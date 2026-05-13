import streamlit as st
import ccxt
import pandas as pd
import ta
from streamlit_autorefresh import st_autorefresh

# This will refresh the app every 1 second (1000 milliseconds)
st_autorefresh(interval=1000, key="price_update_timer")
# Page Configuration
st.set_page_config(page_title="Crypto Analysis Tool", layout="wide")

st.title("Crypto Technical Radar")
st.markdown("---")

# Symbols to track
symbols = ['BTC/USDT', 'SOL/USDT', 'SUI/USDT', 'ANKR/USDT']

def fetch_crypto_data(symbol):
    try:
        exchange = ccxt.kucoin()
        # Fetch 100 hourly candles
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Error fetching {symbol}: {str(e)}")
        return None

# Display logic
for symbol in symbols:
    df = fetch_crypto_data(symbol)
    
    if df is not None:
        # Technical Indicators calculation
        df['RSI'] = ta.momentum.rsi(df['close'], window=14)
        df['SMA_20'] = ta.trend.sma_indicator(df['close'], window=20)
        
        last_price = df['close'].iloc[-1]
        last_rsi = df['RSI'].iloc[-1]
        
        # Display Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric(f"Symbol: {symbol}", f"${last_price:,.4f}")
        col2.metric("RSI (14)", f"{last_rsi:.2f}")
        
        # Signal Logic
        if last_rsi > 70:
            col3.error("SIGNAL: OVERBOUGHT")
        elif last_rsi < 30:
            col3.success("SIGNAL: OVERSOLD")
        else:
            col3.info("SIGNAL: NEUTRAL")
            
        st.dataframe(df.tail(5), use_container_width=True)
        st.markdown("---")

st.caption("Data provided by kucoin via CCXT library.")
