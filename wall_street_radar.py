import os
import json
import requests
import feedparser
from datetime import datetime
from deep_translator import GoogleTranslator

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SENT_LINKS_FILE = "sent_links.json"

FEEDS = {
    "Reuters": "https://news.google.com/rss/search?q=site:reuters.com+Fed+OR+markets+OR+stocks+OR+inflation+OR+tariffs+OR+Samsung+OR+SK+Hynix+OR+South+Korea+OR+Korea+chips&hl=en-US&gl=US&ceid=US:en",
    "Bloomberg": "https://news.google.com/rss/search?q=site:bloomberg.com+Fed+OR+markets+OR+stocks+OR+inflation+OR+tariffs+OR+Samsung+OR+SK+Hynix+OR+South+Korea+OR+Korea+chips&hl=en-US&gl=US&ceid=US:en",
    "Wall Street Journal": "https://news.google.com/rss/search?q=site:wsj.com+Fed+OR+markets+OR+stocks+OR+inflation+OR+tariffs+OR+Samsung+OR+SK+Hynix+OR+South+Korea+OR+Korea+chips&hl=en-US&gl=US&ceid=US:en",
    "Financial Times": "https://news.google.com/rss/search?q=site:ft.com+Fed+OR+markets+OR+stocks+OR+inflation+OR+tariffs+OR+Samsung+OR+SK+Hynix+OR+South+Korea+OR+Korea+chips&hl=en-US&gl=US&ceid=US:en",
    "Trump / Política USA": "https://news.google.com/rss/search?q=Trump+tariffs+OR+China+OR+Fed+OR+Powell+OR+oil+OR+markets+OR+semiconductors&hl=en-US&gl=US&ceid=US:en",
    "Corea / KORU": "https://news.google.com/rss/search?q=South+Korea+stocks+OR+Samsung+Electronics+OR+SK+Hynix+OR+Korean+won+OR+Bank+of+Korea+OR+North+Korea+OR+Korea+semiconductors+OR+HBM&hl=en-US&gl=US&ceid=US:en",
}

CATEGORIES = {
    "🏦 Fed / Tasas": ["fed", "powell", "rate cut", "rate hike", "interest rates", "federal reserve"],
    "📈 Inflación": ["cpi", "pce", "inflation", "prices"],
    "💼 Empleo": ["jobs", "payrolls", "unemployment", "wages"],
    "💵 Bonos / Dólar": ["treasury", "yield", "10-year", "dollar", "bond"],
    "🤖 IA / Semiconductores": ["nvidia", "ai", "semiconductor", "chips", "apple", "microsoft", "google", "broadcom", "amd", "tsmc", "arm", "hbm"],
    "🏦 Bancos / Crédito": ["banks", "credit", "default", "debt", "loan"],
    "🛢️ Energía": ["oil", "gas", "energy", "opec"],
    "🌎 Geopolítica / Política": ["trump", "china", "tariffs", "iran", "war", "sanctions", "white house"],
    "🇰🇷 Corea / KORU": ["south korea", "korea", "korean", "samsung", "sk hynix", "hynix", "bank of korea", "korean won", "won", "north korea", "kospi", "hbm", "dram"]
}

PORTFOLIO_MAP = {
    "KORU": ["south korea", "korea", "korean", "samsung", "sk hynix", "hynix", "kospi", "bank of korea", "korean won", "won", "north korea", "hbm", "dram"],
    "AVGO": ["broadcom", "avgo", "ai chips", "semiconductor", "vmware"],
    "ARM": ["arm", "softbank", "chip design", "semiconductor"],
    "VRT": ["vertiv", "data center", "datacenter", "ai infrastructure", "power cooling"],
    "NVDA": ["nvidia", "gpu", "ai chips", "hbm"],
    "AMD": ["amd", "gpu", "mi300", "mi350", "ai chips"],
    "TSMC": ["tsmc", "taiwan semiconductor", "foundry", "chips"],
    "BITX / Bitcoin": ["bitcoin", "btc", "crypto", "spot bitcoin etf", "coinbase", "microstrategy", "mstr"],
}

def load_sent_links():
    try:
        with open(SENT_LINKS_FILE, "r", encoding="utf-8") as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()
    except json.JSONDecodeError:
        return set()

def save_sent_links(sent_links):
    with open(SENT_LINKS_FILE, "w", encoding="utf-8") as file:
        json.dump(list(sent_links)[-500:], file, ensure_ascii=False, indent=2)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
    )
    print(response.text)

def translate_to_spanish(text):
    try:
        return GoogleTranslator(source="auto", target="es").translate(text)
    except Exception:
        return text

def detect_portfolio_impact(title):
    text = title.lower()
    impacted = []

    for asset, keywords in PORTFOLIO_MAP.items():
        if any(word in text for word in keywords):
            impacted.append(asset)

    return impacted

def analyze_news(title):
    text = title.lower()
    score = 0
    categories = []

    for category, keywords in CATEGORIES.items():
        hits = sum(1 for word in keywords if word in text)
        if hits > 0:
            categories.append(category)
            score += hits

    if "trump" in text and ("tariff" in text or "tariffs" in text or "china" in text or "fed" in text or "oil" in text or "semiconductor" in text):
        score += 3

    if "powell" in text or "federal reserve" in text:
        score += 2

    if "cpi" in text or "pce" in text or "payrolls" in text:
        score += 2

    if "south korea" in text or "samsung" in text or "sk hynix" in text or "north korea" in text:
        score += 3

    if "hbm" in text or "dram" in text or "memory chip" in text:
        score += 2

    if score >= 5:
        impact = "🔥 Impacto ALTO"
    elif score >= 3:
        impact = "⚠️ Impacto MEDIO"
    else:
        impact = "🟡 Impacto BAJO"

    return impact, score, categories

def main():
    sent_links = load_sent_links()
    new_sent = 0

    for source, feed_url in FEEDS.items():
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:8]:
            title = entry.title
            link = entry.link

            if link in sent_links:
                continue

            impact, score, categories = analyze_news(title)
            impacted_assets = detect_portfolio_impact(title)

            if score >= 5:
                title_es = translate_to_spanish(title)

                cartera_text = "No detectado"
                if impacted_assets:
                    cartera_text = ", ".join(impacted_assets)

                message = (
                    f"<b>{impact}</b>\n"
                    f"<b>Fuente:</b> {source}\n"
                    f"<b>Score:</b> {score}/10\n"
                    f"<b>Categoría:</b> {', '.join(categories)}\n"
                    f"<b>🎯 Puede afectar:</b> {cartera_text}\n\n"
                    f"<b>📰 Titular traducido:</b>\n"
                    f"{title_es}\n\n"
                    f"<b>Original:</b>\n"
                    f"{title}\n\n"
                    f"{link}\n\n"
                    f"Hora: {datetime.now().strftime('%H:%M')}"
                )

                send_telegram(message)
                sent_links.add(link)
                new_sent += 1

    save_sent_links(sent_links)

    if new_sent == 0:
        print("Sin noticias nuevas de ALTO impacto.")

if __name__ == "__main__":
    main()
