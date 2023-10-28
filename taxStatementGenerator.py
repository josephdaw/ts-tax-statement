#%% Import Packages
#Import native packages
# import os
import os
import datetime as dt
import pandas as pd
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

import numpy as np
import pandas as pd
import datetime as dt    

# Import 3rd party packages

# Import my local files

load_dotenv()

ACCOUNT_NUMBER = os.environ.get("ACCOUNT_NUMBER")


#%% Defined functions

def importOrders(startDate,endDate,accountNumber):
    # Load Account information from environmental variables
    # load_dotenv()
    ACCOUNT = accountNumber #os.environ.get("SELECTED_ACCOUNT")
    
    # Call Account Trades from web
    url = "https://accountservice.tradestation.com/Transaction/Download/excel"
    params = {
        "SelectedAccount": f"{ACCOUNT}",
        "AccountType": "Margin",
        "AccountStatus": "Active",
        "ReportStartDate": startDate,
        "ReportEndDate": endDate,
        "SelectedOutputType": "Web",
        "SelectedTransactionType": "Trades",
        "AllSymbols": "true",
        "SymbolSearchText": "",
        "ExcludeCanceledTrades": "false"
    }
    
    # Send a GET request to the URL and get the response content
    response = requests.get(url, params=params)
    
    # print(response.text)
    
    # Parse the response content with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the table element with class 'otable'
    table = soup.find_all('table', {'class': 'otable'}, limit=1)[0] # Extract only the first table element found
    
    # Extract column names from the table header row
    headers = [th.text.strip() for th in table.find_all('th')]
    
    # Initialize empty lists to store the data
    dates = []
    symbols = []
    cusips = []
    sides = []
    qty = []
    price = []
    principal = []
    comm = []
    other_fees = []
    net_amt = []
    order_ids = []
    
    # Loop over each row in the table
    for tr in table.find_all('tr')[1:]:
        tds = tr.find_all('td')
        dates.append(tds[0].text.strip())
        symbols.append(tds[1].text.strip())
        cusips.append(tds[2].text.strip())
        sides.append(tds[3].text.strip())
        qty.append(int(tds[4].text.strip()))
        
        # Handle price
        price_str = tds[5].text.replace(',', '').replace('$', '').replace('(', '-').replace(')', '')  # Remove the dollar sign
        price.append(float(price_str))  # Convert to float
        
        # Handle principal
        principal_str = tds[6].text.replace(',', '').replace('$', '').replace('(', '-').replace(')', '')  # Remove the dollar sign and commas
        principal.append(float(principal_str))  # Convert to float
        
        # Handle commission
        comm_str = tds[7].text.replace(',', '').replace('$', '').replace('(', '-').replace(')', '')  # Remove the dollar sign and commas
        comm.append(float(comm_str))  # Convert to float
        
        # Handle other fees
        fees_str = tds[8].text.replace(',', '').replace('$', '').replace('(', '-').replace(')', '')  # Remove the dollar sign and commas
        other_fees.append(float(fees_str))  # Convert to float
        
        # Handle net amount 
        net_amt_str = tds[9].text.replace(',', '').replace('$', '').replace('(', '-').replace(')', '')  # Remove the dollar sign and commas
        net_amt.append(float(net_amt_str))  # Convert to float
        
        order_ids.append(tds[10].text.strip())
    
    # Create a dictionary with the data
    data = {'Date': dates, 'Symbol': symbols, 'Cusip': cusips, 'Side': sides,
            'Qty': qty, 'Price': price, 'Principal': principal, 'Comm': comm,
            'Other Fees': other_fees, 'Net Amt': net_amt, 'Order Id': order_ids}
    
    # Create a Pandas DataFrame from the dictionary
    return(pd.DataFrame(data, columns=headers))

#%% Main Script
print('webscrape for TS Trades...')
dfTrades = importOrders('07/01/2022','07/01/2023', ACCOUNT_NUMBER)
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
print('importing rba rates...')
startDate = dt.datetime(2022,7,1)
endDate = dt.datetime(2023,7,1)

# import AUDUSD from RBA interest rates - as required by the ATO
rbaRates1 = pd.read_excel('https://www.rba.gov.au/statistics/tables/xls-hist/2018-2022.xls',skiprows=10)
rbaRates2 = pd.read_excel('https://www.rba.gov.au/statistics/tables/xls-hist/2023-current.xls',skiprows=10)
rbaRates = pd.concat([rbaRates1, rbaRates2], axis=0)

# rbaRates.to_csv('rbaRates.csv')
# rbaRates = pd.read_csv('rbaRates.csv')

audusd = pd.DataFrame()
audusd['Date'] = pd.to_datetime(rbaRates['Series ID'],dayfirst=True)
audusd['audusd'] = rbaRates.FXRUSD
audusd.set_index('Date',inplace=True)
audusd.reset_index(inplace=True)
audusd.set_index('Date')  
audusd = audusd[audusd.Date>startDate]
audusd = audusd[audusd.Date<endDate]
print('...rates imported...')

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