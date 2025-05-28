import requests, json, time
from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
from solana.system_program import TransferParams, transfer

# ============ KONFIGURASI ============
PUMPFUN_API = "https://api.pump.fun/markets/recent"
JUPITER_PRICE_API = "https://price.jup.ag/v4/price?ids="
RPC = "https://api.mainnet-beta.solana.com"
BUY_AMOUNT_SOL = 0.03
MIN_BUYER_COUNT = 1
SLIPPAGE = 0.2
# ======================================

# ============ LOAD WALLET ============
with open("my-autobuy-wallet.json", "r") as f:
    key = json.load(f)
    wallet = Keypair.from_secret_key(bytes(key))
    my_address = wallet.public_key
client = Client(RPC)
sudah_beli = []

# ============ FUNGSI AMBIL TOKEN BARU ============
def get_recent_tokens():
    try:
        res = requests.get(PUMPFUN_API).json()
        return res["markets"]
    except:
        return []

# ============ FUNGSI AMBIL HARGA DARI JUPITER ============
def get_token_price(token_mint):
    try:
        url = f"{JUPITER_PRICE_API}{token_mint}"
        res = requests.get(url).json()
        return float(res['data'][token_mint]['price'])
    except:
        return None

# ============ FUNGSI BELI TOKEN (dummy transfer) ============
def buy_token(token_address):
    print(f"[BUYING] Token: {token_address}")
    try:
        lamports = int(BUY_AMOUNT_SOL * 1_000_000_000)
        tx = Transaction()
        instr = transfer(TransferParams(
            from_pubkey=my_address,
            to_pubkey=my_address,  # dummy: transfer ke wallet sendiri
            lamports=lamports
        ))
        tx.add(instr)
        response = client.send_transaction(tx, wallet, opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed"))
        print("[✅] Transaksi dummy terkirim:", response)
    except Exception as e:
        print("[❌] Gagal transaksi:", str(e))

# ============ LOOP UTAMA ============
while True:
    print("🔄 Cek token baru...")
    tokens = get_recent_tokens()

    for token in tokens:
        token_address = token["mint"]
        buyer_count = token.get("buyerCount", 0)

        if token_address not in sudah_beli and buyer_count >= MIN_BUYER_COUNT:
            price = get_token_price(token_address)
            if price:
                print(f"🚀 Token Baru: {token['name']} | Buyers: {buyer_count} | Harga: ${price}")
                buy_token(token_address)
                sudah_beli.append(token_address)
            else:
                print(f"⚠️ Harga tidak tersedia untuk {token['name']}")

    time.sleep(5)
