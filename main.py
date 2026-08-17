import json
import re
import urllib.parse
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        print(f"楽天Webページステータス: {res.status_code}")
        if res.status_code != 200:
            return

        # 楽天検索ページ内のアイテム一覧データを抽出
        items = []
        
        # 1. ページ内の埋め込みJSON（items配列）を検索
        json_matches = re.findall(r'"itemUrl"\s*:\s*"(https://item\.rakuten\.co\.jp/[^"]+)"\s*,\s*"itemName"\s*:\s*"([^"]+)"', res.text)
        if json_matches:
            for url_str, name in json_matches:
                items.append({"title": name.encode('utf-8').decode('unicode-escape', 'ignore'), "url": url_str})
        
        # 2. 通常リンクタグからの抽出（フォールバック）
        if not items:
            link_matches = re.findall(r'<a[^>]+href="(https://item\.rakuten\.co\.jp/[^"]+)"[^>]*>([\s\S]*?)</a>', res.text)
            for url_str, raw_text in link_matches:
                clean_title = re.sub(r'<[^>]+>', '', raw_text).strip()
                if "スピーディ" in clean_title and len(clean_title) > 10:
                    items.append({"title": clean_title, "url": url_str})

        print(f"解析検出件数: {len(items)}件")

        for item in items:
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
