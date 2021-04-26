from selenium import webdriver
import pandas as pd


driver = webdriver.Chrome('./chromedriver')
driver.get("https://www2.asx.com.au/markets/trade-our-cash-market/announcements.3DP")

html = driver.page_source

tables = pd.read_html(html)
data = tables[1]

driver.close()

# import requests
# import pandas as pd

# url = 'https://www2.asx.com.au/markets/trade-our-cash-market/announcements.3DP'
# html = requests.get(url).content
# df_list = pd.read_html(str(soup.find_all('table')[0])
# df = df_list[-1]
# print(df)
# # #df.to_csv('my data.csv')