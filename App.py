import requests
import streamlit as st

@st.cache_data(ttl=3)
def get_binance_prices():
    url = "https://api.binance.com/api/v3/ticker/price"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=3)
        response.raise_for_status()
        data = response.json()

        return {item["symbol"]: float(item["price"]) for item in data}

    except:
        return None


def get_coingecko_fallback():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum,binancecoin",
        "vs_currencies": "usd"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        return response.json()
    except:
        return None


st.title("Crypto Live Prices")

data = get_binance_prices()

if data:
    st.success("Data source: Binance")

    st.write({
        "BTCUSDT": data.get("BTCUSDT"),
        "ETHUSDT": data.get("ETHUSDT"),
        "BNBUSDT": data.get("BNBUSDT"),
    })
else:
    st.warning("Binance unavailable, switching to fallback API")
    st.write(get_coingecko_fallback())
