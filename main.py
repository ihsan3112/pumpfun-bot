import os
import requests
import time
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
            return "⚠️ Volume 5m sangat kecil dibanding 1h = kemungkinan token melambat"
        elif v1h < v24h / 10:
            return "⚠️ Aktivitas 1 jam rendah dibanding 24 jam = momentum mungkin hilang"
        else:
            return "✅ Stabil: Token masih aktif dan volume sehat"
    return "⚠️ Volume sangat rendah = token mungkin tidak aktif"

def fetch_token_data(mint):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{mint}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("pair") is None:
                time.sleep(1)
                response = requests.get(url, timeout=5)
                data = response.json()
            return data.get("pair")
        return None
    except Exception:
        return None

@bot.message_handler(func=lambda m: True)
def handle_message(message: Message):
    mint = message.text.strip()

    if not mint or len(mint) < 32:
        bot.send_message(message.chat.id, "❌ Mint tidak valid atau terlalu pendek.")
        return

    bot.send_message(message.chat.id, f"🧠 Mengecek mint:\n{mint}")

    pair_data = fetch_token_data(mint)
    if not pair_data:
        bot.send_message(message.chat.id, "⚠️ Token tidak ditemukan di Dexscreener. Coba lagi beberapa saat lagi.")
        return

    try:
        total_supply = format_number(int(pair_data.get("totalSupply", 0)))
        liquidity = f"${format_number(round(float(pair_data['liquidity']['usd']), 2))}"
        vol_5m = float(pair_data['volume']['usd']['m5'])
        vol_1h = float(pair_data['volume']['usd']['h1'])
        vol_24h = float(pair_data['volume']['usd']['h24'])

        volume_analysis = analyze_volume((vol_5m, vol_1h, vol_24h))

        message_text = (
            f"📦 Total Supply: {total_supply}\n"
            f"💧 Liquidity: {liquidity}\n"
            f"📊 Volume (5m): ${format_number(round(vol_5m))}\n"
            f"📊 Volume (1h): ${format_number(round(vol_1h))}\n"
            f"📊 Volume (24h): ${format_number(round(vol_24h))}\n"
            f"\n🔎 Analisa: {volume_analysis}\n"
            f"🔗 Dexscreener: {pair_data['url']}"
        )

        bot.send_message(message.chat.id, message_text)
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Gagal membaca data token. Error: {str(e)}")

bot.polling()
