import plotly.graph_objects as go
import csv
import yfinance as yf

ticker = yf.Ticker('CBA.AX')
hist = ticker.history(period='360d')
hist.head()

hist=hist.reset_index()
for i in ['Open', 'High', 'Close', 'Low']: 
      hist[i]  =  hist[i].astype('float64')

fig = go.Figure(data=go.Ohlc(
    x = hist['Date'],
    open = hist['Open'],
    close = hist['Close'],
    high = hist['High'],
    low = hist['Low']
))

fig.show()