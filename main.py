import os
import requests
from telebot import TeleBot
from telebot.types import Message
import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("USER_ID")

bot = TeleBot(BOT_TOKEN)

def format_usd(value):
    try:
        return f"${float(value):,.0f}"
    except:
        return "$0"

def format_age(age_minutes):
    if age_minutes < 60:
        return f"{int(age_minutes)} menit"
    elif age_minutes < 1440:
        return f"{age_minutes/60:.1f} jam"
    else:
        return f"{age_minutes/1440:.1f} hari"

def analyze_token(vol5, vol1h, vol24h, liq, price_change_5m, age_minutes):
    analysis = []
    try:
        vol5 = float(vol5)
        vol1h = float(vol1h)
        vol24h = float(vol24h)
        liq = float(liq)
        price_change_5m = float(price_change_5m)
    except:
        return "⚠️ Data volume tidak valid."

    if vol5 > liq * 0.3 and vol5 > vol1h * 0.7 and price_change_5m > 20:
        analysis.append("🚀 Potensi pump kuat! Volume 5m dominan dan harga naik signifikan.")
    if vol5 > liq * 0.3 and price_change_5m < 1:
        analysis.append("🐋 Volume besar dalam 5m tapi harga stagnan → potensi whale buang.")
    if vol1h < vol24h * 0.1:
        analysis.append("📉 Volume 1 jam sangat kecil dibanding 24 jam → momentum menurun.")
    if vol5 < liq * 0.05:
        analysis.append("💤 Volume 5m terlalu kecil dibanding liquidity → token mulai sepi.")
    if age_minutes < 30:
        analysis.append("⚠️ Token masih sangat muda (< 30 menit) → rawan rug / sniper.")
    if not analysis:
        analysis.append("✅ Volume stabil dan tidak ada tanda distribusi atau pump ekstrem.")
    
    return "\n".join(analysis)

@bot.message_handler(func=lambda m: True)
def handle_message(message: Message):
    mint = message.text.strip()
    if not mint or len(mint) < 32:
        bot.send_message(message.chat.id, "❌ Mint tidak valid atau terlalu pendek.")
        return

    bot.send_message(message.chat.id, f"🧠 Mengecek mint: `{mint}`", parse_mode="Markdown")

    try:
        url = f"https://public-api.dextools.io/trial/pair/solana/{mint}"
        headers = {"accept": "application/json"}
        res = requests.get(url, headers=headers, timeout=10)

        if res.status_code != 200:
            bot.send_message(message.chat.id, "⚠️ Token tidak ditemukan di Dexscreener.")
            return

        data = res.json()
        liq = data.get("liquidity", {}).get("usd", 0)
        vol5 = data.get("volume", {}).get("m5", 0)
        vol1h = data.get("volume", {}).get("h1", 0)
        vol24h = data.get("volume", {}).get("h24", 0)
        price_change_5m = data.get("priceChange", {}).get("m5", 0)

        created = data.get("info", {}).get("createdAt")
        age_minutes = 9999
        age_display = "Tidak tersedia"
        if created:
            dt_created = datetime.datetime.fromisoformat(created.replace("Z", "+00:00"))
            now = datetime.datetime.now(datetime.timezone.utc)
            age_minutes = (now - dt_created).total_seconds() / 60
            age_display = format_age(age_minutes)

        result = (
            f"📊 Volume:\n"
            f"- 5m: {format_usd(vol5)}\n"
            f"- 1h: {format_usd(vol1h)}\n"
            f"- 24h: {format_usd(vol24h)}\n"
            f"- Liquidity: {format_usd(liq)}\n"
            f"- Harga 5m: {price_change_5m}%\n"
            f"- Umur Token: {age_display}\n\n"
            f"{analyze_token(vol5, vol1h, vol24h, liq, price_change_5m, age_minutes)}"
        )

        bot.send_message(message.chat.id, result)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error mengambil data:\n{e}")

print("✅ Bot siap menerima mint...")

if __name__ == "__main__":
    try:
        bot.polling(non_stop=True)
    except Exception as e:
        print(f"❌ Polling error: {e}")
