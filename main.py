import urllib.parse
import xml.etree.ElementTree as ET
import requests

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

def check_rakuten_rss():
    encoded_kw = urllib.parse.quote(KEYWORD)
    # 楽天市場の公式新着RSSフィード（価格帯・新着ソート指定）
    rss_url = f"https://rss.rakuten.co.jp/search/item/all/?keyword={encoded_kw}&min={MIN_PRICE}&max={MAX_PRICE}&sort=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0"
    }

    try:
        res = requests.get(rss_url, headers=headers, timeout=15)
        print(f"楽天RSSステータス: {res.status_code}")
        
        if res.status_code != 200:
            return

        # XML解析
        root = ET.fromstring(res.content)
        items = root.findall(".//item")
        print(f"取得件数: {len(items)}件")

        for item in items:
            title = item.find("title").text if item.find("title") is not None else ""
            link = item.find("link").text if item.find("link") is not None else ""
            description = item.find("description").text if item.find("description") is not None else ""

            if any(word in title for word in EXCLUDE_WORDS):
                continue

            msg = f"@everyone\n【楽天・新着】🔥本命スピーディ\n【品名】{title}\n{link}"
            send_discord(msg)
            break

    except Exception as e:
        print(f"処理エラー: {e}")

if __name__ == "__main__":
    check_rakuten_rss()
