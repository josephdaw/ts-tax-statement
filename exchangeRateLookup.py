# %% Import Packages
# Import native packages
# Import 3rd party packages
import pandas as pd
# Import my local files

def importRatesFromRBA(start_date, end_date):
    print('importing rba rates...')
    # import AUDUSD from RBA interest rates - as required by the ATO
    rba_rates_1 = pd.read_excel(
        'https://www.rba.gov.au/statistics/tables/xls-hist/2018-2022.xls',
        skiprows=10)
    rba_rates_2 = pd.read_excel(
        'https://www.rba.gov.au/statistics/tables/xls-hist/2023-current.xls',
        skiprows=10)
    rba_rates = pd.concat([rba_rates_1, rba_rates_2], axis=0)

    # rba_rates.to_csv('rba_rates.csv')
    # rba_rates = pd.read_csv('rba_rates.csv')

    aud_usd = pd.DataFrame()
    aud_usd['Date'] = pd.to_datetime(rba_rates['Series ID'],dayfirst=True)
    aud_usd['audusd'] = rba_rates.FXRUSD
    aud_usd.set_index('Date',inplace=True)
    aud_usd.reset_index(inplace=True)
    aud_usd.set_index('Date')  
    aud_usd = aud_usd[aud_usd.Date>start_date]
    aud_usd = aud_usd[aud_usd.Date<end_date]
    print('...rates imported...')

    return aud_usd