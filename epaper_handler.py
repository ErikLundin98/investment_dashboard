import infographics
import financial_data
import sys
import os
import sched

picdir = os.path.join('..', 'pic')
libdir = os.path.join('..', 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2
from PIL import Image, ImageDraw, ImageFont
import time
import datetime
def refresh_data():
    portfolios = index = ipos = coins = None
    try:
        portfolio = financial_data.get_portfolio_metrics(period='1mo')
        index = financial_data.get_index_metrics()
    except:
        print('error while fetching portfolio data')
    try:
        ipos = financial_data.get_ipos()
    except:
        print('error while fetching IPO:s')
    try:
        coins = financial_data.get_coins(5)
    except:
        print('error while fetching crypto data')
    
    return portfolio, index, ipos, coins

def refresh_display(portfolio, index, ipos, coins):
    
    try:
        epd = epd7in5_V2.EPD()
        print('displaying dashboard on epaper display of size',epd.width, epd.height)
        epd.init()
        epd.Clear()
        image = Image.new('1', (epd.width, epd.height), 255)
        draw = ImageDraw.Draw(image)
        plot = infographics.financial_plot(portfolio['time series'], 200, 400)
        image.paste(plot, (400, 0)) # insert plot

        t_portfolio, t_index, t_vix = infographics.financial_text(portfolio, index)
        t_ipos, t_coins = infographics.listings_text(ipos, coins)
        
        table_font = ImageFont.truetype(os.path.join(picdir, 'Roboto-Black.ttf'), 18)
        
        draw.multiline_text((0,0), t_portfolio.get_string(), font=table_font)
        draw.multiline_text((0,140), t_index.get_string(), font=table_font)
        draw.multiline_text((160,140), t_vix, font=table_font)
        draw.multiline_text((0,260), t_coins.get_string(), font=table_font)
        #draw.multiline_text((180,200), t_ipos.get_string(), font=table_font)
        draw.text((400, 0), f'last update:{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', font=table_font)
        print(t_portfolio.get_string())
        epd.display(epd.getbuffer(image))
        print('successful plot of image')
    except IOError as e:
        print(e)
    except KeyboardInterrupt:
        epd7in5_V2.epdconfig.module_exit()
    print('done')
    epd.sleep()


def update():
    portfolio, index, ipos, coins = refresh_data()
    refresh_display(portfolio, index, ipos, coins)

if __name__ == '__main__':
    while True:
        update()
        time.sleep(60*15)
