import requests
import time
import os
from datetime import datetime

# === KONFIGURASI TELEGRAM ===
TELEGRAM_TOKEN = "7304825429:AAFkU5nZ47g1b1dCJdTaQFZn0hw3c9JP0Bs"
TELEGRAM_CHAT_ID = "7806614019"

# === URL RPC Solana ===
RPC_URL = "https://api.mainnet-beta.solana.com"

# Kirim pesan ke Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except:
        print("Gagal mengirim ke Telegram.")

# Ambil transaksi terbaru untuk sebuah mint address
def get_recent_transactions(mint_address):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getSignaturesForAddress",
        "params": [mint_address, {"limit": 20}]
    }
    try:
        response = requests.post(RPC_URL, json=payload)
        result = response.json()
        return result.get("result", [])
    except:
        return []

# === LOGIKA ANALISA ===
def analyze_token(mint_address):
    send_telegram_message(f"🥛 Menganalisis token selama 5 menit: {mint_address}")
    activity_log = []

    for i in range(10):
        result = get_recent_transactions(mint_address)
        count = len(result)
        activity_log.append(count)
        now = datetime.now().strftime("%H:%M:%S")
        print(f"⏰{now} - Jumlah transaksi terakhir: {count}")
        time.sleep(30)

    drop_count = sum(1 for i in range(1, len(activity_log)) if activity_log[i] <= activity_log[i-1])
    total_tx_last = sum(activity_log[-2:])

    analisa = f"\n📋 Hasil Analisa:\nTotal transaksi dalam 5 menit: {total_tx_last}\nPenurunan aktivitas sebanyak {drop_count} dari 9 interval"

    if drop_count >= 6:
        kesimpulan = "⚠️Kesimpulan: Token kemungkinan MATI dalam 15 menit ke depan"
    else:
        kesimpulan = "✅Kesimpulan: Token berpotensi bertahan (aktivitas stabil/naik)"

    print(analisa)
    print(kesimpulan)
    send_telegram_message(analisa + "\n" + kesimpulan)

# === INPUT USER ===
mint = input("Masukkan mint address token Pump.fun: ").strip()

# === EKSEKUSI ===
analyze_token(mint)
