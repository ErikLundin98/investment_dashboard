import infographics
import financial_data
def refresh_data():
    portfolios = index = ipos = coins = None
    try:
        portfolio = financial_data.get_portfolio_metrics(period='1y')
        index = financial_data.get_index_metrics()
    except:
        print('error while fetching portfolio data')
    try:
        ipos = financial_data.get_ipos()
    except:
        print('error while fetching IPO:s')
    try:
        coins = financial_data.get_coins()
    except:
        print('error while fetching crypto data')
    
    return portfolio, index, ipos, coins


def refresh_display():

    pass



if __name__ == '__main__':
    pass