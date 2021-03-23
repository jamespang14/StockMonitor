from apscheduler.schedulers.blocking import BlockingScheduler
import glob
import pandas as pd
import stock as st

#update all stock datas in the folder within time interval
sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes=1440)
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

sched.start()