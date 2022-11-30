import numpy as np
import pandas as pd
import pytz
import yfinance as yf

class YahooDownloader:
    def __init__(self):
        pass

    def download(self, start_date: str, end_date: str, ticker_list: list, interval: str) -> pd.DataFrame:
        self.start = start_date
        self.end = end_date
        self.interval = interval

        data_df = pd.DataFrame()
        for ticker in ticker_list:
            tmp = yf.download(
                ticker,
                self.start_date,
                self.end_date,
                self.interval
            )
            tmp['ticker'] = ticker
            data_df = data_df.append(tmp)

        data_df.reset_index(inplace=True)
        try:
            # convert the column names to standardized names
            data_df.columns = [
                "date",
                "open",
                "high",
                "low",
                "close",
                "adjcp",
                "volume",
                "tic",
            ]
            # use adjusted close price instead of close price
            data_df["close"] = data_df["adjcp"]
            # drop the adjusted close price column
            data_df = data_df.drop(labels="adjcp", axis=1)
        except NotImplementedError:
            print("the features are not supported currently")
        # create day of the week column (monday = 0)
        data_df["day"] = data_df["date"].dt.dayofweek
        # convert date to standard string format, easy to filter
        data_df["date"] = data_df.date.apply(lambda x: x.strftime("%Y-%m-%d"))
        # drop missing data
        data_df = data_df.dropna()
        data_df = data_df.reset_index(drop=True)
        print("Shape of DataFrame: ", data_df.shape)
        # print("Display DataFrame: ", data_df.head())

        data_df = data_df.sort_values(by=["date", "tic"]).reset_index(drop=True)

        return data_df
