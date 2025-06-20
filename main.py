import os
import telebot

# Ambil token dan user ID dari environment variable
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
USER_ID = os.getenv("USER_ID")

# Cek apakah variabel sudah diisi
if not TOKEN_TELEGRAM or not USER_ID:
    print("❌ Environment variable TOKEN_TELEGRAM atau USER_ID belum di-set.")
    exit()

USER_ID = int(USER_ID)
bot = telebot.TeleBot(TOKEN_TELEGRAM)

# Pesan awal saat bot aktif
bot.send_message(USER_ID, "✅ Bot Railway aktif!\nKirimkan mint address token untuk mulai analisa.")
print("Bot sudah berjalan dan siap menerima pesan.")

# Fungsi ketika user kirim pesan
@bot.message_handler(func=lambda message: True)
def tangani_pesan(message):
    mint = message.text.strip()
    if len(mint) > 20:
        bot.send_message(USER_ID, f"🔍 Menerima mint address:\n`{mint}`", parse_mode="Markdown")
        # Placeholder logika lanjutan bisa ditaruh di sini
    else:
        bot.send_message(USER_ID, "⚠️ Format mint address tidak valid.")

# Jalankan polling
bot.polling(none_stop=True)
