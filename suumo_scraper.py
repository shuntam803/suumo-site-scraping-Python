"""
Created on Thu Apr 27 10:27:45 2023
@author: shuncub
SUUMOのサイトをスクレイピングしCSVファイルで保存するプログラム
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from retry import retry

# 博多区賃貸のHTML
base_url = "https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=090&bs=040&ta=40&sc=40132&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&srch_navi=1"


@retry(tries=3, delay=4, backoff=2)
def get_html(url):
    """
    指定されたURLからHTMLを取得し、BeautifulSoupオブジェクトを返します。
    リクエストに失敗した場合、最大3回リトライします。リトライ間隔は4秒で、バックオフ係数は2です。
    :param url: スクレイピング対象のURL
    :return: BeautifulSoupオブジェクト
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup


def extract_data(item):
    """
    物件情報を抽出し、物件データとアクセス情報を返します。
    :param item: 物件情報を含むHTML要素
    :return: [property_data, stations] 物件データとアクセス情報
    """
    property_data = {}
    property_data["名称"] = item.find("div", {"class": "cassetteitem_content-title"}).text.strip()
    property_data["カテゴリー"] = item.find("div", {"class": "cassetteitem_content-label"}).text.strip()
    property_data["アドレス"] = item.find("li", {"class": "cassetteitem_detail-col1"}).text.strip()
    property_data["築年数"] = item.find("li", {"class": "cassetteitem_detail-col3"}).find_all("div")[0].text.strip()
    property_data["構造"] = item.find("li", {"class": "cassetteitem_detail-col3"}).find_all("div")[1].text.strip()
    stations = item.find_all("div", {"class": "cassetteitem_detail-text"})
    return [property_data, stations]


def extract_room_data(tbody, property_data, station_data):
    """
    部屋情報を抽出し、物件データとアクセス情報を含む辞書を返します。
    :param tbody: 部屋情報を含むHTML要素
    :param property_data: 物件データ
    :param station_data: アクセス情報
    :return: room_data 物件データとアクセス情報を含む辞書
    """
    room_data = property_data.copy()
    room_data["アクセス"] = station_data.text.strip()
    room_data["階数"] = tbody.find_all("td")[2].text.strip()
    room_data["家賃"] = tbody.find_all("td")[3].find_all("li")[0].text.strip()
    room_data["管理費"] = tbody.find_all("td")[3].find_all("li")[1].text.strip()
    room_data["敷金"] = tbody.find_all("td")[4].find_all("li")[0].text.strip()
    room_data["礼金"] = tbody.find_all("td")[4].find_all("li")[1].text.strip()
    room_data["間取り"] = tbody.find_all("td")[5].find_all("li")[0].text.strip()
    room_data["面積"] = tbody.find_all("td")[5].find_all("li")[1].text.strip()
    room_data["URL"] = "https://suumo.jp" + tbody.find_all("td")[8].find("a").get("href")
    return room_data


def main():
    """
    博多区賃貸情報を複数のページから取得し、それらの情報を結合してCSVファイルに出力する。
    この関数は、指定されたページ数の博多区賃貸情報を取得します。
    各ページから賃貸物件のデータを抽出し、全てのデータを結合してデータフレームに格納します。
    最後に、データフレームをCSVファイルに出力します。
    """
    all_data = []
    # 読み込むページ数(ページ数が多いと時間がかかります)
    max_page = 10

    for page in range(1, max_page + 1):
        url = base_url.format(page)
        soup = get_html(url)
        items = soup.find_all("div", {"class": "cassetteitem"})
        print(f"page {page} items {len(items)}") 

        for item in items:
            property_data, stations = extract_data(item)
            stations = item.find_all("div", {"class": "cassetteitem_detail-text"})

            for station in stations:
                tbodys = item.find("table", {"class": "cassetteitem_other"}).find_all("tbody")

                for tbody in tbodys:
                    room_data = extract_room_data(tbody, property_data, station)
                    all_data.append(room_data)

    df = pd.DataFrame(all_data, index=range(1, len(all_data) + 1))
    df.to_csv("fukuoka_raw_data.csv", encoding="utf-8-sig")


if __name__ == "__main__":
    main()
