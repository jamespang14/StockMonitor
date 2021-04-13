import glob
import csv
import pandas as pd
import stock as st

def update_data():
    signal = 0
    for filename in glob.glob("./stock_data/*.csv"):
        signal = signal + 1
        stock_name = filename
        stock_name=stock_name.replace('./stock_data/', '')
        stock_name=stock_name.replace('.csv', '')
        try:
            st.get_current_stock_history(stock_name)
        except:
            pass
        print("Stock: "+str(signal))
    print("Stock history updated")

update_data()