import os
import telebot
import requests
import json
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)


def get_token_supply(mint):
    try:
        url = "https://api.mainnet-beta.solana.com"
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenSupply",
            "params": [mint]
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            result = response.json()
            return int(result["result"]["value"]["uiAmount"])
    except:
        pass
    return -1


def get_token_dex_data(mint):
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={mint}"
        response = requests.get(url)
        if response.status_code == 200:
            pairs = response.json().get("pairs", [])
            for pair in pairs:
                if pair.get("baseToken", {}).get("address") == mint:
                    return {
                        "liquidity": pair["liquidity"]["usd"],
                        "vol_5m": pair["volume"]["m5"],
                        "vol_1h": pair["volume"]["h1"],
                        "vol_24h": pair["volume"]["h24"],
                        "txns": pair["txns"]["m5"],
                        "buy_ratio": pair["txns"]["m5"] and (pair["txns"].get("m5_buy", 0) / max(pair["txns"]["m5"], 1)) * 100,
                        "holders": pair.get("holders", 0),
                        "dex_url": pair["url"],
                        "created_at": pair.get("pairCreatedAt", 0)
                    }
    except:
        pass
    return None


def analisa_status(dex):
    v5 = dex['vol_5m']
    v1 = dex['vol_1h']
    v24 = dex['vol_24h']
    liq = dex['liquidity']
    txns = dex['txns']
    buy_ratio = dex['buy_ratio']

    created = datetime.fromtimestamp(dex['created_at'] / 1000)
    now = datetime.utcnow()
    age_minutes = (now - created).total_seconds() / 60

    if age_minutes < 10:
        if v5 > 500 and buy_ratio > 70:
            return "🚀 Token baru dengan volume tinggi dan dominan dibeli"
        elif v5 < 100:
            return "⚠️ Token baru tapi volume sangat rendah"
        else:
            return "🔎 Token baru, butuh observasi lebih lanjut"

    elif age_minutes < 60:
        if v5 < 0.1 * v1:
            return "⚠️ Aktivitas melambat dibanding 1 jam terakhir"
        elif buy_ratio > 60 and txns > 10:
            return "✅ Aktif: Transaksi sehat dan dominan pembelian"
        else:
            return "🔍 Stabil tapi tidak dominan beli"

    else:
        if v5 < 0.05 * v24 and liq < 300:
            return "❌ Mati suri: volume 5m kecil dibanding 24 jam dan likuiditas tipis"
        elif buy_ratio < 40:
            return "⚠️ Dominan penjualan, kemungkinan akan dump"
        else:
            return "✅ Stabil: Volume, likuiditas dan tren pembelian masih kuat"


@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(message, "🤖 Kirim mint address token Solana untuk analisa lengkap dan prediksi dump/bertahan.")


@bot.message_handler(func=lambda m: True)
def handle_mint(message):
    mint = message.text.strip()
    if len(mint) < 32:
        bot.send_message(message.chat.id, "❌ Format mint tidak valid.")
        return

    bot.send_message(message.chat.id, f"🧠 Menerima mint:\n`{mint}`", parse_mode="Markdown")

    supply = get_token_supply(mint)
    supply_text = f"{supply:,}" if supply != -1 else "N/A"

    dex = get_token_dex_data(mint)
    if dex:
        prediksi = analisa_status(dex)
        reply = (
            f"📦 Total Supply: {supply_text}\n"
            f"💧 Liquidity: ${dex['liquidity']:,}\n"
