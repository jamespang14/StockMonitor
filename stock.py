import yfinance as yf


def search_stock(stock_name):
    data_df = yf.download(stock_name, start="2020-02-01", end="2020-03-20")
    data_df.to_csv('stock_data/'+stock_name+'.csv')


def update_stock():
    data_df = yf.download("AAPL", start="2020-02-01", end="2020-03-20")
    data_df.to_csv('stock_data/AAPL.csv')

    data_df = yf.download("TSLA", start="2020-02-01", end="2020-03-20")
    data_df.to_csv('stock_data/TSLA.csv')

    data_df = yf.download("AMZN", start="2020-02-01", end="2020-03-20")
    data_df.to_csv('stock_data/AMZN.csv')


def cal_data():
    return 0


def update_timer():
    return 0
