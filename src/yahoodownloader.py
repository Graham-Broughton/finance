import numpy as np
import pandas as pd
import yfinance as yf
import exchange_calendars as tc
from stockstats import StockDataFrame as Sdf


class YahooDownloader:
    def __init__(self):
        pass

    def download(
        self, start_date: str, end_date: str, ticker_list: list, interval: str
    ):
        self.start = start_date
        self.end = end_date
        self.interval = interval

        data = pd.DataFrame()
        for ticker in ticker_list:
            tmp = yf.download(
                ticker,
                self.start_date,
                self.end_date,
                self.interval
            )
            tmp['tic'] = ticker
            data = data.append(tmp)
        data.reset_index(inplace=True)
        columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'tic']
        data = data.loc[:, data.columns.isin(columns)]
        # convert the column names to standardized names
        data.columns = [
            "date",
            "open",
            "high",
            "low",
            "close",
            "adjcp",
            "volume",
            "tic",
        ]
        # create day of the week column (monday = 0)
        data["day"] = data["date"].dt.dayofweek
        # convert date to standard string format, easy to filter
        data["date"] = data.date.apply(lambda x: x.strftime("%Y-%m-%d"))
        # drop missing data
        data = data.dropna()
        data = data.reset_index(drop=True)
        print("Shape of DataFrame: ", data.shape)
        data = data.sort_values(by=["date", "tic"]).reset_index(drop=True)
        return data

    def get_trading_days(
        self, start_date: str, end_date: str
    ):
        nyse = tc.get_calender('NYSE')
        df = nyse.sessions_in_range(
            pd.Timestamp(start_date),
            pd.Timestamp(end_date),
        )
        trading_days = df.strftime('%Y-%m-%d').to_list()
        return trading_days

    def clean_data(
        self, data: pd.DataFrame
    ):
        df = data.copy()
        df = df.rename({'date': 'time'}, axis=1)
        time_interval = self.interval
        tickers = df['tic'].unique().values

        # get time index
        trading_days = self.get_trading_days(self.start, self.end)
        if time_interval == '1D':
            times = trading_days
        elif time_interval == '1m':
            # Define and add NY's offset from UST and fill it in with minutes
            NY = "America/New_York"
            delta = np.timedelta64(9, 'h') + np.timedelta64(30, 'm')
            newdt = np.array(trading_days, dtype='datetime64') + delta
            dt = np.array([np.arange(
                day, (day + np.timedelta64(390, 'm')),
                dtype='datetime64') for day in newdt]
            )
            df = pd.to_datetime(dt).reshape(-1, 1).tz_localize(NY)
            times = df.to_list()
        else:
            raise ValueError("The given Interval is not supported")

        # Fill nan values
        new_df = pd.DataFrame()
        for tic in tickers:
            print(("Clean data for ") + tic)
            # Create empty df using the times as index
            tmp_df = pd.DataFrame(
                columns=['open', 'high', 'low', 'close', 'adjclose', 'volume'],
                index=times
            )
            tic_df = df[df['tic'] == tic]
            for i in range(tic_df.shape[0]):
                tmp_df.loc[tic_df.iloc[i]['time']] = tic_df.iloc[i][
                    ['open', 'high', 'low', 'close', 'adjclose', 'volume']
                ]

            if str(tmp_df.iloc[0]['close']) == 'nan':
                print("NaN data on start date, fill using first valid data.")
                for i in range(tmp_df.shape[0]):
                    if str(tmp_df.iloc[i]["close"]) != "nan":
                        first_valid_close = tmp_df.iloc[i]["close"]
                        first_valid_adjclose = tmp_df.iloc[i]["adjcp"]
                    break

                tmp_df.iloc[0] = [
                    first_valid_close,
                    first_valid_close,
                    first_valid_close,
                    first_valid_close,
                    first_valid_adjclose,
                    0.0,
                ]

            # fill NaN data with previous close and set volume to 0.
            # for i in range(tmp_df.shape[0]):
            #     if str(tmp_df.iloc[i]["close"]) == "nan":
            #         previous_close = tmp_df.iloc[i - 1]["close"]
            #         previous_adjcp = tmp_df.iloc[i - 1]["adjcp"]
            #         if str(previous_close) == "nan":
            #             raise ValueError
            #         tmp_df.iloc[i] = [
            #             previous_close,
            #             previous_close,
            #             previous_close,
            #             previous_close,
            #             previous_adjcp,
            #             0.0,
            #         ]
            nan_df = tmp_df[tmp_df['close'] == 'nan'].index
            tmp_df.loc[nan_df, 'volume'] = 0.0
            tmp_df = tmp_df.replace('nan', method='ffill')

            # merge single ticker data to new DataFrame
            tmp_df = tmp_df.astype(float)
            tmp_df["tic"] = tic
            new_df = new_df.append(tmp_df)
            print(("Data clean for ") + tic + (" is finished."))

        # reset index and rename columns
        new_df = new_df.reset_index()
        new_df = new_df.rename(columns={"index": "time"})
        print("Data clean all finished!")
        return new_df

    def add_technical_indicator(self, data, tech_indicator_list):
        """
        calculate technical indicators
        use stockstats package to add technical inidactors
        :param data: (df) pandas dataframe
        :return: (df) pandas dataframe
        """
        df = data.copy()
        df = df.sort_values(by=["tic", "time"])
        stock = Sdf.retype(df.copy())
        unique_ticker = stock.tic.unique()

        for indicator in tech_indicator_list:
            indicator_df = pd.DataFrame()
            for i in range(len(unique_ticker)):
                try:
                    temp_indicator = stock[stock.tic == unique_ticker[i]][indicator]
                    temp_indicator = pd.DataFrame(temp_indicator)
                    temp_indicator["tic"] = unique_ticker[i]
                    temp_indicator["time"] = df[df.tic == unique_ticker[i]][
                        "time"
                    ].to_list()
                    indicator_df = indicator_df.append(
                        temp_indicator, ignore_index=True
                    )
                except Exception as e:
                    print(e)
            df = df.merge(
                indicator_df[["tic", "time", indicator]], on=["tic", "time"], how="left"
            )
        df = df.sort_values(by=["time", "tic"])
        return df

    def add_turbulence(self, data):
        """
        add turbulence index from a precalcualted dataframe
        :param data: (df) pandas dataframe
        :return: (df) pandas dataframe
        """
        df = data.copy()
        turbulence_index = self.calculate_turbulence(df)
        df = df.merge(turbulence_index, on="time")
        df = df.sort_values(["time", "tic"]).reset_index(drop=True)
        return df

    def calculate_turbulence(self, data, time_period=252):
        """calculate turbulence index based on dow 30"""
        # can add other market assets
        df = data.copy()
        df_price_pivot = df.pivot(index="time", columns="tic", values="close")
        # use returns to calculate turbulence
        df_price_pivot = df_price_pivot.pct_change()

        unique_date = df.date.unique()
        # start after a year
        start = time_period
        turbulence_index = [0] * start
        count = 0
        for i in range(start, len(unique_date)):
            current_price = df_price_pivot[df_price_pivot.index == unique_date[i]]
            # use one year rolling window to calcualte covariance
            hist_price = df_price_pivot[
                (df_price_pivot.index < unique_date[i])
                & (df_price_pivot.index >= unique_date[i - time_period])
            ]
            # Drop tickers which has number missing values more than the "oldest" ticker
            filtered_hist_price = hist_price.iloc[
                hist_price.isna().sum().min():
            ].dropna(axis=1)

            cov_temp = filtered_hist_price.cov()
            current_temp = current_price[
                [x for x in filtered_hist_price]
                ] - np.mean(filtered_hist_price, axis=0)
            temp = current_temp.values.dot(np.linalg.pinv(cov_temp)).dot(
                current_temp.values.T
            )
            if temp > 0:
                count += 1
                if count > 2:
                    turbulence_temp = temp[0][0]
                else:
                    # avoid large outlier because of the calculation just begins
                    turbulence_temp = 0
            else:
                turbulence_temp = 0
            turbulence_index.append(turbulence_temp)

        turbulence_index = pd.DataFrame(
            {"time": df_price_pivot.index, "turbulence": turbulence_index}
        )
        return turbulence_index

    def add_vix(self, data):
        """
        add vix from yahoo finance
        :param data: (df) pandas dataframe
        :return: (df) pandas dataframe
        """
        df = data.copy()
        df_vix = self.download_data(
            start_date=df.time.min(),
            end_date=df.time.max(),
            ticker_list=["^VIX"],
            time_interval=self.time_interval,
        )
        df_vix = self.clean_data(df_vix)
        vix = df_vix[["time", "adjcp"]]
        vix.columns = ["time", "vix"]

        df = df.merge(vix, on="time")
        df = df.sort_values(["time", "tic"]).reset_index(drop=True)
        return df

    def df_to_array(
        self, df: pd.DataFrame, tech_indicator_list: list, if_vix: bool
    ):
        """transform final df to numpy arrays"""
        unique_ticker = df.tic.unique()
        print(unique_ticker)
        if_first_time = True
        for tic in unique_ticker:
            if if_first_time:
                price_array = df[df.tic == tic][["adjcp"]].values
                tech_array = df[df.tic == tic][tech_indicator_list].values
                if if_vix:
                    turbulence_array = df[df.tic == tic]["vix"].values
                else:
                    turbulence_array = df[df.tic == tic]["turbulence"].values
                if_first_time = False
            else:
                price_array = np.hstack(
                    [price_array, df[df.tic == tic][["adjcp"]].values]
                )
                tech_array = np.hstack(
                    [tech_array, df[df.tic == tic][tech_indicator_list].values]
                )
        assert price_array.shape[0] == tech_array.shape[0]
        assert tech_array.shape[0] == turbulence_array.shape[0]
        print("Successfully transformed into array")
        return price_array, tech_array, turbulence_array
