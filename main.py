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
    try:
        if any(v is None for v in volumes):
            return "⚠️ Data volume belum lengkap (token mungkin terlalu baru)."

        if v5 == 0 and v1h == 0 and v24h == 0:
            return "⚠️ Tidak ada aktivitas volume. Kemungkinan token sudah mati."

        ratio_5m_1h = v5 / v1h if v1h else 0
        ratio_1h_24h = v1h / v24h if v24h else 0
        ratio_5m_24h = v5 / v24h if v24h else 0

        if ratio_5m_1h > 0.6 and ratio_1h_24h > 0.6:
            return "📈 Volume sangat aktif. Potensi pump tinggi jika tidak ada penjualan besar."
        elif ratio_5m_1h > 0.4:
            return "✅ Aktivitas sehat. Volume 5m cukup untuk menjaga momentum."
        elif ratio_5m_24h < 0.05 and ratio_1h_24h < 0.1:
            return "⚠️ Volume menurun tajam. Waspadai potensi penurunan."
        elif v5 < 50 and v1h < 300:
            return "❗ Aktivitas sangat rendah. Kemungkinan token tidak aktif."
        else:
            return "ℹ️ Volume stabil tapi belum ada momentum besar."
    except:
        return "❓ Gagal analisa volume karena data tidak lengkap."

@bot.message_handler(func=lambda m: True)
def handle_message(message: Message):
    mint = message.text.strip()

    if not mint or len(mint) < 32:
        bot.send_message(message.chat.id, "❌ Mint tidak valid atau terlalu pendek.")
        return

    bot.send_message(message.chat.id, f"🧠 Mengecek mint:\n{mint}")

    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{mint}"
        response = requests.get(url)
        data = response.json()

        pair = data.get("pair")
        if not pair:
            bot.send_message(message.chat.id, "⚠️ Token tidak ditemukan di Dexscreener. Coba lagi beberapa saat lagi.")
            return

        supply = format_number(int(float(pair.get("totalSupply", 0))))
        liquidity = "$" + format_number(int(float(pair.get("liquidity", {}).get("usd", 0))))
        v5 = float(pair.get("volume", {}).get("m5", 0) or 0)
        v1h = float(pair.get("volume", {}).get("h1", 0) or 0)
        v24h = float(pair.get("volume", {}).get("h24", 0) or 0)

        volume_analysis = analyze_volume((v5, v1h, v24h))

        msg = (
            f"📊 Total Supply: {supply}\n"
            f"💧 Liquidity: {liquidity}\n"
            f"📈 Volume (5m): ${format_number(int(v5))}\n"
            f"📈 Volume (1h): ${format_number(int(v1h))}\n"
            f"📈 Volume (24h): ${format_number(int(v24h))}\n"
            f"🔎 Analisa: {volume_analysis}\n"
            f"🔗 Dexscreener: {pair.get('url', '-')}")

        bot.send_message(message.chat.id, msg)

    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Terjadi kesalahan saat memproses: {str(e)}")

print("🤖 Bot aktif dan siap menerima perintah...")
bot.polling()
