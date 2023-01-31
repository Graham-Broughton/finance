from ib_insync import *
# util.startloop()

ib = IB()
# ib.connect('127.0.0.1', 7046, clientId=1) # use for IB Gateway
ib.connect('127.0.0.1', 7497, clientId=1)  # use for TWS

stock = Stock('AMD', 'SMART', 'USD')

order = LimitOrder('BUY', 5, 64.00)

trade = ib.placeOrder(stock, order)
print(trade)

def orderFilled(trade, fill):
    print(f"Order: {order}")
    print('Order filled: ', fill)

trade.fillEvent += orderFilled
ib.run()
