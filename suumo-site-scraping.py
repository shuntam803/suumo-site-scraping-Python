"""
Created on Sat Oct 15 10:27:45 2022

@author: shuncub

Pythonを使いSUUMOのサイトをスクレイピングしCSVファイルで保存するプログラム
"""


from retry import retry
import requests
from bs4 import BeautifulSoup
import pandas as pd

# 博多区賃貸のHTML
base_url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=090&bs=040&ta=40&sc=40132&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&srch_navi=1"


@retry(tries=3, delay=10, backoff=2)
def get_html(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


all_data = []
# 読み込むページ数(ページ数が多いと時間がかかります)
max_page = 10

for page in range(1, max_page+1):
    # URLを定義
    url = base_url.format(page)

    # HTMLを取得
    soup = get_html(url)

    # すべてのアイテムを抽出
    items = soup.findAll("div", {"class": "cassetteitem"})
    print("page", page, "items", len(items))

    # 各アイテムを処理する
    for item in items:
        stations = item.findAll("div", {"class": "cassetteitem_detail-text"})

        # 各物件の処理
        for station in stations:
            # 変数を定義する
            base_data = {}

            # 取得する物件の情報
            base_data["名称"] = item.find(
                "div", {"class": "cassetteitem_content-title"}).getText().strip()
            base_data["カテゴリー"] = item.find(
                "div", {"class": "cassetteitem_content-label"}).getText().strip()
            base_data["アドレス"] = item.find(
                "li", {"class": "cassetteitem_detail-col1"}).getText().strip()
            base_data["アクセス"] = station.getText().strip()
            base_data["築年数"] = item.find(
                "li", {"class": "cassetteitem_detail-col3"}).findAll("div")[0].getText().strip()
            base_data["構造"] = item.find(
                "li", {"class": "cassetteitem_detail-col3"}).findAll("div")[1].getText().strip()

            # 収集する部屋の情報
            tbodys = item.find(
                "table", {"class": "cassetteitem_other"}).findAll("tbody")

            for tbody in tbodys:
                data = base_data.copy()

                data["階数"] = tbody.findAll("td")[2].getText().strip()

                data["家賃"] = tbody.findAll("td")[3].findAll("li")[
                    0].getText().strip()
                data["管理費"] = tbody.findAll("td")[3].findAll("li")[
                    1].getText().strip()

                data["敷金"] = tbody.findAll("td")[4].findAll("li")[
                    0].getText().strip()
                data["礼金"] = tbody.findAll("td")[4].findAll("li")[
                    1].getText().strip()

                data["間取り"] = tbody.findAll("td")[5].findAll("li")[
                    0].getText().strip()
                data["面積"] = tbody.findAll("td")[5].findAll("li")[
                    1].getText().strip()

                data["URL"] = "https://suumo.jp" + \
                    tbody.findAll("td")[8].find("a").get("href")

                all_data.append(data)

# 収集したデータをCSVファイルに変換
df = pd.DataFrame(all_data)
# CSVファイルで保存(df.to_excel("任意のファイル名.csv"))
df.to_excel("fukuoka_raw_data.csv")
