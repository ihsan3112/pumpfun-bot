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
            return "\u26a0\ufe0f Volume 5m sangat kecil dibanding 1h \u2192 kemungkinan token melambat"
        elif v1h < v24h / 10:
            return "\u26a0\ufe0f Aktivitas 1 jam rendah dibanding 24 jam \u2192 momentum mungkin hilang"
        else:
            return "\ud83d\udcc8 Stabil: Token masih aktif dan volume sehat"
    return "\u2753 Data volume tidak lengkap"

@bot.message_handler(func=lambda m: True)
def handle_message(message: Message):
    mint = message.text.strip()
    if not mint or len(mint) < 32:
        bot.send_message(message.chat.id, "\u274c Mint tidak valid atau terlalu pendek.")
        return

    bot.send_message(message.chat.id, f"\ud83e\udde0 Mengecek mint: `{mint}`", parse_mode="Markdown")

    search_url = f"https://api.dexscreener.com/latest/dex/search?q={mint}"
    search_res = requests.get(search_url)
    if search_res.status_code != 200:
        bot.send_message(message.chat.id, "\u26a0\ufe0f Gagal mengakses Dexscreener. Coba beberapa saat lagi.")
        return

    data = search_res.json()
    pairs = data.get("pairs", [])
    if not pairs:
        bot.send_message(message.chat.id, "\u26a0\ufe0f Token tidak ditemukan di Dexscreener.")
        return

    pair = pairs[0]  # Ambil pasangan pertama yang ditemukan
    pair_address = pair.get("pairAddress")
    dex_url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{pair_address}"
    res = requests.get(dex_url)
    if res.status_code != 200:
        bot.send_message(message.chat.id, "\u26a0\ufe0f Gagal ambil data token dari Dexscreener.")
        return

    token = res.json().get("pair", {})
    if not token:
        bot.send_message(message.chat.id, "\u26a0\ufe0f Data token tidak tersedia.")
        return

    info = (
        f"*Total Supply:* {format_number(int(token.get('totalSupply', 0)))}\n"
        f"*Liquidity:* ${format_number(int(token.get('liquidity', {}).get('usd', 0)))}\n"
        f"*Volume (5m):* ${format_number(int(token.get('volume', {}).get('m5', 0)))}\n"
        f"*Volume (1h):* ${format_number(int(token.get('volume', {}).get('h1', 0)))}\n"
        f"*Volume (24h):* ${format_number(int(token.get('volume', {}).get('h24', 0)))}\n"
    )

    v5 = token.get('volume', {}).get('m5', 0)
    v1h = token.get('volume', {}).get('h1', 0)
    v24h = token.get('volume', {}).get('h24', 0)
    analysis = analyze_volume((v5, v1h, v24h))
    
    url = token.get("url", "")
    link = f"[Dexscreener]({url})" if url else ""

    bot.send_message(
        message.chat.id,
        f"{info}\n*Analisa:* {analysis}\n{link}",
        parse_mode="Markdown",
        disable_web_page_preview=False
    )

bot.polling()
