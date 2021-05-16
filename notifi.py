import smtplib, ssl
import pandas as pd
import stock as st
import yfinance as yf
import glob

sender_email = "jamespang14@gmail.com"
receiver_email = "jamespang14@gmail.com"
andrew_email = "andrew@availer.com"
password = "cal060996633"
smtp_server = 'smtp.gmail.com'

monitorList_1day = []
monitorList_3day = []
monitorList_4day = []
monitorList_5day = []

#Calculate VWAP
def typicalPrice(high, low, close, volume):
    typical_price = (high+low+close)/3.0
    typical_price_by_period_volume = typical_price*volume
    return typical_price_by_period_volume

def VWAP(sdatas):
    cumulative_tp = 0.0
    cumulative_volume = 0

    sdatas_180 = sdatas[-180:]
    cumulative_tp_180 = 0.0
    cumulative_volume_180 = 0

    for sdata in sdatas:
        cumulative_tp = cumulative_tp+typicalPrice(sdata['High'], sdata['Low'], sdata['Close'], sdata['Volume'])
        cumulative_volume = cumulative_volume+ sdata['Volume']

    for sdata_180 in sdatas_180:
        cumulative_tp_180 = cumulative_tp+typicalPrice(sdata_180['High'], sdata_180['Low'], sdata_180['Close'], sdata_180['Volume'])
        cumulative_volume_180 = cumulative_volume+ sdata_180['Volume']
    
    vwap = cumulative_tp/cumulative_volume
    vwap_180 = cumulative_tp_180/cumulative_volume_180

    return vwap, vwap_180

# function to calculate average volume
def average_volume(sdatas):
    volume = 0.0
    volume_180 = 0.0
    sdatas_180 = sdatas[-180:]

    for sdata in sdatas:
        volume = volume+sdata['Volume']

    for sdata_180 in sdatas_180:
        volume_180 = volume_180 + sdata_180['Volume']

    volume = volume/360
    volume_180 = volume_180/180

    return volume, volume_180

def format_df(monitor_list):
    formatted_list = ""
    formatted_list = "Name\tClose\tHigh\tLow\tOpen\tVolume\tchange\tC*V \n"
    for stock in monitor_list:
        formatted_list=formatted_list+str(stock["Name"])+"\t"+str(stock["Close"])+"\t"+str(stock["High"])+"\t"+str(stock["Low"])+"\t"+str(stock["Open"])+"\t"+str(stock["Volume"])+"\t"+str(stock["change_close"])+"\t"+str(stock["CV"])+'\n'
    
    return formatted_list


ctr = 1
for filename in glob.glob("./stock_data/*.csv"):
    stock_nm = filename
    stock_nm=stock_nm.replace('./stock_data/', '')
    stock_nm=stock_nm.replace('.AX.csv', '')

    print(stock_nm+": "+str(ctr))
    ctr = ctr + 1
    ticker = yf.Ticker(stock_nm+".AX")
    df=ticker.history(period="360d")
    df.reset_index(inplace = True)
    sdatas = []
    for i in range(len(df["Date"])):
        sdatas.append({
            "Date": df["Date"][i],
            "Close": df["Close"][i],
            "High": df["High"][i],
            "Low": df["Low"][i],
            "Open": df["Open"][i],
            "Volume": df["Volume"][i]
        })

    try:
        vol6m, vol12m = average_volume(sdatas)
        if sdatas[359]["Close"]*sdatas[359]["Volume"] > 100000:
            element = {
                "Name": stock_nm,
                "High":sdatas[359]["High"],
                "Open":sdatas[359]["Open"],
                "Close":sdatas[359]["Close"],
                "Low":sdatas[359]["Low"],
                "Volume":sdatas[359]["Volume"],
                "change_high": float(sdatas[359]["High"])-float(sdatas[358]["High"]),
                "change_open": float(sdatas[359]["Open"])-float(sdatas[358]["Open"]),
                "change_low": float(sdatas[359]["Low"])-float(sdatas[358]["Low"]),
                "change_close_4": float(sdatas[355]["Close"])-float(sdatas[354]["Close"]),
                "change_close_3": float(sdatas[356]["Close"])-float(sdatas[355]["Close"]),
                "change_close_2": float(sdatas[357]["Close"])-float(sdatas[356]["Close"]),
                "change_close_1": float(sdatas[358]["Close"])-float(sdatas[357]["Close"]),
                "change_close": float(sdatas[359]["Close"])-float(sdatas[358]["Close"]),
                "change_volume": int(sdatas[359]["Volume"])-int(sdatas[358]["Volume"]),
                "vol6m":vol6m,
                "vol12m":vol12m,
                "CV":int(float(sdatas[359]["Close"])*int(sdatas[359]["Close"])),
            }
            if element['change_high'] > 0 and element['change_open'] > 0 and element['change_low'] > 0 and element['change_close'] > 0 and element['change_volume'] > 0 and element['Volume']>element['vol6m']:
                monitorList_1day.append(element)
                if element['change_close_1'] > 0 and element['change_close_2'] > 0:
                    monitorList_3day.append(element)
                if element['change_close_1'] > 0 and element['change_close_2'] > 0 and element['change_close_3'] > 0:
                    monitorList_4day.append(element)
                if element['change_close_1'] > 0 and element['change_close_2'] > 0 and element['change_close_3'] > 0 and element['change_close_4'] > 0:
                    monitorList_5day.append(element)
    except:
        pass 


monitorList_1day = sorted(monitorList_1day, key=lambda k: k['Name'])
monitorList_3day = sorted(monitorList_3day, key=lambda k: k['Name']) 
monitorList_4day = sorted(monitorList_4day, key=lambda k: k['Name'])
monitorList_5day = sorted(monitorList_5day, key=lambda k: k['Name'])

msg_1day = format_df(monitorList_1day)
msg_3day = format_df(monitorList_3day)
msg_4day = format_df(monitorList_4day)
msg_5day = format_df(monitorList_5day)

print("1day: ")
print(msg_1day)
print("3day: ")
print(msg_3day)
print("4day: ")
print(msg_4day)
print("5day: ")
print(msg_5day)

message = f"""\
Subject: Stockmon automated email test

This following message is generated by StockMonitor.
https://stockmonita.herokuapp.com

Stock of the day
1 Day:
{msg_1day}
3 Day:
{msg_3day}
4 Day:
{msg_4day}
5 Day:
{msg_5day}
"""

server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo()
server.starttls()
server.ehlo()
server.login(sender_email,password)
server.sendmail(sender_email,receiver_email,message)
server.sendmail(sender_email,receiver_email,message)

server.quit()