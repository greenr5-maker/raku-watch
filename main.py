import urllib.parse
import re
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

def search_rakuten():
    encoded_kw = urllib.parse.quote(KEYWORD)
    url = f"https://search.rakuten.co.jp/search/mall/{encoded_kw}/?min={MIN_PRICE}&max={MAX_PRICE}&s=4&used=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        print(f"楽天Webページステータス: {res.status_code}")
        if res.status_code != 200:
            return

        # HTMLから商品タイトルとURLを抽出
        pattern = r'<a[^>]+href="(https://item\.rakuten\.co\.jp/[^"]+)"[^>]*title="([^"]+)"'
        matches = re.findall(pattern, res.text)
        
        # タイトル属性が逆順になっているパターンのフォールバック
        if not matches:
            pattern = r'<a[^>]+title="([^"]+)"[^>]*href="(https://item\.rakuten\.co\.jp/[^"]+)"'
            matches = [(url, title) for title, url in re.findall(pattern, res.text)]

        print(f"解析検出件数: {len(matches)}件")

        for item_url, title in matches:
            if any(word in title for word in EXCLUDE_WORDS):
                continue

            msg = f"@everyone\n【楽天・新着】🔥本命スピーディ\n【品名】{title}\n{item_url}"
            send_discord(msg)
            break

    except Exception as e:
        print(f"処理エラー: {e}")

if __name__ == "__main__":
    search_rakuten()
