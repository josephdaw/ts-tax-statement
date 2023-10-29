# %% Import Packages
# Import native packages
# Import 3rd party packages
import pandas as pd
# Import my local files

def importRatesFromRBA(startDate, endDate):
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

    return audusd