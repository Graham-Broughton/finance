from bs4 import BeautifulSoup as bs4
from ib_insync import *
# util.startloop()

ib = IB()
# ib.connect('127.0.0.1', 7046, clientId=1) # use for IB Gateway
ib.connect('127.0.0.1', 7497, clientId=1)  # use for TWS

stock = Stock('AMD', 'SMART', 'USD')

# types of reports:
# 'ReportsFinSummary': Financial summary
# 'ReportsOwnership': Company's ownership
# 'ReportSnapshot': Company's financial overview
# 'ReportsFinStatements': Financial Statements
# 'RESC': Analyst Estimates
# 'CalendarReport': Company's calendar

fundamentals = ib.reqFundamentalData(stock, 'ReportSnapshot')
# print(fundamentals)
content = bs4(fundamentals, 'xml')
#print(content)
ratios = content.find_all('Ratio')

for ratio in ratios:
    print(ratio['FieldName'])
    print(ratio.text)
