import os
import telebot

# Ambil token dan user ID dari environment variable
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
USER_ID = os.getenv("USER_ID")

# Validasi sebelum lanjut
if not TOKEN_TELEGRAM or not USER_ID:
    print("❌ Environment variable TOKEN_TELEGRAM atau USER_ID belum di-set.")
    exit()

# Buat objek bot
bot = telebot.TeleBot(TOKEN_TELEGRAM)
USER_ID = int(USER_ID)

# Kirim pesan saat bot aktif
bot.send_message(USER_ID, "✅ Bot Railway aktif!\nKirimkan mint address token untuk mulai analisa.")
print("Bot sudah berjalan dan siap menerima pesan.")

# Handler untuk pesan masuk
@bot.message_handler(func=lambda msg: True)
def handle_message(msg):
    mint = msg.text.strip()
    if len(mint) > 20:
        bot.send_message(USER_ID, f"🧠 Menerima mint address:\n`{mint}`", parse_mode="Markdown")
    else:
        bot.send_message(USER_ID, "⚠️ Format mint address tidak valid.")

bot.polling(none_stop=True)
