import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta


# @st.cache
def fetch_coin_price(coingecko_token_id):
    return [
        (datetime.fromtimestamp(int(str(timestamp)[:-3])), price)
        for timestamp, price in requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coingecko_token_id}/market_chart?vs_currency=usd&days=30"
        )
        .json()
        .get("prices")
    ]


# fetch prices
solana_usd_prices = fetch_coin_price("solana")
gst_usd_prices = fetch_coin_price("green-satoshi-token") 

# normalize length
min_length = min(len(solana_usd_prices), len(gst_usd_prices))
solana_usd_prices = solana_usd_prices[-min_length:]
gst_usd_prices = gst_usd_prices[-min_length:]

# calculte 1 gst in sol
gst_sol_prices = [
    (ts, gst_price / solana_price)
    for (ts, gst_price), (_, solana_price) in zip(gst_usd_prices, solana_usd_prices)
]

gst_sol_price_df = pd.DataFrame(gst_sol_prices, index=None, columns=["date", "price"])


# draw title
st.write("""
# GST - SOL
a simple web application that shows the rate of green-satoshi-token in solana using coingecko api
""")

st.write("current price is", list(gst_sol_price_df.price)[-1], "at", list(gst_sol_price_df.date)[-1])

# draw plot
fig = go.Figure([go.Scatter(x=gst_sol_price_df.date, y=gst_sol_price_df.price)])
st.write(fig)
