# -*-coding:utf-8 -*-
from flask import Flask, render_template, Config, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import yfinance as yf

data_df = yf.download("AAPL", start="2020-02-01", end="2020-03-20")
data_df.to_csv('aapl.csv')

data_df = yf.download("TSLA", start="2020-02-01", end="2020-03-20")
data_df.to_csv('tsla.csv')

data_df = yf.download("AMZN", start="2020-02-01", end="2020-03-20")
data_df.to_csv('AMZN.csv')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Stockinfo.db'
db = SQLAlchemy(app)

@app.route('/', methods=['POST','GET'])
def index():
   return render_template("index.html")


@app.route('/', methods=['POST','GET'])
def login():
   return render_template("login.html")

if __name__ == "__main__":
    app.run(debug=True)
