# -*-coding:utf-8 -*-
from flask import Flask, render_template, Config, url_for, request, redirect, session
import csv
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import stock as st

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Stockinfo.db'
db = SQLAlchemy(app)

def round_larger_than_10(num):
    if num > 10.0:
        num = round(num, 2)
        return num
    return num

def typicalPrice(high, low, close, volume):
    typical_price = (high*low*close)/3.0
    typical_price_by_period_volume = typical_price*volume
    return typical_price_by_period_volume

def VWAP(sdatas):
    cumulative_tp = 0.0
    cumulative_volume = 0

    for sdata in sdatas:
        cumulative_tp = cumulative_tp+typicalPrice(sdata['High'], sdata['Low'], sdata['Close'], sdata['Volume'])
        cumulative_volume = cumulative_volume+ sdata['Volume']
    
    vwap = cumulative_tp/cumulative_volume
    return vwap

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


# @app.route('/dashboard', methods=['POST', 'GET'])
# def dashboard():
#     if request.method == 'POST':
#         stock_nm = request.form['stock_name']
#         stock_display_nm = str(stock_nm)
#         st.search_stock(stock_nm)
#         now = datetime.now()
#         date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

#         with open('stock_data/'+stock_nm+'.csv') as csv_file:
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
#         return render_template("index.html", sdatas=sdatas, stock_display_nm=stock_display_nm, date_time=date_time)
#     else:
#         stock_nm = "AAPL"
#         stock_display_nm = str(stock_nm)
#         st.search_stock(stock_nm)
#         now = datetime.now()
#         date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

#         with open('stock_data/'+stock_nm+'.csv') as csv_file:
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
#         return render_template("index.html", sdatas=sdatas, stock_display_nm=stock_display_nm, date_time=date_time)


@app.route('/data/<stock_name>', methods=['POST', 'GET'])
def data(stock_name):
    if request.method == 'GET':
        stock_display_nm = str(stock_name)
        st.search_stock(stock_name)
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

        
        with open('stock_data/'+stock_name+'.csv') as csv_file:
            data = csv.reader(csv_file, delimiter=',')
            first_line = True
            sdatas = []
            for row in data:
                if not first_line:
                    sdatas.append({
                        "Date": row[0],
                        "AdjClose": round(float(row[1]), 2),
                        "Close": round(float(row[2]), 2),
                        "High": round(float(row[3]), 2),
                        "Low": round(float(row[4]), 2),
                        "Open": round(float(row[5]), 2),
                        "Volume": row[6]
                    })
                else:
                    first_line = False
        return render_template("data.html", sdatas=sdatas, stock_display_nm=stock_display_nm, date_time=date_time)
    return render_template('data.html')


@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if request.method == 'POST':
        stock_nm = request.form['stock_name']
        stock_display_nm = str(stock_nm)
        temp = st.get_current_price(stock_nm)
        st.get_current_stock_history(stock_nm)
        st_holders = st.stock_holders(stock_nm)
        st_recco = st.stock_recommendations(stock_nm)
        current_price = round(float(temp), 2)
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
                        "AdjClose": round_larger_than_10(float(row[1])),
                        "Close": round_larger_than_10(float(row[2])),
                        "High": round_larger_than_10(float(row[3])),
                        "Low": round_larger_than_10(float(row[4])),
                        "Open": round_larger_than_10(float(row[5])),
                        "Volume": int(row[6])
                    })
                else:
                    first_line = False
        vwap = VWAP(sdatas)
        return render_template("test.html", vwap = vwap,st_recco=st_recco , st_holders=st_holders, sdatas=sdatas,current_price=current_price, stock_display_nm=stock_display_nm, date_time=date_time)
    else:
        stock_nm = "voo"
        stock_display_nm = "S&P 500"
        temp = st.get_current_price(stock_nm)
        current_price = round(float(temp), 2)
        now = datetime.now()
        st_holders=[]
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

        return render_template("test.html",st_holders=st_holders,current_price=current_price, stock_display_nm=stock_display_nm, date_time=date_time)

    return render_template('test.html')


if __name__ == "__main__":
    app.run(debug=True)
