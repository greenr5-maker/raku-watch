import urllib.parse
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

def search_rakuten():
    encoded_kw = urllib.parse.quote(KEYWORD)
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
        
        # 楽天検索結果の全商品リンクを走査
        item_links = soup.find_all("a", href=lambda h: h and "item.rakuten.co.jp" in h)
        print(f"検出リンク総数: {len(item_links)}件")

        valid_items = []
        seen_urls = set()

        for a in item_links:
            href = a.get("href", "").split("?")[0] # URLパラメータを除去
            title = a.get("title") or a.get_text(strip=True)
            
            if not title or len(title) < 10 or href in seen_urls:
                continue
            
            seen_urls.add(href)
            valid_items.append({"title": title, "url": href})

        print(f"有効商品件数: {len(valid_items)}件")

        for item in valid_items:
            title = item["title"]
            item_url = item["url"]

            if any(word in title for word in EXCLUDE_WORDS):
                continue

            msg = f"@everyone\n【楽天・新着】🔥本命スピーディ\n【品名】{title}\n{item_url}"
            send_discord(msg)
            print("Discordへ新着通知を送信しました")
            break

    except Exception as e:
        print(f"処理エラー: {e}")

if __name__ == "__main__":
    search_rakuten()
