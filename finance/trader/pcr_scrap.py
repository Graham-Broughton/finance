import datetime
import time
from collections import defaultdict

import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

def driversetup():
    options = webdriver.ChromeOptions()
    #run Selenium in headless mode
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    #overcome limited resource problems
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('lang=en')
    #open Browser in maximized mode
    options.add_argument('start-maximized')
    #disable infobars
    options.add_argument('disable-infobars')
    #disable extension
    options.add_argument('--disable-extensions')
    options.add_argument('--incognito')
    options.add_argument('--disable-blink-features=AutomationControlled')

    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")

    return driver

def pagesource(url, driver):
    driver = driver
    driver.get(url)
    soup = BeautifulSoup(driver.page_source)
    driver.close()
    return soup

def update(path):
    new_df = pd.read_csv(path+'csvs/pcr.csv', parse_dates=['date'])
    start_date = new_df.tail(1)['date'].tolist()[0].date() + datetime.timedelta(days=1)
    end_date = datetime.date.today() - datetime.timedelta(days=1)
    drange = pd.date_range(start_date, end_date, freq='B')
    print(f'Date range is {drange}')

    url = 'https://markets.cboe.com/us/options/market_statistics/daily/?mkt=cone&dt=%s'

    ddict = defaultdict(list)
    for date in drange:
        datestr = date.strftime('%Y-%m-%d')
        print(f'Retrieving {datestr} for URL')

        driver = driversetup()
        page = pagesource(url%datestr, driver)

        try:
            ddict['PCR'].append(page.find_all('td')[7].get_text())
        except IndexError:
            ddict['PCR'].append(np.nan)
        ddict['date'].append(date)

    df = pd.DataFrame.from_dict(ddict)
    new_df = new_df.append(df, ignore_index=True)
    new_df.to_csv(path+'csvs/pcr.csv', index=False)

if __name__ == '__main__':
    path = 'drive/MyDrive/finance/'
    update(path)
