import os
import requests
import time
import datetime
import telebot

# Ambil variabel dari environment Railway
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
USER_ID = int(os.getenv("USER_ID"))

bot = telebot.TeleBot(TOKEN_TELEGRAM)

RPC_URL = "https://api.mainnet-beta.solana.com"

# Fungsi mengambil transaksi terakhir dari token
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

# Fungsi menganalisis token
def analisa_token(mint_address):
    hasil = []
    bot.send_message(USER_ID, f"🧠 Memulai analisa token:\n{mint_address}", parse_mode="Markdown")
    
    for i in range(10):
        tx = get_transactions(mint_address)
        hasil.append(len(tx))
        print(f"⏱️ {datetime.datetime.now().strftime('%H:%M:%S')} - Jumlah transaksi: {len(tx)}")
        time.sleep(30)

    penurunan = 0
    for i in range(1, len(hasil)):
        if hasil[i] <= hasil[i - 1]:
            penurunan += 1

    if penurunan >= 7:
        bot.send_message(USER_ID, f"⚠️ Terjadi penurunan transaksi pada token ini. Waspada dump.")
    else:
        bot.send_message(USER_ID, f"✅ Aktivitas token stabil atau meningkat.")

# Fungsi sambutan awal
def kirim_sambutan():
    bot.send_message(USER_ID, "✅ Bot Railway aktif!!\nKirimkan mint address token untuk mulai analisa.")

# Fungsi menangani pesan masuk dari Telegram
@bot.message_handler(func=lambda message: True)
def tangani_pesan(message):
    mint = message.text.strip()
    if len(mint) < 30:
        bot.send_message(USER_ID, "❌ Format mint address tidak valid.")
        return
    analisa_token(mint)

if __name__ == "__main__":
    kirim_sambutan()
    bot.polling()
