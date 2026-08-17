import html
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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    try:
        res = requests.get(url, headers=headers, timeout=15)
        print(f"楽天Webページステータス: {res.status_code}")
        if res.status_code != 200:
            return

        page_text = res.text
        items = []

        # 1. 楽天の埋め込みNext.js JSONデータを抽出
        next_data_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', page_text)
        if next_data_match:
            try:
                data = json.loads(next_data_match.group(1))
                page_props = data.get("props", {}).get("pageProps", {})
                raw_items = page_props.get("items", []) or page_props.get("searchResult", {}).get("items", [])
                for it in raw_items:
                    title = it.get("itemName") or it.get("title") or ""
                    item_url = it.get("itemUrl") or it.get("url") or ""
                    price = it.get("itemPrice") or it.get("price") or ""
                    if title and item_url:
                        items.append({"title": title, "url": item_url, "price": price})
            except Exception as json_err:
                print(f"JSON解析エラー: {json_err}")

        # 2. JSONから取得できなかった場合のテキストパターン抽出（フォールバック）
        if not items:
            raw_data = re.findall(r'\{[^{}]*"itemUrl"\s*:\s*"([^"]+)"[^{}]*"itemName"\s*:\s*"([^"]+)"[^{}]*\}', page_text)
            for item_url, title_escaped in raw_data:
                try:
                    title = title_escaped.encode('utf-8').decode('unicode-escape')
                except Exception:
                    title = title_escaped
                items.append({"title": title, "url": item_url, "price": ""})

        print(f"抽出商品件数: {len(items)}件")

        # 3. 判定とDiscord通知
        for item in items:
            title = item["title"]
            item_url = item["url"]
            price = item.get("price", "")

            if any(word in title for word in EXCLUDE_WORDS):
                continue

            price_str = f"\n【価格】{price:,}円" if isinstance(price, int) and price > 0 else ""
            msg = f"@everyone\n【楽天・新着】🔥本命スピーディ\n【品名】{title}{price_str}\n{item_url}"
            send_discord(msg)
            print("Discordへ新着通知を送信完了")
            break

    except Exception as e:
        print(f"処理エラー: {e}")

if __name__ == "__main__":
    search_rakuten()
