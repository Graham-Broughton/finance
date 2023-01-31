from ib_insync import *
# util.startloop()

ib = IB()
# ib.connect('127.0.0.1', 7046, clientId=1) # use for IB Gateway
ib.connect('127.0.0.1', 7497, clientId=1)  # use for TWS

# subscription = ScannerSubscription(
#     instrument='STK',
#     locationCode='STK.US.MAJOR',
#     scanCode='SCAN_currYrETFFYDividendYield_DESC')

# scan_data = ib.reqScannerData(subscription)

# for scan in scan_data:
#     #print(scan)
#     print(scan.contractDetails.contract.symbol)

allParams = ib.reqScannerParameters()
print(allParams)
