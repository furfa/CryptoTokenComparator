from datetime import datetime
from typing import Any, Dict, Tuple, List

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

"""
Frontend names to coingecko api coin names
"""
TOKEN_NAMES = {"GST": "green-satoshi-token", "GMT": "stepn", "SOL": "solana"}
CURRENCY_NAMES = {
    "SOL": "solana",
    "USDT": "tether",
}


def get_key_by_val(d: Dict[Any, Any], val: Any):
    """
    Get dict key by value
    """
    for k, v in d.items():
        if v == val:
            return k


@st.cache(ttl=20 * 60)  # time to live 20 minutes
def fetch_coin_price(coingecko_token_id: str):
    """
    Fetch last month token price
    """
    return [
        (datetime.fromtimestamp(int(str(timestamp)[:-3])), price)
        for timestamp, price in requests.get(
            f"https://api.coingecko.com/api/v3/coins/{coingecko_token_id}/market_chart?vs_currency=usd&days=30"
        )
        .json()
        .get("prices")
    ]


def build_controls() -> Tuple[List[str], str]:
    """
    Left side bar
    """
    c1, c2 = st.sidebar.columns([1, 2])
    c1.image("./logo.svg")
    c2.title("StepN")
    st.sidebar.write("")  # padding
    selected_tokens = st.sidebar.multiselect(
        "Select token for tracking", TOKEN_NAMES.keys()
    )

    if not selected_tokens:
        st.sidebar.success("To continue select token 👆")

    currency_to_compare = st.sidebar.selectbox(
        "Select main сurrency", CURRENCY_NAMES.keys()
    )
    return list(map(lambda x: TOKEN_NAMES.get(x), selected_tokens)), CURRENCY_NAMES.get(
        currency_to_compare
    )


def build_main_layout(
    tokens: list[str],
    current_prices: List[Tuple[datetime, float]],
    main_currency: str,
    figure: go.Figure,
):
    """
    Main layout on center of the screen
    """
    if not tokens:
        # initial screen
        st.write(
            """
        # 👋 Hello
        """
        )
        st.write(
            """ 
        This application will help you compare StepN NFT tokens and more intelligently choose the time to sell and buy them.
        Interested?"""
        )

        st.write(
            """ 
        👈 Follow the instructions in the side menu.
        """
        )
        return

    for token, current_price in zip(tokens, current_prices):
        st.write(
            f"Current **{get_key_by_val(TOKEN_NAMES, token)}** price is",
            current_price[1],
            f"**{get_key_by_val(CURRENCY_NAMES, main_currency).lower()}** at",
            current_price[0],
        )

    # draw plot
    st.write(figure)


def main():
    tokens, main_currency = build_controls()

    scatters = []
    current_prices = []
    for token in tokens:
        # fetch prices
        main_prices = fetch_coin_price(main_currency)
        token_usd_prices = fetch_coin_price(token)

        # normalize length
        min_length = min(len(main_prices), len(token_usd_prices))
        main_prices = main_prices[-min_length:]
        token_usd_prices = token_usd_prices[-min_length:]

        # calculte 1 token price in main currency
        token_in_main_prices = [
            (ts, token_usd_prices / main_prices)
            for (ts, token_usd_prices), (_, main_prices) in zip(
                token_usd_prices, main_prices
            )
        ]

        token_in_main_price_df = pd.DataFrame(
            token_in_main_prices, index=None, columns=["date", "price"]
        )
        scatters.append(
            go.Scatter(
                x=token_in_main_price_df.date,
                y=token_in_main_price_df.price,
                name=get_key_by_val(TOKEN_NAMES, token),
            )
        )
        current_prices.append(token_in_main_price_df.values[-1])

    fig = go.Figure(scatters)

    build_main_layout(
        tokens=tokens,
        current_prices=current_prices,
        main_currency=main_currency,
        figure=fig,
    )


if __name__ == "__main__":
    main()
