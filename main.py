import os
import telebot
import requests
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN tidak ditemukan!")

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
        print("❌ Error saat ambil token supply:", e)
        return -1

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Bot aktif!\nKirimkan mint address token Solana untuk mulai analisa.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    mint = message.text.strip()
    if len(mint) >= 32:
        bot.send_message(message.chat.id, f"🧠 Menerima mint:\n`{mint}`", parse_mode="Markdown")

        supply = get_token_supply(mint)
        if supply == -1:
            bot.send_message(message.chat.id, "❌ Gagal mengambil total supply.")
        else:
            reply = (
                f"📦 Total Supply: {supply}\n"
                f"📎 [Dexscreener](https://dexscreener.com/solana/{mint})\n"
                f"📎 [Pump.fun](https://pump.fun/{mint})"
            )
            bot.send_message(message.chat.id, reply, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Format mint tidak valid.")

if __name__ == "__main__":
    print("Bot siap menerima perintah...")
    bot.polling(none_stop=True)
