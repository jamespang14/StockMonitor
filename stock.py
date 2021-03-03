import yfinance as yf
import pandas as pd
#from alpha_vantage.timeseries import TimeSeries
from datetime import datetime
import matplotlib  
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
#plt.style.use('seaborn')

api_key = '00KXYJUV0DWBZY95'#alpha vantage api key
now = datetime.now().strftime("%Y-%m-%d")

def get_current_stock_history(symbol):
    ticker = yf.Ticker(symbol)
    data_df = yf.download(symbol, period='360d', end=now)
    data_df.to_csv('stock_data/'+symbol+'.csv')
    print(data_df)

#get_current_stock_history('TSLA AAPL MSFT')

def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    return todays_data['Close'][0]

#print(get_current_price('tsla'))

def get_stock_info(symbol):
    ticker = yf.Ticker(symbol)
    stockinfo = ticker.info
    
    # for key,value in stockinfo.items():
    #     temp = temp + str(key)+" : "+str(value)
    return stockinfo

#print(get_stock_info('CBA.AX'))

def stock_recommendations(symbol):
    ticker = yf.Ticker(symbol)
    stock_recommendation = ticker.recommendations
    return str(stock_recommendation)

#print(stock_recommendations('TSLA'))

def stock_splits(symbol):
    ticker = yf.Ticker(symbol)
    s_splits = ticker.splits
    print(s_splits)

#stock_splits('TSLA')

def stock_dividends(symbol):
    ticker = yf.Ticker(symbol)
    divs = ticker.dividends
    print(divs)

    data = divs.resample('Y').sum()
    data = data.reset_index()
    data['Year'] = data['Date'].dt.year
    plt.figure()
    plt.bar(data['Year'],data['Dividends'])
    plt.ylabel('Yields($)')
    plt.xlabel('Year')
    plt.title(symbol+' dividend history')
    plt.show()

#stock_dividends('CBA.AX')

def stock_holders(symbol):
    ticker = yf.Ticker(symbol)
    holders = ticker.major_holders
    data = []
    for i in holders[0]:
        data.append(i)
    return data

#print(stock_holders('CBA.AX'))


def string_stock_info(symbol):
    ticker = yf.Ticker(symbol)
    stockinfo = ticker.info
    temp = ""
    for key,value in stockinfo.items():
        temp = temp+ str(key)+': '+str(value)+'\n'
    return temp


def search_stock(stock_name):
    data_df = yf.download(stock_name, start="2020-02-01", end="2020-03-20")
    data_df.to_csv('stock_data/'+stock_name+'.csv')


def cal_data():
    return 0


def update_timer():
    return 0
