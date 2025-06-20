import os
import requests
from telebot import TeleBot
from telebot.types import Message
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")

bot = TeleBot(BOT_TOKEN)

def format_number(n):
    return "{:,}".format(n)

def analyze_volume(v5, v1h, v24h, token_age_minute):
    if token_age_minute < 5:
        return "⏳ Token terlalu baru, belum cukup data volume."
    elif token_age_minute < 60:
        if v5 < v1h / 10:
            return "⚠️ Volume 5m kecil dibanding 1h → token melambat"
        elif v1h < v24h / 10:
            return "⚠️ Aktivitas 1 jam rendah dibanding 24 jam → momentum menurun"
        else:
            return "✅ Stabil: Token masih aktif dan volume sehat"
    else:
        if v1h < v24h / 15:
            return "⚠️ Aktivitas jam ini menurun → token mulai ditinggal"
        else:
            return "✅ Volume tetap stabil > 1 jam"

@bot.message_handler(func=lambda m: True)
def handle_message(message: Message):
    mint = message.text.strip()
    if not mint or len(mint) < 32:
        bot.send_message(message.chat.id, "❌ Mint tidak valid atau terlalu pendek.")
        return

    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{mint}"
    try:
        res = requests.get(url, timeout=10).json()
        pair = res.get("pair")
        if not pair:
            bot.send_message(message.chat.id, "⚠️ Token belum muncul di Dexscreener.")
            return

        name = pair.get("baseToken", {}).get("name", "-")
        supply = pair.get("baseToken", {}).get("totalSupply", "???")
        link = pair.get("url")
        liq = pair.get("liquidity", {}).get("usd", 0)
        vol_5m = pair.get("volume", {}).get("m5", 0)
        vol_1h = pair.get("volume", {}).get("h1", 0)
        vol_24h = pair.get("volume", {}).get("h24", 0)
        created_ms = pair.get("pairCreatedAt", 0)
        age_min = (datetime.now() - datetime.fromtimestamp(created_ms / 1000)).seconds // 60

        analysis = analyze_volume(vol_5m, vol_1h, vol_24h, age_min)
        msg = (
            f"📦 *{name}*\n"
            f"💧 Liquidity: ${format_number(int(liq))}\n"
            f"⏱️ Age: {age_min} menit\n"
            f"📊 Vol 5m: ${format_number(int(vol_5m))}\n"
            f"📊 Vol 1h: ${format_number(int(vol_1h))}\n"
            f"📊 Vol 24h: ${format_number(int(vol_24h))}\n"
            f"\n🧠 Analisa: {analysis}\n\n"
            f"[🔗 Dexscreener]({link})"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Gagal mengambil data: {e}")

if __name__ == "__main__":
    print("Bot siap menerima perintah...")
    bot.infinity_polling()
