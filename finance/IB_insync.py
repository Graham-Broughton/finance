import ib_insync
# util.startloop()

ib = ib_insync.IB()
# ib.connect('127.0.0.1', 7046, clientId=1) # use for IB Gateway
ib.connect('127.0.0.1', 7497, clientId=1)  # use for TWS

stock = ib_insync.Stock('AAPL', 'SMART', 'USD')
# contract = Forex('EURUSD')
# bars = ib.reqHistoricalData(
#     contract, endDateTime='', durationStr='30 D',
#     barSizeSetting='1 hour', whatToShow='MIDPOINT', useRTH=True)

# df = util.df(bars)
# print(df)


def onPendingTickers(tickers):
    print("Ticker received")
    print(tickers)


market_data = ib.reqMktData(stock, '', False, False)

ib.pendingTickersEvent += onPendingTickers
ib.run()
