# -*-coding:utf-8 -*-
from flask import Flask, render_template, Config, url_for, request, redirect, session
import csv
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import glob
import json
import pandas as pd
import stock as st
import plotly
import plotly.graph_objects as go
import yfinance as yf

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Stockinfo.db'
db = SQLAlchemy(app)

#download all stock history on the stock market to csv
def expand_database():
    with open('stock_names.csv') as csv_file:
        data = csv.reader(csv_file, delimiter=',')
        first_line = True
        sdatas = []
        for row in data:
            if not first_line:
                try:
                    st.get_current_stock_history(str(row[0])+".AX")
                except:
                    pass
            else:
                first_line = False

    print("Stock history updated")

#update all stock datas in the folder
def download_stock():
    for filename in glob.glob("./stock_data/*.csv"):
        stock_name = filename
        stock_name=stock_name.replace('./stock_data/', '')
        stock_name=stock_name.replace('.csv', '')
        try:
            st.get_current_stock_history(stock_name)
        except:
            pass
    print("Stock history updated")

#Scheduler update current stocks every x minute
sched = BackgroundScheduler(daemon=True)
sched.add_job(download_stock,'interval',minutes=1440)
sched.start()

#Function to plot stock data into diagram
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
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

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

def add_comma(value):
    temp = '{:,}'.format(value)
    return temp

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_updated = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Task %r>' % self.user_id


@app.route('/', methods=['POST', 'GET'])
def login():
    user = User.query.filter(
        User.username == request.form.get("login_user")).first()
    if user and user.password == request.form.get("login_password"):
        return redirect("/stockmon")
    else:
        return render_template("login.html")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        new_username = request.form['user']
        new_password = request.form['password']
        new_user = User(username=new_username, password=new_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue signing up'
    else:
        return render_template('register.html')

@app.route('/dashboard/data/<stock_name>', methods=['POST', 'GET'])
def data(stock_name):
    if request.method == 'GET':
        stock_display_nm = str(stock_name)
        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
        
        with open('stock_data/'+stock_display_nm+'.csv') as csv_file:
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

        return render_template("data.html", add_comma=add_comma, sdatas=sdatas, stock_display_nm=stock_display_nm, date_time=date_time)
    return render_template('data.html')


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if request.method == 'POST':
        stock_nm = request.form['stock_name']
        stock_display_nm = str(stock_nm)
        temp = st.get_current_price(stock_nm)
        #st.get_current_stock_history(stock_nm)
        st_holders=[]
        try:
            st_holders = st.stock_holders(stock_nm)
        except:
            pass
        #st_recco = st.stock_recommendations(stock_nm)
        current_price = temp
        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
        plot = plot_graph(stock_display_nm)

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
        vwap,vwap_180 = VWAP(sdatas)
        vwap = float(vwap)
        vwap_180 = float(vwap_180)
        avg_volume, avg_volume_180 = average_volume(sdatas)
        avg_volume = int(avg_volume)
        avg_volume_180 = int(avg_volume_180)
        return render_template("dashboard.html",plot=plot ,add_comma=add_comma, avg_volume = avg_volume, avg_volume_180=avg_volume_180,vwap_180=vwap_180 , vwap = vwap , st_holders=st_holders, sdatas=sdatas,current_price=current_price, stock_display_nm=stock_display_nm, date_time=date_time)

    return render_template('dashboard.html')

@app.route('/stockmon', methods=['POST', 'GET'])
def stockmon():
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
    monitorList = []
    for filename in glob.glob("./stock_data/*.csv"):
        stock_nm = filename
        stock_nm=stock_nm.replace('./stock_data/', '')
        stock_nm=stock_nm.replace('.AX.csv', '')
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
                    "change_high": float(rows[360][3])-float(rows[359][3]),
                    "change_open": float(rows[360][5])-float(rows[359][5]),
                    "change_low": float(rows[360][4])-float(rows[359][4]),
                    "change_close": float(rows[360][2])-float(rows[359][2]),
                    "change_volume": int(rows[360][6])-int(rows[359][6]),
                    "High":float(rows[360][3]),
                    "Open":float(rows[360][5]),
                    "Close":float(rows[360][2]),
                    "Low":float(rows[360][4]),
                    "Volume":int(rows[360][6])
                }
                if element['change_high'] > 0 and element['change_open'] > 0 and element['change_low'] > 0 and element['change_close'] > 0 and element['change_volume'] > 0:
                    monitorList.append(element)
            except:
                pass

    return render_template('stockmon.html', add_comma=add_comma, date_time=date_time, monitorList=monitorList)

@app.route('/watchlist/<int:user_id>', methods=['POST', 'GET'])
def watchlist():

    return render_template('watchlist.html')

if __name__ == "__main__":
    app.run(debug=True)
