import os
import telebot
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN tidak ditemukan!")

bot = telebot.TeleBot(BOT_TOKEN)

# Fungsi ambil jumlah holders dari Solscan
def get_holder_count(mint):
    try:
        url = f"https://public-api.solscan.io/token/holders?tokenAddress={mint}&limit=1"
        headers = {
            "accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("total", 0)  # jumlah holders
        else:
            return -1
    except Exception as e:
        print("❌ Error saat ambil data:", e)
        return -1

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Bot aktif!\nKirimkan mint address token Solana untuk mulai analisa.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    mint = message.text.strip()
    if len(mint) >= 32:
        bot.send_message(message.chat.id, f"🧠 Menerima mint:\n_
