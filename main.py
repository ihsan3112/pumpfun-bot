import os
import requests
from telebot import TeleBot
from telebot.types import Message

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")

bot = TeleBot(BOT_TOKEN)

def format_number(n):
    return "{:,}".format(n)

def score_token(vol_5m, vol_1h, vol_24h, liq, mc):
    score = 0
    reasons = []

    if vol_5m > liq * 0.8:
        score += 40
        reasons.append("Volume 5m tinggi dibanding liquidity")
    if vol_1h > vol_24h * 0.2:
        score += 30
        reasons.append("Volume 1h aktif (lebih dari 20% dari 24h)")
    if mc < liq * 10:
        score += 20
        reasons.append("Market cap belum terlalu berat")
    if vol_24h > mc:
        score += 10
        reasons.append("Volume 24h lebih besar dari MC")

    if score >= 80:
        status = "🟢 Sangat kuat untuk masuk cepat"
    elif score >= 50:
        status = "🟡 Moderat, momentum bisa naik atau turun"
    else:
        status = "🔴 Risiko tinggi, potensi rug atau token lemah"

    return score, status, reasons

@bot.message_handler(func=lambda m: True)
def handle_message(message: Message):
    mint = message.text.strip()

    if not mint or len(mint) < 32:
        bot.send_message(message.chat.id, "❌ Mint tidak valid atau terlalu pendek.")
        return

    bot.send_message(message.chat.id, f"🧠 Mengecek mint: \n{mint}")

    try:
        # Contoh URL, disesuaikan dengan struktur data DexScreener API
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{mint}"
        res = requests.get(url)
        data = res.json()

        pair = data.get("pair")
        if not pair:
            bot.send_message(message.chat.id, "⚠️ Token tidak ditemukan di Dexscreener. Coba lagi beberapa saat lagi.")
            return

        supply = int(pair.get("totalSupply", 0))
        liquidity = float(pair.get("liquidity", {}).get("usd", 0))
        volume_5m = float(pair.get("volume", {}).get("m5", 0))
        volume_1h = float(pair.get("volume", {}).get("h1", 0))
        volume_24h = float(pair.get("volume", {}).get("h24", 0))
        marketcap = float(pair.get("fdv", 0))

        score, status, reasons = score_token(volume_5m, volume_1h, volume_24h, liquidity, marketcap)

        reply = f"Total Supply: {format_number(supply)}\n"
        reply += f"Liquidity: ${format_number(int(liquidity))}\n"
        reply += f"Volume (5m): ${format_number(int(volume_5m))}\n"
        reply += f"Volume (1h): ${format_number(int(volume_1h))}\n"
        reply += f"Volume (24h): ${format_number(int(volume_24h))}\n"
        reply += f"Marketcap: ${format_number(int(marketcap))}\n"
        reply += f"\n📊 Skor: {score}/100\n📌 Analisa: {status}\n"
        reply += f"\n🧩 Alasan:\n- " + "\n- ".join(reasons)

        bot.send_message(message.chat.id, reply)

    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Terjadi kesalahan saat mengambil data: {str(e)}")

bot.polling()
