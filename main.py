import os
import requests
from telebot import TeleBot
from telebot.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")

bot = TeleBot(BOT_TOKEN)

def format_number(n):
    return "{:,}".format(n)

def analyze_volume(v5, v1h, v24h):
    if v5 > 0 and v1h > 0 and v24h > 0:
        if v5 < v1h / 10:
            return "Volume 5m sangat kecil dibanding 1h = kemungkinan token melambat"
        elif v1h < v24h / 10:
            return "Aktivitas 1 jam rendah dibanding 24 jam = momentum mungkin hilang"
        else:
            return "Stabil: Token masih aktif dan volume sehat"
    return "Volume sangat rendah = token mungkin tidak aktif"

@bot.message_handler(func=lambda m: True)
def handle_message(message: Message):
    mint = message.text.strip()
    if not mint or len(mint) < 32:
        bot.send_message(message.chat.id, "Mint tidak valid atau terlalu pendek.")
        return

    bot.send_message(message.chat.id, f"Mint diterima:\n{mint}")

    search_url = f"https://api.dexscreener.com/latest/dex/search?q={mint}"
    res = requests.get(search_url)
    if res.status_code != 200:
        bot.send_message(message.chat.id, "Gagal mencari data dari Dexscreener.")
        return

    data = res.json()
    if not data.get("pairs"):
        bot.send_message(message.chat.id, "Token belum muncul di Dexscreener (mungkin terlalu baru).")
        return

    pair = data["pairs"][0]
    pair_address = pair.get("pairAddress")
    pair_url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"
    res2 = requests.get(pair_url)

    if res2.status_code != 200:
        bot.send_message(message.chat.id, "Gagal mengambil data pair.")
        return

    d = res2.json()["pair"]
    v5 = d["volume"]["m5"]
    v1h = d["volume"]["h1"]
    v24h = d["volume"]["h24"]
    analysis = analyze_volume(v5, v1h, v24h)

    msg = (
        f"Total Supply: {format_number(d.get('totalSupply', 0))}\n"
        f"Liquidity: ${format_number(int(d['liquidity']['usd']))}\n"
        f"Volume (5m): ${format_number(int(v5))}\n"
        f"Volume (1h): ${format_number(int(v1h))}\n"
        f"Volume (24h): ${format_number(int(v24h))}\n"
        f"Analisa: {analysis}\n"
        f"Dexscreener: {d['url']}"
    )

    bot.send_message(message.chat.id, msg)

bot.polling(non_stop=True)
