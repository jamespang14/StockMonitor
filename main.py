# -*-coding:utf-8 -*-
from flask import Flask, render_template, Config, url_for, request, redirect, session
import csv
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
import glob
import pandas as pd
import stock as st

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Stockinfo.db'
db = SQLAlchemy(app)

def download_stock():
    st.get_current_stock_history("ANZ.AX")
    st.get_current_stock_history("CBA.AX")
    st.get_current_stock_history("360.AX")
    st.get_current_stock_history("AMA.AX")
    st.get_current_stock_history("ATS.AX")
    st.get_current_stock_history("WMA.AX")
    st.get_current_stock_history("WOW.AX")
    st.get_current_stock_history("RIO.AX")
    st.get_current_stock_history("OZL.AX")
    st.get_current_stock_history("TPD.AX")
    print("Stock history updated")

sched = BackgroundScheduler(daemon=True)
sched.add_job(download_stock,'interval',minutes=15)
sched.start()

def round_larger_than(num):
    if num > 0.1:
        num = round(num, 2)
        return num
    if num <= 0.1:
        num = round(num, 5)
    return num

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
        return redirect("/dashboard")
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

# @app.route('/data/<stock_name>', methods=['POST', 'GET'])
# def data(stock_name):
#     if request.method == 'GET':
#         stock_display_nm = str(stock_name)
#         st.search_stock(stock_name)
#         now = datetime.now()
#         date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

        
#         with open('stock_data/'+stock_name+'.csv') as csv_file:
#             data = csv.reader(csv_file, delimiter=',')
#             first_line = True
#             sdatas = []
#             for row in data:
#                 if not first_line:
#                     sdatas.append({
#                         "Date": row[0],
#                         "AdjClose": round(float(row[1]), 2),
#                         "Close": round(float(row[2]), 2),
#                         "High": round(float(row[3]), 2),
#                         "Low": round(float(row[4]), 2),
#                         "Open": round(float(row[5]), 2),
#                         "Volume": row[6]
#                     })
#                 else:
#                     first_line = False
#         return render_template("data.html", sdatas=sdatas, stock_display_nm=stock_display_nm, date_time=date_time)
#     return render_template('data.html')


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if request.method == 'POST':
        stock_nm = request.form['stock_name']
        stock_display_nm = str(stock_nm)
        temp = st.get_current_price(stock_nm)
        #st.get_current_stock_history(stock_nm)
        st_holders = st.stock_holders(stock_nm)
        #st_recco = st.stock_recommendations(stock_nm)
        current_price = round_larger_than(temp)
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

        with open('stock_data/'+stock_nm+'.csv') as csv_file:
            data = csv.reader(csv_file, delimiter=',')
            first_line = True
            sdatas = []
            for row in data:
                if not first_line:
                    sdatas.append({
                        "Date": row[0],
                        "AdjClose": round_larger_than(float(row[1])),
                        "Close": round_larger_than(float(row[2])),
                        "High": round_larger_than(float(row[3])),
                        "Low": round_larger_than(float(row[4])),
                        "Open": round_larger_than(float(row[5])),
                        "Volume": int(row[6])
                    })
                else:
                    first_line = False
        vwap,vwap_180 = VWAP(sdatas)
        vwap = round_larger_than(float(vwap))
        vwap_180 = round_larger_than(float(vwap_180))
        avg_volume, avg_volume_180 = average_volume(sdatas)
        avg_volume = round_larger_than(float(avg_volume))
        avg_volume_180 = round_larger_than(float(avg_volume_180))
        return render_template("test.html",avg_volume = avg_volume, avg_volume_180=avg_volume_180,vwap_180=vwap_180 , vwap = vwap , st_holders=st_holders, sdatas=sdatas,current_price=current_price, stock_display_nm=stock_display_nm, date_time=date_time)
    
    else:
        stock_nm = "CBA.AX"
        stock_display_nm = str(stock_nm)
        temp = st.get_current_price(stock_nm)
        #st.get_current_stock_history(stock_nm)
        st_holders = st.stock_holders(stock_nm)
        #st_recco = st.stock_recommendations(stock_nm)
        current_price = round_larger_than(temp)
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

        with open('stock_data/'+stock_nm+'.csv') as csv_file:
            data = csv.reader(csv_file, delimiter=',')
            first_line = True
            sdatas = []
            for row in data:
                if not first_line:
                    sdatas.append({
                        "Date": row[0],
                        "AdjClose": round_larger_than(float(row[1])),
                        "Close": round_larger_than(float(row[2])),
                        "High": round_larger_than(float(row[3])),
                        "Low": round_larger_than(float(row[4])),
                        "Open": round_larger_than(float(row[5])),
                        "Volume": int(row[6])
                    })
                else:
                    first_line = False

        vwap,vwap_180 = VWAP(sdatas)
        vwap = round_larger_than(float(vwap))
        vwap_180 = round_larger_than(float(vwap_180))
        avg_volume, avg_volume_180 = average_volume(sdatas)
        avg_volume = round_larger_than(float(avg_volume))
        avg_volume_180 = round_larger_than(float(avg_volume_180))
        return render_template("test.html",avg_volume = avg_volume, avg_volume_180=avg_volume_180, vwap_180 = vwap_180, vwap = vwap , st_holders=st_holders, sdatas=sdatas,current_price=current_price, stock_display_nm=stock_display_nm, date_time=date_time)

    return render_template('test.html')

@app.route('/watchlist', methods=['POST', 'GET'])
def watchlist():
    now = datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    watchList = []
    for filename in glob.glob("./stock_data/*.csv"):
        stock_nm = filename
        stock_nm=stock_nm.replace('./stock_data/', '')
        stock_nm=stock_nm.replace('.AX.csv', '')
        with open(filename) as csv_file:
            data = csv.reader(csv_file)
            rows = list(data)
            #compare close price from 1 year age to today
            #if close price increased than into watch list
            element = {
                "Name": stock_nm,
                "Pct_change_1y": round_larger_than((float(rows[360][2])-float(rows[1][2]))/float(rows[1][2])),
                "Pct_change_1m": round_larger_than((float(rows[360][2])-float(rows[330][2]))/float(rows[330][2])),
                "Pct_change_1w": round_larger_than((float(rows[360][2])-float(rows[353][2]))/float(rows[353][2])),
                "Year_close":round_larger_than(float(rows[1][2])),
                "Month_close":round_larger_than(float(rows[330][2])),
                "Week_close":round_larger_than(float(rows[353][2])),
                "Close":round_larger_than(float(rows[360][2]))
            }
            if element['Pct_change_1y'] > 0 and element['Pct_change_1m'] > 0 and element['Pct_change_1w'] > 0:
                watchList.append(element)

    return render_template('watchlist.html', date_time=date_time, watchList=watchList)

if __name__ == "__main__":
    app.run(debug=True)
