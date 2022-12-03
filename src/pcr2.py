import threading
import concurrent.futures
import time
import datetime
from collections import defaultdict
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np
from selenium import webdriver

def driversetup():
    options = webdriver.ChromeOptions()
    #run Selenium in headless mode
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    #overcome limited resource problems
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("lang=en")
    #open Browser in maximized mode
    options.add_argument("start-maximized")
    #disable infobars
    options.add_argument("disable-infobars")
    #disable extension
    options.add_argument("--disable-extensions")
    options.add_argument("--incognito")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
    return driver

def pagesource(url, driver):
    driver = driver
    driver.get(url)
    soup = BeautifulSoup(driver.page_source)
    driver.close()
    return soup

def get_info(date):
    url = 'https://markets.cboe.com/us/options/market_statistics/daily/?mkt=cone&dt=%s'
    datestr = date.strftime("%Y-%m-%d")
    print(f"Retrieving {datestr} for URL")
    driver = driversetup()
    page = pagesource(url%datestr, driver)
    try:
        pcr = page.find_all('td')[7].get_text()
    except IndexError:
        pcr = np.nan
    return datestr, pcr

def get_df(path):
    new_df = pd.read_csv(path+'csvs/pcr.csv', parse_dates=['date'])
    start_date = new_df.tail(1)['date'].tolist()[0].date() + datetime.timedelta(days=1)
    end_date = datetime.date.today() - datetime.timedelta(days=1)
    drange = pd.date_range(start_date, end_date, freq='B')
    print(f'Date range is {drange}')
    max_workers = len(drange)
    ddict = defaultdict(list)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(get_info, date): date for date in drange}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                ddict['date'].append(url)
                ddict['PCR'].append(data[1])

    df = pd.DataFrame.from_dict(ddict).sort_values('date')
    new_df = new_df.append(df, ignore_index=True)
    return new_df

if __name__ == "__main__":
    path = 'drive/MyDrive/finance/'
    df = get_df(path)
    df.to_csv(path + 'csvs/pcr.csv')