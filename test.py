from selenium import webdriver
import pandas as pd

driver = webdriver.Safari()
#driver.implicitly_wait(30)

driver.get('https://www2.asx.com.au/markets/trade-our-cash-market/announcements.3DP')
df=pd.read_html(driver.find_element_by_id("data-v-4784e3fa").get_attribute('outerHTML'))[0]
print(df)

# import requests
# import pandas as pd

# url = 'https://www2.asx.com.au/markets/trade-our-cash-market/announcements.3DP'
# html = requests.get(url).content
# df_list = pd.read_html(html)
# df = df_list[-1]
# print(df)
# #df.to_csv('my data.csv')