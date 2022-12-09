# import numpy as np
# import pandas as pd
from yahoodownloader import YahooDownloader
# from pcr import get_df


class ProcessData:
    def __init__(self, **kwargs):
        """
        Initializes the downloader.

        Args:
            self: write your description
        """
        self.stock_processor = YahooDownloader()

    def download_data(self, ticker_list, start_date, end_date, interval):
        """
        Download data from the stock processor.

        Args:
            self: write your description
            ticker_list: write your description
            start_date: write your description
            end_date: write your description
            interval: write your description
        """
        df = self.stock_processor.download(
            start_date, end_date, ticker_list, interval
        )
        return df

    def clean_data(self, df):
        """
        Clean dataframe.

        Args:
            self: write your description
            df: write your description
        """
        return self.stock_processor.clean_data(df)

    def add_indicators(self, df, indicators):
        """
        Add indicators to dataframe.

        Args:
            self: write your description
            df: write your description
            indicators: write your description
        """
        self.indicator_list = indicators
        return self.stock_processor.add_indicators(df, indicators)

    # def add_turbulence(self, df):
