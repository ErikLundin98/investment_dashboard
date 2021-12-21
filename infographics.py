import financial_data
from matplotlib import pyplot as plt
import numpy as np
from prettytable import PrettyTable
import PIL

#plt.style.use('grayscale')
plt.tight_layout()
def financial_plot(ts, as_pillow=True, w=450, h=350):

    fig, (ax1, ax2, ax3) = plt.subplots(3, sharex=True)
    dpi = 100
    figsize = (w, h)
    fig.set_size_inches(figsize[0]/dpi, figsize[1]/dpi)
    fig.set_dpi(dpi)
    for ax, tseries, title in zip([ax1, ax2, ax3], ['total_ts', 'crypto_ts', 'stock_ts'], ['total', 'crypto', 'stock']):
        ax.plot(ts['dates'], ts[tseries])
        ax.tick_params(axis=u'y', which=u'both',length=0, labelsize=6)
        #ax.tick_params(axis=u'x', which=u'both')
        ax.text(ts['dates'][0], np.mean(ts[tseries]), int(ts[tseries][-1]), fontsize=7)
        ax.text(ts['dates'][-4], np.mean(ts[tseries]), int(ts[tseries][-1]), fontsize=7)
        ax.text(ts['dates'][0], min(ts[tseries]), title, fontsize=14)

    ticks = ax1.get_xticks()
    ax1.set_xticks([ticks[0], ticks[-1]])
    if as_pillow:
        fig.canvas.draw()
        return PIL.Image.frombytes('RGB', fig.canvas.get_width_height(), fig.canvas.tostring_rgb()).convert('1')
    else:
        plt.savefig('plot.png', dpi=dpi)
    

def financial_text(portfolio, index):
    t1 = PrettyTable(['Portfolio', 'Value', '1D %', u'30D \u03C3'])
    t1.add_row(['Stocks', portfolio['stock value'], portfolio['stock 1d r'], portfolio['stock vol']])
    t1.add_row(['Cryptos', portfolio['crypto value'], portfolio['crypto 1d r'], portfolio['crypto vol']])
    t1.add_row(['---', '---', '---', '---'])
    t1.add_row(['Total', portfolio['total value'], portfolio['total 1d r'], '---'])
   
    t2 = PrettyTable(['Index', '1D %'])
    t2.add_row(['OMXS30', index['OMX']])
    t2.add_row(['S&P500', index['SP']])
    vix_str = f"VIX - Current: {index['VIX']['current']}, 1Y MAX: {index['VIX']['1 year high']}"
    return t1, t2, vix_str

def listings_text(ipos, coins):
    t1 = PrettyTable(['date', 'name', 'ticker', 'exchange'])
    for ipo in ipos:
        t1.add_row(ipo)

    t2 = PrettyTable(['Coin Pair', '24h %'])
    for _, (symbol, prct) in coins.iterrows():
        t2.add_row((symbol, prct))

    return t1, t2

if __name__ == '__main__':
    p_met = financial_data.get_portfolio_metrics(period='1y')
    i_met = financial_data.get_index_metrics()
    financial_plot(p_met['time series'])
    print(financial_text(p_met, i_met))
    print(listings_text(financial_data.get_ipos(), financial_data.get_coins(5)))
