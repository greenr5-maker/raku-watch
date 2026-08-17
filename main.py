import html
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        print(f"楽天Webページステータス: {res.status_code}")
        if res.status_code != 200:
            return

        page_text = res.text
        
        # 1. ページ内にある「https://item.rakuten.co.jp/...」形式のURLを網羅的に全抽出
        raw_urls = re.findall(r'https?://item\.rakuten\.co\.jp/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+/?', page_text)
        
        # 2. ショップトップ以外の個別商品URLのみに絞り込み・重複除外
        unique_urls = []
        for u in raw_urls:
            clean_u = u.rstrip("/")
            # ショップトップURLを除外（/shopname/itemid の2階層になっているもの）
            parts = clean_u.replace("https://item.rakuten.co.jp/", "").split("/")
            if len(parts) >= 2 and clean_u not in unique_urls:
                unique_urls.append(clean_u)

        print(f"抽出商品URL件数: {len(unique_urls)}件")

        if not unique_urls:
            print("商品URLが見つかりませんでした")
            return

        # 3. 最新商品の判定とDiscord通知
        for item_url in unique_urls:
            # ページ内から該当URL近辺のタイトル文字列を抽出（見つからない場合は初期タイトル）
            escaped_url = re.escape(item_url)
            match = re.search(rf'{escaped_url}[^>]*?>([\s\S]*?)</a>', page_text)
            
            title = ""
            if match:
                title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                title = html.unescape(title)
            
            if not title or len(title) < 5:
                title = "【楽天新着】ルイヴィトン モノグラム スピーディ"

            if any(word in title for word in EXCLUDE_WORDS):
                continue

            msg = f"@everyone\n【楽天・新着】🔥本命スピーディ\n【品名】{title}\n{item_url}"
            send_discord(msg)
            print(f"Discordへ送信完了: {item_url}")
            break

    except Exception as e:
        print(f"処理エラー: {e}")

if __name__ == "__main__":
    search_rakuten()
