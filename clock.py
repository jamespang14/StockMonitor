from apscheduler.schedulers.blocking import BlockingScheduler
import glob
import csv
import pandas as pd
import stock as st

#update all stock datas in the folder within time interval
#sched = BlockingScheduler()

#download all stock history on the stock market to csv
# def expand_database():
#     with open('stock_names.csv') as csv_file:
#         data = csv.reader(csv_file, delimiter=',')
#         first_line = True
#         sdatas = []
#         for row in data:
#             if not first_line:
#                 try:
#                     st.get_current_stock_history(str(row[0])+".AX")
#                 except:
#                     pass
#             else:
#                 first_line = False

#     print("Stock history updated")

# #@sched.scheduled_job('interval', minutes=1440)
def download_stock():
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

if __name__=="__main__":
    # expand_database()
    download_stock()

#sched.start()