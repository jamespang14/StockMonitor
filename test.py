import pandas as pd
import yfinance as yf
import csv

def dump_Pandas_Timestamp (ts):
    result = ""
    result += str(ts.year) + "-" + str(ts.month) + "-" + str(ts.day)
    #result += " " + zeroX(ts.hour) + ":" + zeroX(ts.minute) + ":" + zeroX(ts.second)
    return result

def search_stock(stock_name):
    ticker = yf.Ticker(stock_name)
    df=ticker.history(period="360d")
    df.reset_index(inplace = True)

    sdatas = []
    for i in range(len(df["Date"])):
        sdatas.append({
            "Date": dump_Pandas_Timestamp(df["Date"][i]),
            "Close": df["Close"][i],
            "High": df["High"][i],
            "Low": df["Low"][i],
            "Open": df["Open"][i],
            "Volume": df["Volume"][i]
        })

    print(sdatas[358])

def dash(stock_nm):
    with open('stock_data/'+stock_nm+'.csv') as csv_file:
            data = csv.reader(csv_file, delimiter=',')
            first_line = True
            sdatas = []
            for row in data:
                if not first_line:
                    sdatas.append({
                        "Date": row[0],
                        "AdjClose": float(row[1]),
                        "Close": float(row[2]),
                        "High": float(row[3]),
                        "Low": float(row[4]),
                        "Open": float(row[5]),
                        "Volume": int(row[6])
                    })
                else:
                    first_line = False
    print(sdatas[0])


search_stock("CBA.AX")
#dash("CBA.AX")
