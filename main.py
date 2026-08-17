import urllib.parse
import re
import requests
from bs4 import BeautifulSoup

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1468599693003980893/f88tz5FEhzgM5Yzo5IUzOk2NvJ5nDa1PxmDwALHeV7IhKMl_TDrDNsyKSkv31jrW9jVr"

KEYWORD = "ヴィトン モノグラム スピーディ"
MIN_PRICE = 25000
MAX_PRICE = 60000

EXCLUDE_WORDS = [
    "スピーディ40", "スタンプ", "印鑑", "はんこ", "インク", "リング", 
    "指輪", "ネックレス", "時計", "ミニチュア", "空箱", "ミニポシェット", 
    "ミニラン", "エベヌ", "チャーム", "アクセソワール"
]

def send_discord(msg):
    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})
        print(f"Discord送信ステータス: {res.status_code}")
    except Exception as e:
        print(f"Discord送信エラー: {e}")

def search_rakuten_html():
    encoded_kw = urllib.parse.quote(KEYWORD)
    # 楽天市場の一般検索URL（新着順・価格指定・中古指定）
    url = f"https://search.rakuten.co.jp/search/mall/{encoded_kw}/?min={MIN_PRICE}&max={MAX_PRICE}&s=4&used=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        print(f"楽天Webページステータス: {res.status_code}")
        
        if res.status_code != 200:
            return

        soup = BeautifulSoup(res.text, "html.parser")
        # 検索結果のアイテム要素を抽出
        items = soup.select(".searchresultitem, div[data-track-item-id]")
        if not items:
            items = soup.find_all("div", class_=re.compile(r"item"))
        
        print(f"解析検出件数: {len(items)}件")

        for item in items:
            title_elem = item.select_one(".title a, a[title], h2 a")
            if not title_elem:
                continue
            
            title = title_elem.get("title") or title_elem.text.strip()
            link = title_elem.get("href", "")
            
            if not title or not link:
                continue

            if any(word in title for word in EXCLUDE_WORDS):
                continue

            msg = f"@everyone\n【楽天・新着】🔥本命スピーディ\n【品名】{title}\n{link}"
            send_discord(msg)
            break

    except Exception as e:
        print(f"処理エラー: {e}")

if __name__ == "__main__":
    search_rakuten_html()
