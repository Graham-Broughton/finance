# import numpy as np
# import pandas as pd
from yahoodownloader import YahooDownloader
# from pcr import get_df


class ProcessData:
    def __init__(self, **kwargs):
        self.stock_processor = YahooDownloader()

    def download_data(self, ticker_list, start_date, end_date, interval):
        df = self.stock_processor.download(
            start_date, end_date, ticker_list, interval
        )
        return df

    def clean_data(self, df):
        return self.stock_processor.clean_data(df)

    def add_indicators(self, df, indicators):
        self.indicator_list = indicators
        return self.stock_processor.add_indicators(df, indicators)

    # def add_turbulence(self, df):
