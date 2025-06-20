import requests
import time
import datetime
import telebot

# Ganti token dan ID kamu di sini
TOKEN_TELEGRAM = "7304825429:AAFkU5nZ4g7g1b1dCJdTaQFZn0hw3c9JP0Bs"
USER_ID = 7806614019

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
    bot.send_message(USER_ID, f"🔍 Memulai analisa token: `{mint_address}`", parse_mode="Markdown")

    for i in range(10):  # total 5 menit (10 x 30 detik)
        tx = get_transactions(mint_address)
        hasil.append(len(tx))
        print(f"🕓 {datetime.datetime.now().strftime('%H:%M:%S')} - Jumlah transaksi: {len(tx)}")
        time.sleep(30)

    penurunan = 0
    for i in range(1, len(hasil)):
        if hasil[i] <= hasil[i - 1]:
            penurunan += 1

    pesan = (
        f"📊 *Hasil Analisa:*\n"
        f"Total transaksi dalam 5 menit: `{hasil[-1]}`\n"
        f"Penurunan aktivitas sebanyak `{penurunan}` dari 9 interval\n\n"
    )

    if penurunan >= 7:
        pesan += "⚠️ *Kesimpulan:* Tok
