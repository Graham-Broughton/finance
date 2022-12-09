# import numpy as np
# import pandas as pd
from yahoodownloader import YahooDownloader
# from pcr import get_df


class ProcessData:
    def __init__(self, **kwargs):
        """
        Initializes the downloader.
        """
        self.stock_processor = YahooDownloader()

    def download_data(self, ticker_list, start_date, end_date, interval):
        """
        Download data from the stock processor.

        Args:
            ticker_list: list of stock tickers
            start_date: starting date
            end_date: ending date
            interval: interval to trade on
        """
        df = self.stock_processor.download(
            start_date, end_date, ticker_list, interval
        )
        return df

    def clean_data(self, df):
        """
        Clean dataframe.

        Args:
            df: stock dataframe
        """
        return self.stock_processor.clean_data(df)

    def add_indicators(self, df, indicators):
        """
        Add indicators to dataframe.

        Args:
            df: stock dataframe
            indicators: list of technical indicators
        """
        self.indicator_list = indicators
        return self.stock_processor.add_indicators(df, indicators)

    # def add_turbulence(self, df):
