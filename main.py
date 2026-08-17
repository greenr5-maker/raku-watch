import time
import requests

RAKUTEN_APP_ID = "1068355966231154319"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1468599693003980893/f88tz5FEhzgM5Yzo5IUzOk2NvJ5nDa1PxmDwALHeV7IhKMl_TDrDNsyKSkv31jrW9jVr"

TARGET = {
    "keyword": "ヴィトン モノグラム スピーディ",
    "minPrice": 25000,
    "maxPrice": 60000
}

EXCLUDE_WORDS = [
    "スタンプ", "印鑑", "はんこ", "インク", "リング", "指輪", "ネックレス", 
    "時計", "ミニチュア", "空箱", "ミニポシェット", "ミニラン", "エベヌ", 
    "チャーム", "アクセソワール"
]

def send_discord(msg):
    try:
        res = requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})
        print(f"Discord送信ステータス: {res.status_code}")
    except Exception as e:
        print(f"Discord送信エラー: {e}")

def search_rakuten():
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    params = {
        "applicationId": RAKUTEN_APP_ID,
        "keyword": TARGET["keyword"],
        "minPrice": TARGET["minPrice"],
        "maxPrice": TARGET["maxPrice"],
        "sort": "+updateTimestamp",
        "format": "json"
    }
    
    # 503対策：最大3回まで再試行
    for attempt in range(3):
        try:
            res = requests.get(url, params=params, headers=headers, timeout=10)
            print(f"楽天APIステータス (試行{attempt + 1}): {res.status_code}")
            
            if res.status_code == 200:
                items = res.json().get('Items', [])
                print(f"取得件数: {len(items)}件")
                
                for i in items:
                    item = i['Item']
                    item_name = item['itemName']
                    
                    if "スピーディ40" in item_name: continue
                    if any(word in item_name for word in EXCLUDE_WORDS): continue

                    msg = f"@everyone\n【楽天・新着】🔥本命スピーディ\n【品名】{item_name}\n【価格】{item['itemPrice']}円\n{item['itemUrl']}"
                    send_discord(msg)
                    break
                return
            elif res.status_code == 503:
                time.sleep(2)  # 2秒待って再試行
        except Exception as e:
            print(f"通信エラー: {e}")
            time.sleep(2)

if __name__ == "__main__":
    search_rakuten()
