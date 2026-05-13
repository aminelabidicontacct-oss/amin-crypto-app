import streamlit as st
import pandas as pd
import requests
import streamlit.components.v1 as components
import ta
import json

st.set_page_config(layout="wide")

st.title("🚀 Pro TradingView Dashboard")

symbol = st.text_input("Symbol", "BTC").upper()
timeframe = st.selectbox("Timeframe", ["minute", "hour", "day"])

# ======================
# FETCH DATA
# ======================
def fetch_data(symbol, tf):
    url = f"https://min-api.cryptocompare.com/data/v2/histo{tf}?fsym={symbol}&tsym=USD&limit=300"
    r = requests.get(url, timeout=10).json()

    if "Data" not in r:
        return None

    df = pd.DataFrame(r["Data"]["Data"])
    df["time"] = df["time"] * 1000

    df["RSI"] = ta.momentum.rsi(df["close"], window=14)
    df["EMA50"] = ta.trend.ema_indicator(df["close"], window=50)

    return df

df = fetch_data(symbol, timeframe)

if df is None:
    st.error("Error loading data")
    st.stop()

# ======================
# SAFE DATA
# ======================
candles = df[["time","open","high","low","close"]].dropna().values.tolist()

ema = df[["time","EMA50"]].dropna()
ema = [{"time": int(x[0]), "value": float(x[1])} for x in ema.values]

volume = df[["time","volumeto"]].dropna()
volume = [{"time": int(x[0]), "value": float(x[1]), "color": "#26a69a"} for x in volume.values]

rsi_series = df["RSI"].dropna()
rsi_last = float(rsi_series.iloc[-1]) if len(rsi_series) > 0 else 50

# ======================
# JS SAFE JSON
# ======================
candles_json = json.dumps(candles)
ema_json = json.dumps(ema)
volume_json = json.dumps(volume)

# ======================
# CHART
# ======================
html = f"""
<!DOCTYPE html>
<html>
<head>
<script src="https://unpkg.com/lightweight-charts/dist/lightweight-charts.standalone.production.js"></script>
</head>

<body style="margin:0;background:#0e1117;">

<div id="chart" style="height:700px;"></div>

<script>
const chart = LightweightCharts.createChart(document.getElementById('chart'), {{
    layout: {{
        background: {{ color: '#0e1117' }},
        textColor: '#ffffff'
    }},
    grid: {{
        vertLines: {{ color: '#1f2937' }},
        horzLines: {{ color: '#1f2937' }}
    }},
    width: window.innerWidth,
    height: 700
}});

// ================= CANDLES =================
const candles = chart.addCandlestickSeries();
candles.setData({candles_json});

// ================= EMA =================
const ema = chart.addLineSeries({{
    color: 'orange',
    lineWidth: 2
}});
ema.setData({ema_json});

// ================= VOLUME =================
const volume = chart.addHistogramSeries({{
    priceFormat: {{ type: 'volume' }},
    priceScaleId: 'volume'
}});
volume.setData({volume_json});

// ================= LEVEL =================
candles.createPriceLine({{
    price: {df['close'].iloc[-1]},
    color: 'red',
    lineWidth: 2,
    lineStyle: 2,
    axisLabelVisible: true,
    title: 'Price'
}});

</script>

</body>
</html>
"""

components.html(html, height=750)

# ======================
# RSI PANEL
# ======================
st.subheader("📊 RSI")

st.metric("RSI", f"{rsi_last:.2f}")

if rsi_last < 30:
    st.success("Oversold 🟢")
elif rsi_last > 70:
    st.error("Overbought 🔴")
else:
    st.info("Neutral ⚪")
