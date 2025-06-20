import os
import requests
import time
from telebot import TeleBot
from telebot.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")

bot = TeleBot(BOT_TOKEN)

def format_number(n):
    return "{:,}".format(n)

def calculate_score(v5, v1h, v24h, mc, liq):
    score = 0
    log = []

    if v5 > 0 and v1h > 0 and v24h > 0:
        if v5 >= v1h / 5:
            score += 1
            log.append("✅ Volume 5m aktif")
        else:
            log.append("⚠️ Volume 5m rendah")

        if v1h >= v24h / 10:
            score += 1
            log.append("✅ Aktivitas 1 jam tinggi")
        else:
            log.append("⚠️ Aktivitas 1 jam melambat")
    else:
        log.append("⚠️ Salah satu volume kosong")

    if mc > liq:
        score += 1
        log.append("✅ MC lebih besar dari Liquidity")
    else:
        log.append("⚠️ MC lebih kecil dari Liquidity")

    if liq > 5000:
        score += 1
        log.append("✅ Likuiditas sehat")
    else:
        log.append("⚠️ Likuiditas kecil")

    if v24h > 10000:
        score += 1
        log.append("✅ Volume 24 jam sehat")
    else:
        log.append("⚠️ Volume 24 jam kecil")

    return score, log

def fetch_token_data(mint):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{mint}"
    for attempt in range(3):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        time.sleep(2)
    return None

@bot.message_handler(func=lambda m: True)
def handle_message(message: Message):
    mint = message.text.strip()
    bot.send_message(message.chat.id, f"🧠 Mengecek mint:\n{mint}")

    if not mint or len(mint) < 32:
        bot.send_message(message.chat.id, "❌ Mint tidak valid atau terlalu pendek.")
        return

    data = fetch_token_data(mint)
    if not data or not data.get("pair"):
        bot.send_message(message.chat.id, "⚠️ Token tidak ditemukan di Dexscreener. Coba lagi beberapa saat lagi.")
        return

    pair = data["pair"]
    v5 = float(pair.get("volume", {}).get("m5", 0))
    v1h = float(pair.get("volume", {}).get("h1", 0))
    v24h = float(pair.get("volume", {}).get("h24", 0))
    mc = float(pair.get("fdv", 0))
    liq = float(pair.get("liquidity", {}).get("usd", 0))

    score, analysis = calculate_score(v5, v1h, v24h, mc, liq)

    text = (
        f"Total Supply: {format_number(pair.get('totalSupply', 0))}\n"
        f"Liquidity: ${format_number(liq)}\n"
        f"Volume (5m): ${format_number(v5)}\n"
        f"Volume (1h): ${format_number(v1h)}\n"
        f"Volume (24h): ${format_number(v24h)}\n"
        f"MarketCap: ${format_number(mc)}\n"
        f"Score: {score}/5\n\n"
        f"Analisa:\n" + '\n'.join(analysis) + "\n\n"
        f"🔗 Dexscreener: {pair.get('url')}"
    )

    bot.send_message(message.chat.id, text)

if __name__ == '__main__':
    print("Bot sedang berjalan...")
    bot.infinity_polling()
