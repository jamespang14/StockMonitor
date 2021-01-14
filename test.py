import yfinance as yf

data_df = yf.download("AAPL", start="2020-02-01", end="2020-03-20")
data_df.to_csv('aapl.csv')

