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
    # 楽天市場の一般検索（新着順・価格指定・中古指定）
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

        page_text = res.text
        
        # 1. ページ内の商品URL（https://item.rakuten.co.jp/ショップ名/商品ID/）を全抽出
        raw_urls = re.findall(r'https?://item\.rakuten\.co\.jp/[a-zA-Z0-9_\-]+/[a-zA-Z0-9_\-]+/?', page_text)
        
        # 重複を除去（順番を維持）
        unique_urls = list(dict.fromkeys(raw_urls))
        print(f"検出URL件数: {len(unique_urls)}件")

        # 2. 各リンクに対応する商品名・テキストブロックを探索
        items = []
        for item_url in unique_urls:
            # URL周辺のHTMLから日本語の商品名を抽出
            clean_url = item_url.rstrip("/")
            escaped_url = re.escape(clean_url)
            match = re.search(rf'href=["\']?{escaped_url}/?["\']?[^>]*>([\s\S]*?)</a>', page_text)
            
            title = ""
            if match:
                title = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                title = html.unescape(title)
            
            if not title:
                title = "ルイヴィトン モノグラム スピーディ（楽天市場新着）"

            items.append({"title": title, "url": item_url})

        print(f"処理対象商品数: {len(items)}件")

        # 3. 除外条件を判定してDiscordへ送信
        for item in items:
            title = item["title"]
            item_url = item["url"]

            if any(word in title for word in EXCLUDE_WORDS):
                continue

            msg = f"@everyone\n【楽天・新着】🔥本命スピーディ\n【品名】{title}\n{item_url}"
            send_discord(msg)
            print("Discordへ新着通知を送信完了")
            break

    except Exception as e:
        print(f"処理エラー: {e}")

if __name__ == "__main__":
    search_rakuten()
