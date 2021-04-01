# -*-coding:utf-8 -*-
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

app = Flask(__name__)
app.secret_key = "StockMonita"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Stockinfo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now)
    date_updated = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Task %r>' % self.user_id

class Watchlist(db.Model):
    __tablename__ = 'watchlist'
    list_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    stock_code = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)
    current_price = db.Column(db.Numeric, nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.list_id

class Feedback(db.Model):
    __tablename__ = 'feedback'
    feedback_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.now)
    feedback = db.Column(db.String(2000), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.feedback_id


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

#function to format large volume numbers
def add_comma(value):
    temp = '{:,}'.format(value)
    return temp

#login route for the user
@app.route('/', methods=['POST', 'GET'])
def login():
    user = User.query.filter(
        User.username == request.form.get("login_user")).first()
    if user and user.password == request.form.get("login_password"):
        session["user"] = user.username
        return redirect("/stockmon")
    else:
        return render_template("login.html")

#sign up route for users
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

#dashboard full data route
#data contain full history of stocks
@app.route('/dashboard/data/<stock_name>', methods=['POST', 'GET'])
def data(stock_name):
    if request.method == 'GET':
        stock_display_nm = str(stock_name+".AX")
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

#dashboard route
#will contain current price, 5d stock shortlist, plot, calculations
@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if request.method == 'POST':
        stock_nm = request.form['stock_name']
        stock_nm = stock_nm + ".AX"
        stock_display_nm = str(stock_nm)
        stock_display_nm = stock_nm.replace('.AX', '')
        current_price = st.get_current_price(stock_nm)
        sector_info=''
        try:
            sector_info = str(st.get_sector_info(stock_nm))
        except:
            pass
        #st.get_current_stock_history(stock_nm)
        #st_recco = st.stock_recommendations(stock_nm)
        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
        plot = plot_graph(stock_nm)

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
        return render_template("dashboard.html",sector_info=sector_info, plot=plot ,add_comma=add_comma, avg_volume = avg_volume, avg_volume_180=avg_volume_180,vwap_180=vwap_180 , vwap = vwap , sdatas=sdatas,current_price=current_price, stock_display_nm=stock_display_nm, date_time=date_time)

    return redirect('/stockmon')

#route to filter out stocks that fits the criteria
#main route / homepage after logging in
@app.route('/stockmon', methods=['POST', 'GET'])
def stockmon():
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
    monitorList = []
    for filename in glob.glob("./stock_data/*.csv"):
        stock_nm = filename
        stock_nm=stock_nm.replace('./stock_data/', '')
        stock_nm=stock_nm.replace('.AX.csv', '')
        vol6m, vol12m = stockmon_volume(filename)

        with open(filename) as csv_file:
            data = csv.reader(csv_file)
            rows = list(data)

            try:
                if float(rows[360][2]) and float(rows[360][2])<5 and int(float(rows[360][2])*int(rows[360][6])) > 100000:
                    if int(rows[360][6]) > 0 and int(rows[360][6]) < 1600000000:
                        element = {
                            "Name": stock_nm,
                            #"Sector":str(st.get_sector_info(filename)),
                            "change_high": float(rows[360][3])-float(rows[359][3]),
                            "change_open": float(rows[360][5])-float(rows[359][5]),
                            "change_low": float(rows[360][4])-float(rows[359][4]),
                            #"change_close_4": float(rows[356][2])-float(rows[355][2]),
                            #"change_close_3": float(rows[357][2])-float(rows[356][2]),
                            "change_close_2": float(rows[358][2])-float(rows[357][2]),
                            "change_close_1": float(rows[359][2])-float(rows[358][2]),
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
                        if element['change_high'] > 0 and element['change_open'] > 0 and element['change_low'] > 0 and element['change_close'] > 0 and element['change_volume'] > 0:
                            if element['change_close_1'] > 0 and element['change_close_2'] > 0:
                                monitorList.append(element)
            except:
                pass

    monitorList = sorted(monitorList, key=lambda k: k['Name'])            
    return render_template('stockmon.html', add_comma=add_comma, date_time=date_time, monitorList=monitorList)

@app.route('/watchlist/', methods=['POST', 'GET'])
def watchlist():
    stocks = Watchlist.query.filter(Watchlist.username == session.get("user")).all()
    userlist = []
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")
    for stock in stocks:
        temp = float(st.get_current_price(stock.stock_code+".AX"))
        element = {
            "id":stock.list_id,
            "Name":stock.stock_code,
            "Date_added":stock.date_added,
            "Added_price":float(stock.current_price),
            "Current_price":temp,
            "Price_change": float(stock.current_price)-temp
        }
        userlist.append(element)
    return render_template('watchlist.html',add_comma=add_comma,date_time=date_time,userlist=userlist)


@app.route('/addwatchlist/<stock_cd>', methods=['POST', 'GET'])
def add_list(stock_cd):
    stock_nm = stock_cd
    user = session["user"]
    c_price = st.get_current_price(stock_nm+".AX")
    new_list_entry = Watchlist(username=user, stock_code=stock_nm, current_price=c_price)

    try:
        db.session.add(new_list_entry)
        db.session.commit()

        return redirect(request.referrer)
    except:
        return 'There was an issue'

    # return redirect(request.referrer)

@app.route('/remove/<stock_name>', methods=['POST', 'GET'])
def remove():
    return redirect(request.referrer)

@app.route('/feedback', methods=['POST', 'GET'])
def feedback():
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

    if request.method == 'POST':
        fback = request.form['feedback']
        user = session["user"]
        new_feedback = Feedback(username = user, feedback = fback)
        
        try:
            db.session.add(new_feedback)
            db.session.commit()
            return render_template('feedback.html', date_time=date_time)
        except:
            return 'There was an issue posting feedback'
    else:
        return render_template('feedback.html', date_time=date_time)

@app.route('/checkfeedback', methods=['POST', 'GET'])
def checkfeedback():
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

    feedbacks = Feedback.query.order_by(Feedback.feedback_id).all()
    
    return render_template('checkfeedback.html', feedbacks=feedbacks, date_time=date_time)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)

