import os
import telebot

TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
USER_ID = int(os.getenv("USER_ID"))

bot = telebot.TeleBot(TOKEN_TELEGRAM)
bot.send_message(USER_ID, "✅ Bot berhasil dijalankan dan Telegram sudah terhubung!")

print("Pesan terkirim. Bot siap digunakan.")
