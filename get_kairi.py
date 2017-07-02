from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pandasjsm import pandasjsm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyzer import analyzer
import datetime
from pprint import pprint
import statsmodels.api as sm
import numpy as np


options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1280,1024')
driver = webdriver.Chrome(chrome_options=options)
driver.get('https://jp.kabumap.com/servlets/kabumap/Action?SRC=stockRanking/base&ind=spr25&exch=all&d=a')
print("サイト名：{0}".format(driver.title)) #=> Google
#driver.save_screenshot('test.png')
pj = pandasjsm()

try:
    blacklist = []
    with open("./code_blacklist.txt", "r") as f:
        for line in f.readlines():
            if line.rstrip().isdigit():
                blacklist.append(line.rstrip())
except:
    blacklist = None


def get_high_dev_code(class_name, result):
    for tr in driver.find_elements_by_class_name(class_name):
        try:
            code = tr.find_element_by_class_name("KM_CODE").text
            name = tr.find_element_by_class_name("KM_TEXT").text
            deviation = tr.find_element_by_class_name("select_number").text
            if code in blacklist:
                continue
            if float(deviation) > -15.0:
                break
            result.append({"code":code, "name":name, "deviation":deviation})

        except Exception as e:
            print("NG")
            print(e)

result = []
get_high_dev_code("KM_TINT", result)
get_high_dev_code("KM_NOTINT", result)
driver.quit()

result = sorted(result, key=lambda x: x['deviation'], reverse=True)
for item in result:
    pprint(item)


for res in result:
    try:
        code = res["code"]
        deviation = res["deviation"]
        df = pj.get_historical_prices(code, start_date = datetime.date(2016,1,1))
        analyzer.ma_deviation(df)
        analyzer.momentum(df, period=25)
        df["max"] = df.adj_close.rolling(window=20).max().shift(periods=-20)
        df["max"] = df["max"] / df["adj_close"]
        df["min"] = df.adj_close.rolling(window=20).min().shift(periods=-20)
        df["min"] = df["min"] / df["adj_close"]
        fig, [ax1, ax2] = plt.subplots(2,1,figsize=(6,8))
        df["momentum25"] = df["momentum25"] / df["adj_close"]
        #        df.plot(ax=ax1, kind='scatter', x="momentum25", y="max", c=df.MA25_deviation, cmap="winter")
        #        df.plot(ax=ax2, kind='scatter', x="momentum25", y="min", c=df.MA25_deviation, cmap="winter")
        fig.suptitle("Today: deviation = {0}, momentum = {1}".format(deviation, df.tail(1).momentum25[0]))

        df = df[df["momentum25"] <= 0].dropna()
        df = df[df["MA25_deviation"] <= -0.15].dropna()
        x = df["momentum25"]
        X = np.column_stack((np.repeat(1, x.size), x))
        model_ols = sm.OLS(df["max"], X)
        results = model_ols.fit()

        a, b = results.params
        ax1.plot(x, a+b*x)
        ax1.text(0, 0, "a={:8.3f}, b={:8.3f}".format(a,b))

        print(results.summary())
        df.plot(ax=ax1, kind='scatter', x="momentum25", y="max", c=df.MA25_deviation, cmap="winter")
        df.plot(ax=ax2, kind='scatter', x="momentum25", y="min", c=df.MA25_deviation, cmap="winter")

        plt.savefig("./figure/{0}.png".format(code))
        plt.close()

    except Exception as e:
        print("NG")
        print(e)
