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
    params = {
        "applicationId": RAKUTEN_APP_ID,
        "keyword": TARGET["keyword"],
        "minPrice": TARGET["minPrice"],
        "maxPrice": TARGET["maxPrice"],
        "itemPurveyance": 1, 
        "sort": "+updateTimestamp",
        "format": "json"
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code != 200:
            print(f"楽天APIエラー: {res.status_code}")
            return
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
    except Exception as e:
        print(f"処理エラー: {e}")

if __name__ == "__main__":
    send_discord("【動作テスト】GitHub Actionsから直接送信しています！")
    search_rakuten()
