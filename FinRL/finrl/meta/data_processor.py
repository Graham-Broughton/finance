from __future__ import annotations

import numpy as np
import pandas as pd

from finrl.meta.data_processors.processor_alpaca import AlpacaProcessor as Alpaca
from finrl.meta.data_processors.processor_wrds import WrdsProcessor as Wrds
from finrl.meta.data_processors.processor_yahoofinance import (
    YahooFinanceProcessor as YahooFinance,
)


class DataProcessor:
    def __init__(self, data_source, **kwargs):
        """
        Initialize the processor

        Args:
            self: write your description
            data_source: write your description
        """
        if data_source == "alpaca":

            try:
                API_KEY = kwargs.get("API_KEY")
                API_SECRET = kwargs.get("API_SECRET")
                API_BASE_URL = kwargs.get("API_BASE_URL")
                self.processor = Alpaca(API_KEY, API_SECRET, API_BASE_URL)
                print("Alpaca successfully connected")
            except BaseException:
                raise ValueError("Please input correct account info for alpaca!")

        elif data_source == "wrds":
            self.processor = Wrds()

        elif data_source == "yahoofinance":
            self.processor = YahooFinance()

        else:
            raise ValueError("Data source input is NOT supported yet.")

    def download_data(
        self, ticker_list, start_date, end_date, time_interval
    ) -> pd.DataFrame:
        """
        Download data from the data processor.

        Args:
            self: write your description
            ticker_list: write your description
            start_date: write your description
            end_date: write your description
            time_interval: write your description
        """
        df = self.processor.download_data(
            ticker_list=ticker_list,
            start_date=start_date,
            end_date=end_date,
            time_interval=time_interval,
        )
        return df

    def clean_data(self, df) -> pd.DataFrame:
        """
        Clean data from old format to new format.

        Args:
            self: write your description
            df: write your description
        """
        df = self.processor.clean_data(df)

        return df

    def add_technical_indicator(self, df, tech_indicator_list) -> pd.DataFrame:
        """
        Add technical indicator to dataframe.

        Args:
            self: write your description
            df: write your description
            tech_indicator_list: write your description
        """
        self.tech_indicator_list = tech_indicator_list
        df = self.processor.add_technical_indicator(df, tech_indicator_list)

        return df

    def add_turbulence(self, df) -> pd.DataFrame:
        """
        Add turbulence to a dataframe.

        Args:
            self: write your description
            df: write your description
        """
        df = self.processor.add_turbulence(df)

        return df

    def add_vix(self, df) -> pd.DataFrame:
        """
        Add a VIX DataFrame to the dataframe.

        Args:
            self: write your description
            df: write your description
        """
        df = self.processor.add_vix(df)

        return df

    def df_to_array(self, df, if_vix) -> np.array:
        """
        Convert a DataFrame to a numpy array.

        Args:
            self: write your description
            df: write your description
            if_vix: write your description
        """
        price_array, tech_array, turbulence_array = self.processor.df_to_array(
            df, self.tech_indicator_list, if_vix
        )
        # fill nan and inf values with 0 for technical indicators
        tech_nan_positions = np.isnan(tech_array)
        tech_array[tech_nan_positions] = 0
        tech_inf_positions = np.isinf(tech_array)
        tech_array[tech_inf_positions] = 0

        return price_array, tech_array, turbulence_array
