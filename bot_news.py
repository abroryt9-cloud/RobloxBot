import requests
import time
import random
import feedparser
import schedule
import threading
from datetime import datetime

# ============================================
# НАСТРОЙКИ (ЗАМЕНИ НА СВОИ)
# ============================================
TOKEN = "8940147419:AAE0Lf44YylpRWboKJ0n1S5vbZ88IVjUOwk"
CHANNEL_ID = -1004491058570  # ID канала с минусом

# ============================================
# СТИЛИ ДЛЯ НОВОСТЕЙ
# ============================================
EMOJIS = ["🔥", "🎮", "⚡", "🚀", "✨", "📢", "🎯", "🏆", "💎", "🤖"]
STARTERS = [
    "Срочно в Roblox! ",
    "Новость дня: ",
    "Внимание, игроки! ",
    "Горячая новость: ",
    "Для всех фанатов: "
]
ENDINGS = [
    " Что думаешь? 👇",
    " А ты уже попробовал? 🤔",
    " Делимся в комментариях! 💬",
    " Это важно! 🔥"
]

def change_style(title):
    emoji = random.choice(EMOJIS)
    starter = random.choice(STARTERS)
    ending = random.choice(ENDINGS)
    
    text = f"{emoji} <b>{starter}{title}</b>\n\n"
    text += f"{ending}\n"
    text += f"🕐 {datetime.now().strftime('%H:%M, %d.%m.%Y')}"
    
    return text

def get_news():
    rss_url = "https://news.google.com/rss/search?q=roblox&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    news_list = []
    for entry in feed.entries[:5]:
        news_list.append({
            "title": entry.title,
            "link": entry.link
        })
    return news_list

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        print(f"Ошибка: {e}")

def send_news_to_channel():
    news_list = get_news()
    if news_list:
        news = random.choice(news_list)
        styled = change_style(news['title'])
        styled += f"\n\n🔗 <a href='{news['link']}'>Читать полностью</a>"
        send_message(CHANNEL_ID, styled)
        print(f"✅ Новость отправлена в канал")

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.json().get("result", [])
    except:
        return []

def handle_commands():
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                chat_id = update["message"]["chat"]["id"]
                text = update["message"].get("text", "")
                
                if text == "/start":
                    send_message(chat_id, "🤖 Roblox News Bot\n/news — получить новость")
                elif text == "/news":
                    news_list = get_news()
                    if news_list:
                        news = random.choice(news_list)
                        styled = change_style(news['title'])
                        styled += f"\n\n🔗 <a href='{news['link']}'>Читать полностью</a>"
                        send_message(chat_id, styled)
                    else:
                        send_message(chat_id, "Новостей пока нет")
                else:
                    send_message(chat_id, "Используй /news")
            
            time.sleep(1)
        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(5)

def main():
    print("🤖 БОТ НОВОСТЕЙ ЗАПУЩЕН")
    schedule.every(3).hours.do(send_news_to_channel)
    
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    thread = threading.Thread(target=run_schedule)
    thread.daemon = True
    thread.start()
    
    handle_commands()

if __name__ == "__main__":
    main()