# import numpy as np
# import pandas as pd
from yahoodownloader import YahooDownloader


class GetIndexes:
    def download_yahoo(self, start, end, tickers, interval):
        """
        Download Yahoo Finance data from the specified time range.

        Args:
            start: start date
            end: end date
            tickers: list of stock tickers
            interval: interval to trade on
        """
        yp = YahooDownloader()
        data = yp.download(start, end, tickers, interval)
        data = yp.clean_data(data)
