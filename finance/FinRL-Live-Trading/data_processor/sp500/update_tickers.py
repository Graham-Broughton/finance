import os
from datetime import datetime

import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'


def get_table(filename):
    if os.path.isfile(filename):
        return pd.read_csv(filename, index_col='date')
    else:
        print("File not found.")


def get_data(filename):
    df = get_table(filename)
    df['tickers'] = df['tickers'].apply(lambda x: sorted(x.split(',')))

    # Replace SYMBOL-yyyymm with SYMBOL.
    df['tickers'] = [[ticker.split('-')[0] for ticker in tickers] for tickers in df['tickers']]

    # Add LIN after 2018-10-31
    df.loc[df.index > '2018-10-31', 'tickers'].apply(lambda x: x.append('LIN'))

    # Remove duplicates in each row.
    df['tickers'] = [sorted(list(set(tickers))) for tickers in df['tickers']]
    return df


def apply_changes(filename, df):
    changes = get_table(filename)
    # Convert ticker column from csv to list, then sort.
    changes['add'] = changes['add'].apply(lambda x: sorted(x.split(',')))
    changes['remove'] = changes['remove'].apply(lambda x: sorted(x.split(',')))

    # Copy the last row in dataframe, modify for changes, then append.
    for change in changes.itertuples():

        new_row = df.tail(1)

        tickers = list(new_row['tickers'][0])
        tickers += change.add
        tickers = list(set(tickers) - set(change.remove))
        tickers = sorted(tickers)

        d = {'date':change.Index, 'tickers':[tickers]}
        new_entry = pd.DataFrame(d)
        new_entry.set_index('date', inplace=True)
        df = pd.concat([df, new_entry])
    return df


def get_diff(filename, df):
    # compare last row to current S&P500 list
    current = pd.read_csv(filename)
    current = list(current['Symbol'])
    last_entry = list(df['tickers'][-1])

    diff = list(set(current) - set(last_entry)) + list(set(last_entry) - set(current))
    df['tickers'] = df['tickers'].apply(lambda x: ",".join(x))
    return df, diff


def save(df):
    now = datetime.now()
    dt_string = now.strftime('%m-%d-%Y')  # mm-dd-YYYY
    filename = f'S&P 500 Historical Components & Changes({dt_string}).csv'
    df.to_csv(filename)


def main(prefix='sp500/'):
    df = get_data(prefix + 'S&P 500 Historical Components & Changes.csv')
    df = apply_changes(prefix + 'sp500_changes_since_2019.csv', df)
    df, diff = get_diff(prefix + 'sp500.csv', df)
    print(diff)
    save(df)
    return df


if __name__ == '__main__':
    main()
