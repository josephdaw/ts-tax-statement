# %% Import Packages
# Import native packages
import os
import datetime as dt

# Import 3rd party packages
from dotenv import load_dotenv
import pandas as pd

# Import my local files
from tradestationFunctions import importOrders
from exchangeRateLookup import importRatesFromRBA

#%% Load environmental variables
load_dotenv()

ACCOUNT_NUMBER = os.environ.get("ACCOUNT_NUMBER")

# Set the start and end dates for the report in the format yyyy,mm,dd
startDate = dt.datetime(2022, 7, 1)
endDate = dt.datetime(2023, 7, 1)

#%% Scrape Tradestation for trade list
print('webscrape for TS Trades...')
# note: dates are in format mm/dd/yyyy
dfTrades = importOrders(startDate.strftime('%m/%d/%Y'),endDate.strftime('%m/%d/%Y'), ACCOUNT_NUMBER)

#%% Save trades to csv
print('...done\nscrape tradestation website for orders...')
dfTrades.to_csv('dfTrades.csv')

#%% Format Trades
#Turn pandas warnings off - this is not advisable but necessary for the moment
pd.set_option('mode.chained_assignment', None)
df= dfTrades[['Date','Symbol','Side','Qty','Price','Comm','Other Fees','Net Amt']]
df['Date']= pd.to_datetime(dfTrades['Date'])

df.rename({'Other Fees':'Fees','Net Amt':'netPnl'}, axis=1, inplace=True)
df.sort_values(by=['Date','Symbol'], ascending=[True,True], inplace=True)
df.reset_index(drop=True,inplace=True)

#%% Import and concat RBA AUD Daily Rates
# Call the function to import the RBA rates
audusd = importRatesFromRBA(startDate, endDate)

#%% Join AUDUSD xRates to the df
# Join audusd and df, but drop any rows where Symbol is NAN - ie there is an entry for AUDUSD but there was no trade on the day
df2 = df.merge(audusd, on='Date',how='left')

# Forward fill the AUDUSD values so that multiple trades on the same day will have the same value for AUDUSD and drop un-neccessary columns
df2 = df2.ffill().dropna()

# Calculate all trades in AUDUSD
df2['netPnlAud'] = round( df2.netPnl / df2.audusd, 3)

# Tally up 
df2.loc['Total','buyTrades_AUD']= df2[df2.Side=='Buy'].netPnlAud.sum()
df2.loc['Total','sellTrades_AUD']= df2[df2.Side=='Sell'].netPnlAud.sum()
df2.loc['Total','shortTrades_AUD']= df2[df2.Side=='Short'].netPnlAud.sum()
df2.loc['Total','coverTrades_AUD']= df2[df2.Side=='Cover'].netPnlAud.sum()

df2.loc['Total','PnL_AUD']= df2['netPnlAud'].sum()

# Send to csv
df2.to_excel('TradeStation_EOFY_Report.xlsx')