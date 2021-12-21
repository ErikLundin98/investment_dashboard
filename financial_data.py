import yfinance as yf
import json
import pandas as pd
import numpy as np
import datetime
from matplotlib import pyplot as plt
import finnhub
import binance
import os
from dotenv import load_dotenv

load_dotenv()
fh_client = finnhub.Client(api_key=os.getenv('FH_KEY'))
bin_client  = binance.Client(os.getenv('BIN_KEY'), os.getenv('BIN_SECRET'))

def get_holdings(file_name = "holdings.json"):
    """
    Load json dict
    """
    
    with open(file_name, 'r') as file:
        holdings = json.load(file)
        return holdings
    
def get_historical_prices(tickers_and_bases, period='1mo', currency='SEK'):
    """
    Load daily close prices (and spot) in a dataframe for a set of tickers and their base currencies
    Convert the closes to a desired currency
    Return the dataframe
    """
    print("downloading prices, period:", period, ", tickers:", tickers_and_bases)
    tickers = list(tickers_and_bases.keys())
    bases = list(tickers_and_bases.values())
    data = yf.download(' '.join(tickers), period=period, prepost=True) # download prices
    closes = data['Adj Close']
    # replace NA:s with previous close or subsequent close if not possible
    closes = closes.fillna(method='ffill').fillna(method='bfill')

    # convert all prices to desired currency
    fx_pairs = [base + currency + "=X" for base in bases if (base != currency)]
    fx_pairs_set = set(fx_pairs)
    currency_prices = yf.download(' '.join(fx_pairs_set), period=period, prepost=True)["Adj Close"] # download FX
    currency_mat = pd.DataFrame(index=closes.index)

    for i, (ticker, base) in enumerate(zip(tickers, bases)):
        if base == currency:
            currency_mat[ticker] = 1
        else:
            if len(fx_pairs_set) == 1: # no multiindex
                currency_mat[ticker] = currency_prices
            else:
                currency_mat[ticker] = currency_prices[base+currency+"=X"]
    
    # replace NA:s with previous close or subsequent close if not possible
    currency_mat = currency_mat.fillna(method='ffill').fillna(method='bfill') 
    closes = closes*currency_mat

    return closes

def extract_tickers_and_bases(holdings):
    """
    Parse ticker-currency pairs
    """
    tickers_and_bases = {}

    for key, value in holdings['stocks'].items():
        tickers_and_bases[key] = value['currency']
    for key, value in holdings['cryptocurrencies'].items():
        tickers_and_bases[key] = key.split('-')[1]

    return tickers_and_bases

def prct_str(x):
    return "{:.2%}".format(x)

def get_index_metrics():
    """
    Fetch some common index metrics
    """
    VIX = yf.Ticker('^VIX').info
    OMX = yf.Ticker('^OMX').info
    SP = yf.Ticker('^GSPC').info

    metrics = {
        'VIX' : {
            'current' : str(VIX['regularMarketPrice']) + '%',
            '1 year high' : str(VIX['fiftyTwoWeekHigh']) + '%',
        },
        'OMX' : prct_str(OMX['regularMarketPrice']/OMX['open'] - 1),
        'SP' : prct_str(SP['regularMarketPrice']/SP['open'] - 1),
    }

    return metrics

def get_portfolio_metrics(period='1mo'):
    """
    Fetch metrics for portfolio in holdings.json
    """
    b_days = 250
    holdings = get_holdings()
    pairs = extract_tickers_and_bases(holdings)
    data = get_historical_prices(pairs, currency="SEK", period=period)
    
    # calculate portfolio values
    v_crypto = np.zeros(len(data))
    dates = data.index
    for ticker, amount in holdings['cryptocurrencies'].items():
        v_crypto += data[ticker].values*amount

    v_stock = np.zeros(len(data))
    for ticker, h_and_c in holdings['stocks'].items():
        v_stock += data[ticker].values*h_and_c['amount']

    v_tot = v_crypto + v_stock 
    r_crypto = v_crypto[1:]/v_crypto[0:-1] - 1 # arithmetic
    r_stock = v_stock[1:]/v_stock[0:-1] - 1 # arithmetic
    r_tot = v_tot[1:]/v_tot[0:-1] - 1 # arithmetic
    vol_crypto = np.std(r_crypto, ddof=1)
    vol_stock = np.std(r_stock, ddof=1)
    metrics = {
        'last updated date' : dates[-1],
        'time series': {
            'dates' : dates,
            'crypto_ts' : v_crypto,
            'stock_ts' : v_stock,
            'total_ts' : v_tot
        },
        'crypto vol' : prct_str(vol_crypto*np.sqrt(b_days)),
        'stock vol' : prct_str(vol_stock*np.sqrt(b_days)),
        'crypto 1d r' : prct_str(r_crypto[-1]),
        'stock 1d r' : prct_str(r_stock[-1]),
        'total 1d r' : prct_str(r_tot[-1]),
        'crypto value' : int(v_crypto[-1]),
        'stock value' : int(v_stock[-1]),
        'total value' : int(v_tot[-1])
    }
    return metrics

def get_ipos(_from=datetime.date.today(), to=(datetime.date.today()+datetime.timedelta(days=2))):
    """
    Get upcoming ipo calendar
    """
    _from = _from.strftime('%Y-%m-%d')
    to = to.strftime('%Y-%m-%d')
    ipos = fh_client.ipo_calendar(_from=_from, to=to)

    ipo_list = [(ipo['date'], ipo['name'], ipo['symbol'], ipo['exchange']) for ipo in ipos['ipoCalendar']]
    return ipo_list

def get_coins(top=8):
    """
    Get trending coins
    """
    tickers = bin_client.get_ticker()
    df = pd.DataFrame(tickers)
    df_change = df[['symbol', 'priceChangePercent']]
    df_change['priceChangePercent'] = df_change['priceChangePercent'].astype(float)
    df_change = df_change.sort_values(by='priceChangePercent', ascending=False)
    return df_change.head(top)

if __name__ == "__main__":
    #print(get_portfolio_metrics())
    #print(get_index_metrics())
    #print(get_ipos(datetime.date(2021,10,28), datetime.date(2021,10,30)))
    print(get_coins())