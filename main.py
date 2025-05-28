import requests, json, time
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
from solana.system_program import TransferParams, transfer

# === KONFIGURASI ===
PUMPFUN_API = PUMPFUN_API = "https://client-api.pump.fun/v1/markets/recent"
JUPITER_API = "https://price.jup.ag/v4/price?ids="
RPC = "https://api.mainnet-beta.solana.com"
BUY_AMOUNT_SOL = 0.03
MIN_BUYER_COUNT = 1
SLIPPAGE = 0.2

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# === LOAD WALLET ===
with open("my-autobuy-wallet.json", "r") as f:
    key = json.load(f)
    wallet = Keypair.from_secret_key(bytes(key))
    my_address = wallet.public_key

client = Client(RPC)
sudah_beli = []

# === AMBIL TOKEN BARU DARI PUMPFUN ===
def get_recent_tokens():
    try:
        res = requests.get(PUMPFUN_API, headers=HEADERS)
        if res.status_code == 200:
            data = res.json()
            return data if isinstance(data, list) else []
        else:
            print(f"[❌] Gagal ambil token. Status code: {res.status_code}")
            return []
    except Exception as e:
        print("[⚠️] Error ambil token:", e)
        return []

# === CEK HARGA TOKEN DI JUPITER ===
def get_token_price(token_mint):
    try:
        res = requests.get(f"{JUPITER_API}{token_mint}")
        if res.status_code == 200:
            return float(res.json()["data"][token_mint]["price"])
    except:
        return None

# === FUNGSI BELI TOKEN (DUMMY) ===
def buy_token(token_address):
    print(f"💥 BUYING token: {token_address}")
    try:
        lamports = int(BUY_AMOUNT_SOL * 1_000_000_000)
        tx = Transaction()
        instr = transfer(TransferParams(
            from_pubkey=my_address,
            to_pubkey=my_address,
            lamports=lamports
        ))
        tx.add(instr)
        response = client.send_transaction(tx, wallet, opts=TxOpts(skip_preflight=True))
        print("✅ Transaksi dummy terkirim:", response)
    except Exception as e:
        print("❌ Gagal beli token:", e)

# === LOOP UTAMA ===
while True:
    print("🔍 Cek token baru...")
    tokens = get_recent_tokens()

    for token in tokens:
        token_address = token.get("mint")
        token_name = token.get("name", "UNKNOWN")
        buyer_count = token.get("buyerCount", 0)

        print(f"📦 Token: {token_name} | Buyers: {buyer_count}")

        if token_address and token_address not in sudah_beli and buyer_count >= MIN_BUYER_COUNT:
            price = get_token_price(token_address)
            if price:
                print(f"🚀 Beli Token: {token_name} | Buyers: {buyer_count} | Harga: ${price}")
                buy_token(token_address)
                sudah_beli.append(token_address)
            else:
                print(f"⚠️ Harga tidak tersedia untuk {token_name}")

    time.sleep(5)
