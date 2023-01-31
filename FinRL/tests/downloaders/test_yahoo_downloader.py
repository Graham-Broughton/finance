from __future__ import annotations

import pandas as pd
import pytest

from finrl.meta.preprocessor.yahoodownloader import YahooDownloader


@pytest.fixture(scope="session")
def ticker_list():
    """
    List of tickers.

    Args:
    """
    return ["AAPL", "GOOG"]


def test_download(ticker_list):
    """
    Test that the download function works.

    Args:
        ticker_list: write your description
    """
    df = YahooDownloader(
        start_date="2019-01-01", end_date="2019-02-01", ticker_list=ticker_list
    ).fetch_data()
    assert isinstance(df, pd.DataFrame)
