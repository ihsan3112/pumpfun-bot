import time
import requests
from datetime import datetime
import os

# === Konfigurasi Telegram ===
BOT_TOKEN = "7304825429:AAFkU5nZ47g1b1dCJdTaQFZn0hw3c9JP0Bs"
USER_ID = "7806614019"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# === RPC URL Solana ===
RPC_URL = "https://api.mainnet-beta.solana.com"

# === Daftar token (mint address) yang akan dianalisis ===
TOKEN_LIST = [
    "DzqgQpPxzoUBGSwcCj6k3VnEg2JgxCfF99QofRaZpump"
]

def kirim_telegram(pesan):
    try:
        requests.post(TELEGRAM_API, json={"chat_id": USER_ID, "text": pesan})
    except Exception as e:
        print(f"[x] Gagal kirim Telegram: {e}")

def get_recent_transactions(mint_address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [mint_address, {"limit": 20}]
    }
    response = requests.post(RPC_URL, json=payload)
    return response.json()

def analisa_token(mint_address):
    print(f"🔍 Memulai analisa token: {mint_address}")
    kirim_telegram(f"🔍 Mulai analisa token:\n{mint_address}")

    previous = 0
    penurunan = 0

    for _ in range(9):
        result = get_recent_transactions(mint_address)
        count = len(result.get("result", []))
        print(f"🕒 {datetime.now().strftime('%H:%M:%S')} — Jumlah transaksi: {count}")
        if count < previous:
            penurunan += 1
        previous = count
        time.sleep(30)

    if previous == 0 or penurunan >= 7:
        kesimpulan = "⚠️ Token kemungkinan MATI dalam 15 menit ke depan"
    else:
        kesimpulan = "✅ Token masih aktif dan ada potensi bertahan"

    print(f"\n📊 Hasil: {kesimpulan}\n")
    kirim_telegram(f"📊 Hasil analisa:\n{kesimpulan}\nToken: {mint_address}")

def monitor_tokens():
    while True:
        for token in TOKEN_LIST:
            analisa_token(token)
        time.sleep(60)  # Tunggu 1 menit sebelum analisa token berikutnya

if __name__ == "__main__":
    print("🚀 Bot Railway telah dimulai...")
    kirim_telegram("🚀 Bot Railway telah aktif dan siap menganalisa token.")
    monitor_tokens()
