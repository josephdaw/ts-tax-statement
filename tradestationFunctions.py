# %% Import Packages
# Import native packages
# Import 3rd party packages
from bs4 import BeautifulSoup
import requests
import pandas as pd
# Import my local files

# note: dates are in format mm/dd/yyyy
def importOrders(startDate,endDate,accountNumber):
    
    # Call Account Trades from web
    url = "https://accountservice.tradestation.com/Transaction/Download/excel"
    params = {
        "SelectedAccount": f"{accountNumber}",
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
    # response = requests.get(url, params=params, timeout=10)
    
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
