import os
import requests
import time
import datetime
import telebot

# Ambil variabel dari environment Railway
TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
USER_ID = int(os.getenv("USER_ID"))

if not TOKEN_TELEGRAM or not USER_ID:
    print("❌ Environment variable TOKEN_TELEGRAM atau USER_ID belum diset.")
    exit()

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
    bot.send_message(USER_ID, f"🔍 Memulai analisa token:\n`{mint_address}`", parse_mode="Markdown")

    txs = get_transactions(mint_address)
    if not txs:
        bot.send_message(USER_ID, "⚠️ Tidak ada transaksi ditemukan untuk token ini.")
        return

    for tx in txs:
        signature = tx.get("signature")
        blocktime = tx.get("blockTime")
        waktu = datetime.datetime.fromtimestamp(blocktime).strftime("%H:%M:%S") if blocktime else "?"
        hasil.append(f"🧾 Tx: `{signature}`\n⏰ Waktu: `{waktu}`")

    ringkasan = "\n\n".join(hasil)
    bot.send_message(USER_ID, f"📊 Ringkasan transaksi terakhir:\n\n{ringkasan}", parse_mode="Markdown")

# Fungsi kirim sambutan awal
def kirim_sambutan():
    bot.send_message(USER_ID, "✅ Bot Railway aktif!!\nKirimkan mint address token untuk mulai analisa.")

# Fungsi menangani pesan masuk
def tangani_pesan(message):
    teks = message.text.strip()
    if len(teks) > 20:
        analisa_token(teks)
    else:
        bot.send_message(USER_ID, "❌ Format mint address tidak valid atau terlalu pendek.")

# Jalankan
kirim_sambutan()
bot.register_next_step_handler_by_chat_id(USER_ID, tangani_pesan)
bot.polling()
