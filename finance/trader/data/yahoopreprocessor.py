import pandas as pd
import polars as pl
import yfinance as yf


class YahooDownloader:
    def __init__(self, start_date: str, end_date: str, ticker_list: list):
        """
        Initialize the date range

        Args:
            start_date: starting date
            end_date: ending date
            ticker_list: list of stock tickers
        """
        self.start_date = start_date
        self.end_date = end_date
        self.ticker_list = ticker_list

    def fetch_data(self, proxy=None):
        """
        Fetch the latest data from Yahoo Finance and return it as a pandas DataFrame.

        Args:
            proxy: proxy to download from
        """
        # Download and save the data in a pandas DataFrame:
        data_df = pd.DataFrame()
        for tic in self.ticker_list:
            temp_df = yf.download(
                tic, start=self.start_date, end=self.end_date, proxy=proxy
            )
            temp_df['tic'] = tic
            data_df = data_df.append(temp_df)
        # reset the index, we want to use numbers as index instead of dates
        data_df = data_df.reset_index()
        try:
            # convert the column names to standardized names
            data_df.columns = [
                'date',
                'open',
                'high',
                'low',
                'close',
                'adjcp',
                'volume',
                'tic',
            ]
            # use adjusted close price instead of close price
            data_df['close'] = data_df['adjcp']
            # drop the adjusted close price column
            data_df = data_df.drop(labels='adjcp', axis=1)
        except NotImplementedError:
            print('the features are not supported currently')
        # create day of the week column (monday = 0)
        data_df['day'] = data_df['date'].dt.dayofweek
        # convert date to standard string format, easy to filter
        data_df['date'] = data_df.date.apply(lambda x: x.strftime('%Y-%m-%d'))
        # drop missing data
        data_df = data_df.dropna()
        data_df = data_df.reset_index(drop=True)
        print('Shape of DataFrame: ', data_df.shape)
        # print("Display DataFrame: ", data_df.head())

        data_df = data_df.sort_values(by=['date', 'tic']).reset_index(drop=True)
        return data_df

    def select_equal_rows_stock(self, df):
        """
        Select only rows with equal counts that have a stock value greater than the mean value.

        Args:
            df: stock dataframe
        """
        df_check = df.tic.value_counts()
        df_check = pd.DataFrame(df_check).reset_index()
        df_check.columns = ['tic', 'counts']
        mean_df = df_check.counts.mean()
        equal_list = list(df.tic.value_counts() >= mean_df)
        names = df.tic.value_counts().index
        select_stocks_list = list(names[equal_list])
        df = df[df.tic.isin(select_stocks_list)]
        return df