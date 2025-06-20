import os
import requests
import re
from telebot import TeleBot
from telebot.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")

bot = TeleBot(BOT_TOKEN)

def format_number(n):
    return "{:,}".format(n)

def analyze_volume(volumes):
    v5, v1h, v24h = volumes
    if v5 > 0 and v1h > 0 and v24h > 0:
        if v5 < v1h / 10:
            return "⚠️ Volume 5m kecil dibanding 1h → kemungkinan token melambat"
        elif v1h < v24h / 10:
            return "⚠️ Aktivitas 1 jam rendah dibanding 24 jam = momentum mungkin hilang"
        else:
            return "✅ Stabil: Token masih aktif dan volume sehat"
    else:
        return "⚠️ Volume sangat rendah = token mungkin tidak aktif"

@bot.message_handler(func=lambda m: True)
def handle_message(message: Message):
    raw_mint = message.text.encode('utf-8', 'ignore').decode('utf-8').strip()
    mint = re.sub(r'[^A-Za-z0-9]', '', raw_mint)

    if not mint or len(mint) < 32:
        bot.send_message(message.chat.id, "❌ Mint tidak valid atau terlalu pendek.")
        return

    bot.send_message(message.chat.id, f"🧠 Mengecek mint:\n`{mint}`", parse_mode="Markdown")

    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{mint}"
        response = requests.get(url)
        data = response.json()

        if "pair" not in data:
            bot.send_message(message.chat.id, "⚠️ Token tidak ditemukan di Dexscreener. Coba lagi beberapa saat lagi.")
            return

        pair = data["pair"]
        name = pair.get("baseToken", {}).get("name", "Unknown")
        symbol = pair.get("baseToken", {}).get("symbol", "")
        liquidity = float(pair.get("liquidity", {}).get("usd", 0))
        v5 = float(pair.get("volume", {}).get("m5", 0))
        v1h = float(pair.get("volume", {}).get("h1", 0))
        v24h = float(pair.get("volume", {}).get("h24", 0))
        url = pair.get("url", "")

        analysis = analyze_volume((v5, v1h, v24h))
        msg = (
            f"💧 Total Supply: {format_number(int(pair['baseToken']['totalSupply']))}\n"
            f"💰 Liquidity: ${format_number(liquidity)}\n"
            f"📊 Volume (5m): ${format_number(v5)}\n"
            f"📊 Volume (1h): ${format_number(v1h)}\n"
            f"📊 Volume (24h): ${format_number(v24h)}\n"
            f"📉 Analisa: {analysis}\n"
            f"🔗 Dexscreener: {url}"
        )
        bot.send_message(message.chat.id, msg)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

bot.polling()
