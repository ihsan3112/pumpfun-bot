import os
import telebot

TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
USER_ID = os.getenv("USER_ID")

if not TOKEN_TELEGRAM or not USER_ID:
    print("❌ Environment variable TOKEN_TELEGRAM atau USER_ID belum diset.")
else:
    try:
        USER_ID = int(USER_ID)
        bot = telebot.TeleBot(TOKEN_TELEGRAM)
        bot.send_message(USER_ID, "✅ Bot berhasil dijalankan dan Telegram sudah terhubung!")
        print("Pesan terkirim. Bot siap digunakan.")
    except Exception as e:
        print("❌ Gagal kirim pesan ke Telegram:", e)
