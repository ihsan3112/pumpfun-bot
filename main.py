import telebot
import os

# Ambil token bot dari environment variable di Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Komando awal /start atau /help
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🤖 Bot aktif!\nKirimkan mint address token Solana untuk mulai analisa.")

# Handler untuk pesan biasa
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    mint_address = message.text.strip()

    # Cek apakah teks terlihat seperti alamat mint
    if len(mint_address) >= 32:
        bot.reply_to(message, f"🧠 Menerima mint:\n`{mint_address}`", parse_mode="Markdown")

        # Dummy response / logika analisa bisa kamu isi di sini
        # Contoh:
        # data = check_solscan(mint_address)
        # bot.reply_to(message, format_data(data))

        bot.send_message(message.chat.id, "✅ Jumlah transaksi ditemukan: 20")  # Dummy statik
    else:
        bot.reply_to(message, "❌ Alamat mint tidak valid. Kirim mint address token Solana.")

# Jalankan bot (FIXED: tanpa threaded=True)
if __name__ == "__main__":
    print("Bot siap menerima perintah...")
    bot.polling(none_stop=True)
