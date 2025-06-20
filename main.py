import os
import requests
import telebot

# Ambil token dan user ID dari environment variable
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
USER_ID = os.getenv("USER_ID")

# Cek apakah variabel sudah diisi
if not TOKEN_TELEGRAM or not USER_ID:
    print("❌ TOKEN_TELEGRAM atau USER_ID belum di-set.")
    exit()

USER_ID = int(USER_ID)
bot = telebot.TeleBot(TOKEN_TELEGRAM)

RPC_URL = "https://api.mainnet-beta.solana.com"

# Fungsi untuk mengambil transaksi terakhir dari mint address
def get_transactions(mint_address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [mint_address, {"limit": 20}]
    }
    response = requests.post(RPC_URL, json=payload)
    result = response.json()
    if "result" in result:
        return result["result"]
    return []

# Fungsi utama untuk analisa mint address
def analisa_token(mint_address):
    hasil = []
    bot.send_message(USER_ID, f"\U0001F9E0 Menerima mint: \n`{mint_address}`", parse_mode="Markdown")
    txs = get_transactions(mint_address)
    if not txs:
        bot.send_message(USER_ID, "\u26a0\ufe0f Tidak ditemukan transaksi untuk mint address tersebut.")
        return
    # Placeholder untuk logika analisa lanjutan
    bot.send_message(USER_ID, f"\u2705 Jumlah transaksi ditemukan: {len(txs)}")

# Sambutan awal
bot.send_message(USER_ID, "✅ Bot Railway aktif!\nKirimkan mint address token untuk mulai analisa.")
print("Bot siap menerima perintah...")

# Tangani pesan masuk
@bot.message_handler(func=lambda message: True)
def tangani_pesan(message):
    mint = message.text.strip()
    if len(mint) > 20:
        analisa_token(mint)
    else:
        bot.send_message(USER_ID, "\u26a0\ufe0f Mint address terlalu pendek atau tidak valid.")

bot.polling(non_stop=True)
