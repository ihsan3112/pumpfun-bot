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
            return "⚠️ Volume 5m kecil dibanding 1h → kemungkinan melambat"
        elif v1h < v24h / 10:
            return "⚠️ Aktivitas 1h rendah dibanding 24h → momentum melemah"
        elif v5 > v1h / 2 and v1h > v24h / 2:
            return "📈 Sinyal kuat: volume meningkat cepat → potensi pump"
        else:
            return "✅ Stabil: token aktif & volume cukup sehat"
    return "❓ Data volume tidak lengkap atau salah format"

@bot.message_handler(func=lambda m: True)
def handle_message(message: Message):
    mint = message.text.strip()

    if not mint or len(mint) < 32:
        bot.send_message(message.chat.id, "❌ Mint tidak valid atau terlalu pendek.")
        return

    bot.send_message(message.chat.id, f"🧠 Mengecek mint:\n{mint}")

    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{mint}"
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            bot.send_message(message.chat.id, "⚠️ Gagal mengambil data dari Dexscreener.")
            return

        data = r.json()
        pairs = data.get("pairs")

        if not pairs:
            bot.send_message(message.chat.id, "⚠️ Token tidak ditemukan di Dexscreener.")
            return

        pair = pairs[0]
        vol5m = float(pair.get("volume", {}).get("m5", 0))
        vol1h = float(pair.get("volume", {}).get("h1", 0))
        vol24h = float(pair.get("volume", {}).get("h24", 0))
        liquidity = float(pair.get("liquidity", {}).get("usd", 0))
        supply = pair.get("fdv", "n/a")

        result = (
            f"📦 Total Supply: {supply}\n"
            f"💧 Liquidity: ${format_number(int(liquidity))}\n"
            f"📊 Volume (5m): ${format_number(int(vol5m))}\n"
            f"📊 Volume (1h): ${format_number(int(vol1h))}\n"
            f"📊 Volume (24h): ${format_number(int(vol24h))}\n"
            f"📉 Analisa: {analyze_volume((vol5m, vol1h, vol24h))}\n"
            f"🔗 Dexscreener: {pair.get('url')}"
        )

        bot.send_message(message.chat.id, result)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error: {str(e)}")

bot.polling()
