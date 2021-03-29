from flask import Flask, render_template, Config, url_for, request, redirect, session
import csv
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import glob
import json
import pandas as pd
import stock as st
import plotly
import plotly.graph_objects as go
import yfinance as yf

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

def stockmon_volume(stock_name):
    vol180 = 0
    vol360 = 0
    with open(stock_name) as csv_file:
        data = csv.reader(csv_file, delimiter=',')
        first_line = True
        sdatas = []
        for row in data:
            try:
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
            except:
                pass

        avg_volume, avg_volume_180 = average_volume(sdatas)
        avg_volume = int(avg_volume)
        avg_volume_180 = int(avg_volume_180)

    return avg_volume, avg_volume_180


def read():
    monitorList = []
    for filename in glob.glob("./stock_data/*.csv"):
        stock_nm = filename
        stock_nm=stock_nm.replace('./stock_data/', '')
        stock_nm=stock_nm.replace('.AX.csv', '')
        vol6m, vol12m = stockmon_volume(filename)

        with open(filename) as csv_file:
            data = csv.reader(csv_file)
            rows = list(data)
            
            #compare close price from 1 year age to today
            #if close price increased than into watch list

            #Above average volume 
            #day high,open,close needs to be high
            #day volume, low has to be high
            #VWAP has to be higher

            try:
                element = {
                    "Name": stock_nm,
                    #"Sector":str(st.get_sector_info(filename)),
                    "change_high": float(rows[360][3])-float(rows[359][3]),
                    "change_open": float(rows[360][5])-float(rows[359][5]),
                    "change_low": float(rows[360][4])-float(rows[359][4]),
                    "change_close": float(rows[360][2])-float(rows[359][2]),
                    "change_volume": int(rows[360][6])-int(rows[359][6]),
                    "High":float(rows[360][3]),
                    "Open":float(rows[360][5]),
                    "Close":float(rows[360][2]),
                    "Low":float(rows[360][4]),
                    "Volume":int(rows[360][6]),
                    "vol6m":vol6m,
                    "vol12m":vol12m,
                    "CV":int(float(rows[360][2])*int(rows[360][6]))
                }
                if element['Close']>0.01 and element['Close']<5 and element['CV'] > 100000 and element['change_high'] > 0 and element['change_open'] > 0 and element['change_low'] > 0 and element['change_close'] > 0 and element['change_volume'] > 0:
                    if element['Volume']>0 and element['Volume']<1600000000:
                        monitorList.append(element)
            except:
                pass   
    return monitorList
    
stocks = read()
stocks = sorted(stocks, key=lambda k: k['Name'])
for stock in stocks:
    print(stock['Name'])
