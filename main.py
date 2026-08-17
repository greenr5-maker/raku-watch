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

def search():
    session = requests.Session()
    
    # 楽天の公式検索API（スマートフォン用ヘッダー・国内IP偽装）
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
        "X-Forwarded-For": "133.242.0.1", # 日本国内IPのヘッダー偽装
        "Accept-Language": "ja-JP,ja;q=0.9"
    }

    # 1. 楽天ウェブ検索
    encoded_kw = urllib.parse.quote(KEYWORD)
    url = f"https://search.rakuten.co.jp/search/mall/{encoded_kw}/?min={MIN_PRICE}&max={MAX_PRICE}&s=4&used=1"

    try:
        res = session.get(url, headers=headers, timeout=15)
        print(f"受信HTML文字数: {len(res.text)}文字")
        
        # タイトルタグの確認（ブロックされているか判定）
        title_match = re.search(r'<title>(.*?)</title>', res.text, re.IGNORECASE)
        if title_match:
            print(f"取得ページタイトル: {title_match.group(1)}")

        # リンクの全探索（href属性の完全一致・部分一致）
        urls = re.findall(r'href=[\'"](https?://item\.rakuten\.co\.jp/[^\'"]+)[\'"]', res.text)
        print(f"抽出URL数: {len(urls)}件")

        if urls:
            target_url = urls[0].split("?")[0]
            send_discord(f"@everyone\n【楽天・新着検知】🔥スピーディ出品中\n{target_url}")
        else:
            # HTML先頭200文字を出力して原因を可視化
            clean_sample = re.sub(r'\s+', ' ', res.text[:250])
            print(f"HTML冒頭サンプル: {clean_sample}")

    except Exception as e:
        print(f"実行エラー: {e}")

if __name__ == "__main__":
    search()
