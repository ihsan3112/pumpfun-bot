import os
import telebot
import requests
import json

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
                        "dex_url": pair["url"]
                    }
    except:
        pass
    return None

def analisa_status(dex):
    v5 = dex['vol_5m']
    v1 = dex['vol_1h']
    liq = dex['liquidity']

    if v5 == 0 and liq < 100:
        return "❌ Sangat Berisiko: Mati suri dan liquidity sangat rendah"
    elif v5 < 0.01 * v1 or liq < 300:
        return "⚠️ Waspada: Aktivitas menurun atau liquidity tipis"
    elif v5 > 0.02 * v1 and liq > 1000:
        return "✅ Stabil: Token masih aktif dan volume sehat"
    else:
        return "🔎 Belum jelas: Perlu observasi volume lanjutan"

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(message, "🤖 Kirim mint address token Solana untuk analisa lengkap.")

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
            f"📈 Volume (5m): ${dex['vol_5m']:,}\n"
            f"📊 Volume (1h): ${dex['vol_1h']:,}\n"
            f"📉 Volume (24h): ${dex['vol_24h']:,}\n\n"
            f"🔍 *Analisa:* {prediksi}\n\n"
            f"📎 [Dexscreener]({dex['dex_url']})\n"
            f"📎 [Pump.fun](https://pump.fun/{mint})"
        )
    else:
        reply = (
            f"📦 Total Supply: {supply_text}\n"
            f"⚠️ Token belum muncul di Dexscreener (mungkin terlalu baru)\n\n"
            f"📎 [Pump.fun](https://pump.fun/{mint})"
        )

    bot.send_message(message.chat.id, reply, parse_mode="Markdown")

if __name__ == "__main__":
    print("Bot aktif dan menganalisa dump/bertahan...")
    bot.polling(none_stop=True)
