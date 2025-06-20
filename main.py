import os
import telebot

TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
USER_ID = os.getenv("USER_ID")

if not TOKEN_TELEGRAM or not USER_ID:
    print("❌ TOKEN_TELEGRAM atau USER_ID belum di-set.")
    exit()

USER_ID = int(USER_ID)
bot = telebot.TeleBot(TOKEN_TELEGRAM)

bot.send_message(USER_ID, "✅ Bot Railway aktif!\nKirimkan mint address token untuk mulai analisa.")
print("Bot siap menerima pesan Telegram.")

@bot.message_handler(func=lambda msg: True)
def handle(msg):
    text = msg.text.strip()
    if len(text) > 20:
        bot.send_message(USER_ID, f"🧠 Menerima mint:\n`{text}`", parse_mode="Markdown")
    else:
        bot.send_message(USER_ID, "⚠️ Mint address terlalu pendek atau tidak valid.")

bot.polling(none_stop=True)
