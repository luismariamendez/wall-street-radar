import os
import requests
import feedparser
from datetime import datetime
from deep_translator import GoogleTranslator

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

FEEDS = {
    "Reuters": "https://news.google.com/rss/search?q=site:reuters.com+Fed+OR+markets+OR+stocks+OR+inflation+OR+tariffs&hl=en-US&gl=US&ceid=US:en",
    "Bloomberg": "https://news.google.com/rss/search?q=site:bloomberg.com+Fed+OR+markets+OR+stocks+OR+inflation+OR+tariffs&hl=en-US&gl=US&ceid=US:en",
    "Wall Street Journal": "https://news.google.com/rss/search?q=site:wsj.com+Fed+OR+markets+OR+stocks+OR+inflation+OR+tariffs&hl=en-US&gl=US&ceid=US:en",
    "Financial Times": "https://news.google.com/rss/search?q=site:ft.com+Fed+OR+markets+OR+stocks+OR+inflation+OR+tariffs&hl=en-US&gl=US&ceid=US:en",
    "Trump / Política USA": "https://news.google.com/rss/search?q=Trump+tariffs+OR+China+OR+Fed+OR+Powell+OR+oil+OR+markets&hl=en-US&gl=US&ceid=US:en",
}

CATEGORIES = {
    "🏦 Fed / Tasas": ["fed", "powell", "rate cut", "rate hike", "interest rates", "federal reserve"],
    "📈 Inflación": ["cpi", "pce", "inflation", "prices"],
    "💼 Empleo": ["jobs", "payrolls", "unemployment", "wages"],
    "💵 Bonos / Dólar": ["treasury", "yield", "10-year", "dollar", "bond"],
    "🤖 IA / Semiconductores": ["nvidia", "ai", "semiconductor", "chips", "apple", "microsoft", "google"],
    "🏦 Bancos / Crédito": ["banks", "credit", "default", "debt", "loan"],
    "🛢️ Energía": ["oil", "gas", "energy", "opec"],
    "🌎 Geopolítica / Política": ["trump", "china", "tariffs", "iran", "war", "sanctions", "white house"]
}

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

def analyze_news(title):
    text = title.lower()
    score = 0
    categories = []

    for category, keywords in CATEGORIES.items():
        hits = sum(1 for word in keywords if word in text)
        if hits > 0:
            categories.append(category)
            score += hits

    if "trump" in text and ("tariff" in text or "china" in text or "fed" in text or "oil" in text):
        score += 3

    if score >= 5:
        impact = "🔥 Impacto ALTO"
    elif score >= 3:
        impact = "⚠️ Impacto MEDIO"
    else:
        impact = "🟡 Impacto BAJO"

    return impact, score, categories

def main():
    sent_count = 0

    for source, feed_url in FEEDS.items():
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:
            title = entry.title
            link = entry.link

            impact, score, categories = analyze_news(title)

            # SOLO NOTICIAS DE ALTO IMPACTO
            if score >= 5:
                title_es = translate_to_spanish(title)

                message = (
                    f"<b>{impact}</b>\n"
                    f"<b>Fuente:</b> {source}\n"
                    f"<b>Score:</b> {score}/10\n"
                    f"<b>Categoría:</b> {', '.join(categories)}\n\n"
                    f"<b>📰 Titular traducido:</b>\n"
                    f"{title_es}\n\n"
                    f"<b>Original:</b>\n"
                    f"{title}\n\n"
                    f"{link}\n\n"
                    f"Hora: {datetime.now().strftime('%H:%M')}"
                )

                send_telegram(message)
                sent_count += 1

    if sent_count == 0:
        send_telegram("✅ Wall Street Radar revisó noticias. No encontró alertas de ALTO impacto en este momento.")

if __name__ == "__main__":
    main()
