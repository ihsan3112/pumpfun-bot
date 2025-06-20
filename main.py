import requests
import time
import datetime
import telebot

TOKEN_TELEGRAM = "7304825429:AAFkU5nZ4...g3c9JP0Bs"  # Ganti dengan token kamu
USER_ID = 7806614019  # Ganti dengan ID kamu

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

def analisa_token(mint_address):
    hasil = []
    bot.send_message(USER_ID, f"🔍 Memulai analisa token:\n`{mint_address}`", parse_mode="Markdown")

    for i in range(10):
        tx = get_transactions(mint_address)
        hasil.append(len(tx))
        print(f"🕓 {datetime.datetime.now().strftime('%H:%M:%S')} - Jumlah transaksi: {len(tx)}")
        time.sleep(30)

    penurunan = 0
    for i in range(1, len(hasil)):
        if hasil[i] <= hasil[i-1]:
            penurunan += 1

    kesimpulan = "✅ Token kemungkinan AKAN BERTAHAN" if penurunan <= 3 else "⚠️ Token kemungkinan MATI dalam 15 menit"

    bot.send_message(USER_ID,
        f"📊 Hasil analisa token:\nTotal pengamatan: 5 menit\nPenurunan aktivitas: {penurunan} dari 9\n\n{kesimpulan}"
    )

@bot.message_handler(commands=['start'])
def kirim_sambutan(message):
    bot.send_message(message.chat.id, "Halo! Kirim perintah: `/analisa <mint_address>`", parse_mode="Markdown")

@bot.message_handler(commands=['analisa'])
def tangani_analisa(message):
    try:
        mint = message.text.split(" ")[1]
        analisa_token(mint)
    except:
        bot.send_message(message.chat.id, "❗ Format salah. Contoh:\n`/analisa 7kGx...`", parse_mode="Markdown")

print("🤖 Bot Railway telah dimulai...")
bot.polling()
