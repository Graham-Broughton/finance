# import numpy as np
# import pandas as pd
from yahoodownloader import YahooDownloader


class GetIndexes:
    def download_yahoo(start, end, tickers, interval):
        """
        Download Yahoo Finance data from the specified time range.

        Args:
            start: write your description
            end: write your description
            tickers: write your description
            interval: write your description
        """
        yp = YahooDownloader()
        data = yp.download(start, end, tickers, interval)
        data = yp.clean_data(data)
