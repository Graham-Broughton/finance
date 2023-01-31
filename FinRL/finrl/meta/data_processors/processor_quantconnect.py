from __future__ import annotations

import numpy as np


class QuantConnectEngineer:
    def __init__(self):
        """
        Initialize the class with the default values.

        Args:
            self: write your description
        """
        pass

    def data_fetch(start_time, end_time, stock_list, resolution=Resolution.Daily):
        """
        Fetch historical data from QuantBook.

        Args:
            start_time: write your description
            end_time: write your description
            stock_list: write your description
            resolution: write your description
            Resolution: write your description
            Daily: write your description
        """
        # resolution: Daily, Hour, Minute, Second
        qb = QuantBook()
        for stock in stock_list:
            qb.AddEquity(stock)
        history = qb.History(qb.Securities.Keys, start_time, end_time, resolution)
        return history

    def preprocess(df, stock_list):
        """
        This function will convert the DataFrame df into a structured array of arrays.

        Args:
            df: write your description
            stock_list: write your description
        """
        df = df[["open", "high", "low", "close", "volume"]]
        if_first_time = True
        for stock in stock_list:
            if if_first_time:
                ary = df.loc[stock].values
                if_first_time = False
            else:
                temp = df.loc[stock].values
                ary = np.hstack((ary, temp))
        return ary
