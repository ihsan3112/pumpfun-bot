import os
import requests
from telebot import TeleBot
from telebot.types import Message
import time

# Ambil token dan user ID dari variabel environment (Railway)
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")

bot = TeleBot(BOT_TOKEN)

def format_number(n):
    return "{:,}".format(n)

def analyze_volume(volumes):
    v5, v1h, v24h = volumes
    if v5 > 0 and v1h > 0 and v24h > 0:
        if v5 < v1h / 10:
            return "⚠️ Volume 5m sangat kecil dibanding 1h = kemungkinan token melambat"
        elif v1h < v24h / 10:
            return "⚠️ Aktivitas 1 jam rendah dibanding 24 jam = momentum mungkin hilang"
        else:
            return "✅ Stabil: Token masih aktif dan volume sehat"
    return "⚠️ Volume sangat rendah = token mungkin tidak aktif"

@bot.message_handler(func=lambda m: True)
def handle_message(message: Message):
    mint = message.text.strip()

    if not mint or len(mint) < 32:
        bot.send_message(message.chat.id, "❌ Mint tidak valid atau terlalu pendek.")
        return

    bot.send_message(message.chat.id, f"🧠 Mengecek mint:\n{mint}")

    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{mint}"
    response = requests.get(url)

    if response.status_code != 200:
        time.sleep(3)
        response = requests.get(url)

    data = response.json()

    if not data.get("pair"):
        bot.send_message(message.chat.id, "⚠️ Token tidak ditemukan di Dexscreener. Coba lagi beberapa saat lagi.")
        return

    pair = data["pair"]
    supply = int(float(pair.get("baseToken", {}).get("totalSupply", 0)))
    liquidity = float(pair.get("liquidity", {}).get("usd", 0))
    volume_5m = float(pair.get("volume", {}).get("usd5m", 0))
    volume_1h = float(pair.get("volume", {}).get("h1", 0))
    volume_24h = float(pair.get("volume", {}).get("h24", 0))
    url_dex = pair.get("url", "")

    analisa = analyze_volume([volume_5m, volume_1h, volume_24h])

    pesan = (
        f"📦 Total Supply: {format_number(supply)}\n"
        f"💧 Liquidity: ${format_number(int(liquidity))}\n"
        f"📊 Volume (5m): ${format_number(int(volume_5m))}\n"
        f"📊 Volume (1h): ${format_number(int(volume_1h))}\n"
        f"📊 Volume (24h): ${format_number(int(volume_24h))}\n"
        f"📈 Analisa: {analisa}\n"
        f"🔗 Dexscreener: {url_dex}"
    )

    bot.send_message(message.chat.id, pesan)
    bot.send_message(message.chat.id, url_dex)

bot.infinity_polling(skip_pending=True)
