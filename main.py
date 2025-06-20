import requests
import time
import datetime
import telebot

TOKEN_TELEGRAM = "7304825429:AAFkU5nZ4...g3c9JP0Bs"  # Ganti dengan token bot kamu
USER_ID = 7806614019  # Ganti dengan ID Telegram kamu

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
    bot.send_message(USER_ID, f"🧠 Memulai analisa token:\n`{mint_address}`", parse_mode="Markdown")

    for i in range(10):  # 5 menit total, tiap 30 detik
        tx = get_transactions(mint_address)
        hasil.append(len(tx))
        print(f"⏰ {datetime.datetime.now().strftime('%H:%M:%S')} – Jumlah transaksi: {len(tx)}")
        time.sleep(30)

    penurunan = 0
    for i in range(1, len(hasil)):
        if hasil[i] <= hasil[i - 1]:
            penurunan += 1

    pesan = "\n📊 *Hasil Analisa:*\n"
    pesan += f"Total transaksi dalam 5 menit: `{sum(hasil)}`\n"
    pesan += f"Penurunan aktivitas sebanyak {penurunan} dari {len(hasil) - 1} interval\n"

    if penurunan >= 7:
        pesan += "\n⚠️ *Kesimpulan:* Token kemungkinan *MATI* dalam 15 menit ke depan"
    else:
        pesan += "\n✅ *Kesimpulan:* Token kemungkinan *MASIH HIDUP* untuk sementara"

    bot.send_message(USER_ID, pesan, parse_mode="Markdown")


def kirim_sambutan():
    bot.send_message(USER_ID, "🤖 Bot Railway telah dimulai...\nKirim mint address token Pump.fun untuk mulai analisa.")


def tangani_analisa(message):
    mint = message.text.strip()
    if len(mint) < 32:
        bot.send_message(USER_ID, "❌ Mint address tidak valid. Silakan coba lagi.")
        return
    analisa_token(mint)


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    tangani_analisa(message)


if __name__ == "__main__":
    kirim_sambutan()
    bot.polling()
