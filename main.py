import os
import requests
from telebot import TeleBot
from telebot.types import Message

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
            return "⚠️ Volume 5m sangat kecil dibanding 1h → kemungkinan token melambat"
        elif v1h < v24h / 10:
            return "⚠️ Aktivitas 1 jam rendah dibanding 24 jam → momentum mungkin hilang"
        else:
            return "✅ Stabil: Token masih aktif dan volume sehat"
    return "⚠️ Volume sangat rendah → token mungkin tidak aktif"

@bot.message_handler(func=lambda m: True)
def handle_message(message: Message):
    mint = message.text.strip()
    
    if not mint or len(mint) < 32:
        bot.send_message(message.chat.id, "❌ Mint tidak valid atau terlalu pendek.")
        return

    bot.send_message(message.chat.id, f"🧠 Menerima mint:\n`{mint}`", parse_mode="Markdown")

    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{mint}"
    response = requests.get(url)

    if response.status_code != 200:
        bot.send_message(message.chat.id, "❌ Gagal mengambil data dari Dexscreener.")
        return

    data = response.json()

    if "pair" not in data:
        bot.send_message(message.chat.id, "⚠️ Token belum muncul di Dexscreener (mungkin terlalu baru)")
        return

    pair = data["pair"]
    supply = pair.get("totalSupply", 0)
    liquidity = pair.get("liquidity", {}).get("usd", 0)
    vol5m = pair.get("volume", {}).get("m5", 0)
    vol1h = pair.get("volume", {}).get("h1", 0)
    vol24h = pair.get("volume", {}).get("h24", 0)
    url = pair.get("url", "")

    status = analyze_volume((vol5m, vol1h, vol24h))

    reply = (
        f"📦 Total Supply: {format_number(int(supply))}\n"
        f"💧 Liquidity: ${format_number(int(liquidity))}\n"
        f"📊 Volume (5m): ${format_number(int(vol5m))}\n"
        f"📊 Volume (1h): ${format_number(int(vol1h))}\n"
        f"📊 Volume (24h): ${format_number(int(vol24h))}\n"
        f"🧠 Analisa: {status}\n\n"
        f"[🔗 Dexscreener]({url})"
    )

    bot.send_message(message.chat.id, reply, parse_mode="Markdown")

print("Bot siap menerima perintah...")
bot.infinity_polling()
