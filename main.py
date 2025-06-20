import os
import requests
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
            return "⚠️ Volume 5m sangat kecil dibanding 1h = kemungkinan token melambat"
        elif v1h < v24h / 10:
            return "⚠️ Aktivitas 1 jam rendah dibanding 24 jam = momentum mungkin hilang"
        else:
            return "✅ Stabil: Token masih aktif dan volume sehat"
    else:
        return "⚠️ Volume sangat rendah = token mungkin tidak aktif"

@bot.message_handler(func=lambda m: True)
def handle_message(message: Message):
    mint = message.text.strip()

    if not mint or len(mint) < 32:
        bot.send_message(message.chat.id, "❌ Mint tidak valid atau terlalu pendek.")
        return

    bot.send_message(message.chat.id, f"🧠 Mengecek mint:\n{mint}")

    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{mint}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200:
            bot.send_message(message.chat.id, f"⚠️ Gagal mengambil data dari Dexscreener (status {res.status_code})")
            return

        data = res.json()
        pair = data.get("pair")
        if not pair:
            bot.send_message(message.chat.id, "⚠️ Token tidak ditemukan di Dexscreener.")
            return

        name = pair.get("baseToken", {}).get("name", "")
        symbol = pair.get("baseToken", {}).get("symbol", "")
        supply = pair.get("baseToken", {}).get("totalSupply")
        liq = pair.get("liquidity", {}).get("usd")
        vol_5m = pair.get("volume", {}).get("m5", 0)
        vol_1h = pair.get("volume", {}).get("h1", 0)
        vol_24h = pair.get("volume", {}).get("h24", 0)
        url = pair.get("url", "")

        vol_analysis = analyze_volume([vol_5m, vol_1h, vol_24h])

        msg = (
            f"🧾 <b>{name} ({symbol})</b>\n"
            f"Total Supply: {format_number(int(float(supply)))}\n"
            f"Liquidity: ${format_number(round(liq))}\n"
            f"Volume (5m): ${format_number(round(vol_5m))}\n"
            f"Volume (1h): ${format_number(round(vol_1h))}\n"
            f"Volume (24h): ${format_number(round(vol_24h))}\n"
            f"<b>Analisa:</b> {vol_analysis}\n"
            f"<a href='{url}'>Dexscreener</a>"
        )

        bot.send_message(message.chat.id, msg, parse_mode="HTML", disable_web_page_preview=True)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Terjadi kesalahan: {str(e)}")

bot.infinity_polling()
