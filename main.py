import requests

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1468599693003980893/f88tz5FEhzgM5Yzo5IUzOk2NvJ5nDa1PxmDwALHeV7IhKMl_TDrDNsyKSkv31jrW9jVr"
RAKUTEN_APP_ID = "1068355966231154319"

TARGET_KEYWORD = "ヴィトン モノグラム スピーディ"
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
    # 安定版エンドポイント（20170706）
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20170706"
    
    params = {
        "applicationId": RAKUTEN_APP_ID,
        "keyword": TARGET_KEYWORD,
        "minPrice": MIN_PRICE,
        "maxPrice": MAX_PRICE,
        "sort": "+updateTimestamp",
        "format": "json",
        "hits": 30
    }

    try:
        res = requests.get(url, params=params, timeout=15)
        print(f"楽天APIステータス: {res.status_code}")
        
        if res.status_code != 200:
            print(f"エラーレスポンス: {res.text[:200]}")
            return

        data = res.json()
        items = data.get("Items", [])
        print(f"取得アイテム件数: {len(items)}件")

        for item_data in items:
            item = item_data.get("Item", {})
            title = item.get("itemName", "")
            item_url = item.get("itemUrl", "")
            price = item.get("itemPrice", 0)

            if not title or not item_url:
                continue

            if any(word in title for word in EXCLUDE_WORDS):
                continue

            msg = f"@everyone\n【楽天・新着】🔥本命スピーディ\n【品名】{title}\n【価格】{price:,}円\n{item_url}"
            send_discord(msg)
            print(f"Discordへ新着通知を送信しました: {title[:20]}...")
            break

    except Exception as e:
        print(f"処理エラー: {e}")

if __name__ == "__main__":
    search_rakuten()
