import os
import requests
import time
import datetime
import telebot

TOKEN_TELEGRAM = os.getenv("TOKEN_TELEGRAM")
USER_ID = int(os.getenv("USER_ID"))

bot = telebot.TeleBot(TOKEN_TELEGRAM)

RPC_URL = "https://api.mainnet-beta.solana.com"

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

def kirim_sambutan():
    bot.send_message(USER_ID, "🚀 Bot Railway telah dimulai...\nKirim mint address token Pump.fun untuk mulai analisa.")

@bot.message_handler(func=lambda message: True)
def tangani_analisa(message):
    mint = message.text.strip()
    hasil = []
    bot.send_message(USER_ID, f"📊 Memulai analisa token: `{mint}`", parse_mode="Markdown")

    for i in range(10):
        tx = get_transactions(mint)
        hasil.append(len(tx))
        print(f"⏰{datetime.datetime.now().strftime('%H:%M:%S')} – Jumlah transaksi: {len(tx)}")
        time.sleep(30)

    penurunan = sum(1 for i in range(1, len(hasil)) if hasil[i] <= hasil[i - 1])

    if hasil[-1] == 0 or penurunan >= 7:
        kesimpulan = "⚠️ *Kesimpulan*: Token kemungkinan *MATI* dalam 15 menit ke depan"
    else:
        kesimpulan = "✅ *Kesimpulan*: Token masih aktif dan kemungkinan *AMAN*"

    bot.send_message(USER_ID, f"{kesimpulan}", parse_mode="Markdown")

if __name__ == "__main__":
    kirim_sambutan()
    bot.polling()

