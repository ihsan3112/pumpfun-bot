 import os
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")
bot = telebot.TeleBot(TOKEN)

def fetch_token_data(mint):
    url = f"https://public-api.birdeye.so/public/token/{mint}"
    headers = {"X-API-KEY": "birdeye_public_api_key"}  # ganti dengan API key jika perlu
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def fetch_dexscreener_data(mint):
    url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{mint}"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return None

def build_reply(mint_address):
    token_data = fetch_token_data(mint_address)
    dexs_data = fetch_dexscreener_data(mint_address)

    if not token_data:
        return f"⚠️ Mint tidak valid atau tidak ditemukan: {mint_address}"

    reply = f"🧠 Menerima mint:\n{mint_address}\n"
    reply += f"📦 Total Supply: {token_data.get('data', {}).get('supply', 'Unknown')}\n"

    if not dexs_data or not dexs_data.get("pair"):
        reply += "⚠️ Token belum muncul di Dexscreener (mungkin terlalu baru)"
        return reply

    pair = dexs_data["pair"]
    liq = pair.get("liquidity", {})
    vol = pair.get("volume", {})
    reply += f"💧 Liquidity: ${liq.get('usd', 'N/A')}\n"
    reply += f"📈 Volume (5m): ${vol.get('m5', 'N/A')}\n"
    reply += f"📈 Volume (1h): ${vol.get('h1', 'N/A')}\n"
    reply += f"📈 Volume (24h): ${vol.get('h24', 'N/A')}\n"

    # Analisa status token sederhana berdasarkan umur dan volume
    if vol.get('m5', 0) > 5000 and vol.get('h1', 0) > 20000:
        reply += "✅ Analisa: Token masih aktif dan volume sehat"
    else:
        reply += "⚠️ Analisa: Volume rendah, waspadai token mati"

    return reply

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if str(message.chat.id) != str(USER_ID):
        return

    mint_address = message.text.strip()
    bot.send_message(message.chat.id, f"🧠 Menerima mint:\n{mint_address}")

    reply = build_reply(mint_address)
    bot.send_message(message.chat.id, reply)

print("🤖 Bot aktif dengan analisa cerdas...")
bot.infinity_polling()
