import numpy as np
import pandas as pd
from yahoodownloader import YahooDownloader


def download_yahoo(start, end, tickers, interval):
    yp = YahooDownloader()
    data = yp.download(start, end, tickers, interval)
    data = yp.clean_data(data)
