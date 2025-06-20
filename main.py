import telebot

# ✅ Gunakan token baru dari BotFather
TOKEN_TELEGRAM = "8184173057:AAFxfvVPUpwovWHP3LPnZMlblqQy-E96sGA"
USER_ID = 7806614019

bot = telebot.TeleBot(TOKEN_TELEGRAM)

# Notifikasi awal
bot.send_message(USER_ID, "✅ Bot Railway aktif!\nKirimkan mint address token untuk mulai analisa.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    mint_address = message.text.strip()
    response = f"📥 Mint address diterima:\n`{mint_address}`"
    bot.reply_to(message, response, parse_mode="Markdown")

bot.polling(none_stop=True)
