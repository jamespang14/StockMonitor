import plotly
import plotly.graph_objects as go
import yfinance as yf

def plot_graph(stock):
    ticker = yf.Ticker(stock)
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
    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # return graphJSON
    fig.show()
plot_graph("ZYUS.AX")