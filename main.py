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
        else:
            return -1
    except Exception as e:
        print("❌ Supply error:", e)
        return -1

def get_token_dex_data_via_search(mint):
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={mint}"
        response = requests.get(url)
        if response.status_code == 200:
            pairs = response.json().get("pairs", [])
            for pair in pairs:
                base = pair.get("baseToken", {})
                if base.get("address", "") == mint:
                    return {
                        "liquidity": pair["liquidity"]["usd"],
                        "vol_5m": pair["volume"]["m5"],
                        "vol_1h": pair["volume"]["h1"],
                        "vol_24h": pair["volume"]["h24"],
                        "dex_url": pair["url"]
                    }
        return None
    except Exception as e:
        print("❌ Dex search error:", e)
        return None

def interpret_status(volume_5m, liquidity):
    if volume_5m == 0 or liquidity < 10:
        return "❌ Mati Suri"
    elif volume_5m < 50:
        return "⚠️ Sepi"
    else:
        return "✅ Aktif"

@bot.message_handler(commands=['start', 'help'])
def welcome(message):
    bot.reply_to(message, "🤖 Kirim mint address token Solana untuk analisa.")

@bot.message_handler(func=lambda m: True)
def handle_mint(message):
    mint = message.text.strip()
    if len(mint) < 32:
        bot.send_message(message.chat.id, "❌ Format mint tidak valid.")
        return

    bot.send_message(message.chat.id, f"🧠 Menerima mint:\n`{mint}`", parse_mode="Markdown")

    supply = get_token_supply(mint)
    supply_text = f"{supply:,}" if supply != -1 else "N/A"

    dex = get_token_dex_data_via_search(mint)
    if dex:
        status = interpret_status(dex["vol_5m"], dex["liquidity"])
        reply = (
            f"📦 Total Supply: {supply_text}\n"
            f"💧 Liquidity: ${dex['liquidity']:,}\n"
            f"📈 Volume (5m): ${dex['vol_5m']:,} → {status}\n"
            f"📊 Volume (1h): ${dex['vol_1h']:,}\n"
            f"📉 Volume (24h): ${dex['vol_24h']:,}\n\n"
            f"📎 [Dexscreener]({dex['dex_url']})\n"
            f"📎 [Pump.fun](https://pump.fun/{mint})"
        )
    else:
        reply = (
            f"📦 Total Supply: {supply_text}\n"
            f"⚠️ Token belum ditemukan di Dexscreener (mungkin terlalu baru atau tidak match)\n\n"
            f"📎 [Pump.fun](https://pump.fun/{mint})"
        )

    bot.send_message(message.chat.id, reply, parse_mode="Markdown")

if __name__ == "__main__":
    print("Bot siap analisa cerdas...")
    bot.polling(none_stop=True)
