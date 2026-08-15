import os
import requests

RAKUTEN_APP_ID = "1068355966231154319"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

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

def search_rakuten():
    url = "https://app.rakuten.co.jp/services/api/IchibaItem/Search/20220601"
    params = {
        "applicationId": RAKUTEN_APP_ID,
        "keyword": TARGET["keyword"],
        "minPrice": TARGET["minPrice"],
        "maxPrice": TARGET["maxPrice"],
        "itemPurveyance": 1, 
        "sort": "+updateTimestamp", # 新着順
        "format": "json"
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code != 200: return
        items = res.json().get('Items', [])
        for i in items:
            item = i['Item']
            item_name = item['itemName']
            
            if "スピーディ40" in item_name: continue
            if any(word in item_name for word in EXCLUDE_WORDS): continue

            # 条件に合致した新着があれば通知
            msg = f"@everyone\n【楽天・新着】🔥本命スピーディ\n【品名】{item_name}\n【価格】{item['itemPrice']}円\n{item['itemUrl']}"
            send_discord(msg)
            break # 最上位の1件チェックで通知
    except Exception as e:
        print(f"エラー: {e}")

def send_discord(msg):
    if DISCORD_WEBHOOK_URL:
        requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})

if __name__ == "__main__":
    search_rakuten()
