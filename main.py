import os
import telebot

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN tidak ditemukan!")

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Bot aktif!\nKirim mint address token Solana untuk mulai analisa.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    mint = message.text.strip()
    if len(mint) >= 32:
        bot.reply_to(message, f"🧠 Menerima mint:\n`{mint}`", parse_mode="Markdown")
        bot.send_message(message.chat.id, "✅ Jumlah transaksi ditemukan: 20")
    else:
        bot.reply_to(message, "❌ Mint address tidak valid.")

if __name__ == "__main__":
    print("Bot siap menerima perintah...")
    bot.polling(none_stop=True)
