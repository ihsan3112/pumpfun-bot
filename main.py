import os
import telebot
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN tidak ditemukan!")

bot = telebot.TeleBot(BOT_TOKEN)

def get_transaction_count(mint):
    try:
        url = f"https://api.helius.xyz/v0/token-transactions?mint={mint}&limit=1"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return len(data)  # total tx ditemukan
        else:
            return -1
    except Exception as e:
        print("❌ Error saat ambil data transaksi:", e)
        return -1

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Bot aktif!\nKirim mint address token Solana untuk mulai analisa.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    mint = message.text.strip()
    if len(mint) >= 32:
        bot.send_message(message.chat.id, f"🧠 Menerima mint:\n`{mint}`", parse_mode="Markdown")

        tx_count = get_transaction_count(mint)
        if tx_count == -1:
            bot.send_message(message.chat.id, "❌ Gagal mengambil data transaksi.")
        else:
            reply = (
                f"🔄 Jumlah transaksi: {tx_count}\n"
                f"📎 [Dexscreener](https://dexscreener.com/solana/{mint})\n"
                f"📎 [Pump.fun](https://pump.fun/{mint})"
            )
            bot.send_message(message.chat.id, reply, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Format mint tidak valid.")

if __name__ == "__main__":
    print("Bot siap menerima perintah...")
    bot.polling(none_stop=True)
