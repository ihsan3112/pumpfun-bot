import requests, json, time
from solders.pubkey import Pubkey as PublicKey
from solana.rpc.api import Client
from solders.keypair import Keypair
from solana.transaction import Transaction
from solana.rpc.types import TxOpts
from solders.system_program import transfer, TransferParams

PUMPFUN_API = "https://api.pump.fun/markets/recent"
JUPITER_PRICE_API = "https://price.jup.ag/v4/price?ids="
RPC = "https://api.mainnet-beta.solana.com"

MIN_BUYER_COUNT = 1
BUY_AMOUNT_SOL = 0.03  # jumlah pembelian
SLIPPAGE = 0.2

with open("my-autobuy-wallet.json", "r") as f:
    key = json.load(f)
    wallet = Keypair.from_secret_key(bytes(key))
    my_address = wallet.pubkey()

client = Client(RPC)
sudah_beli = []

def get_recent_tokens():
    try:
        res = requests.get(PUMPFUN_API).json()
        return res["markets"]
    except:
        return []

def get_token_price(token_mint):
    try:
        url = f"{JUPITER_PRICE_API}{token_mint}"
        res = requests.get(url).json()
        return float(res['data'][token_mint]['price'])
    except:
        return None

def buy_token(token_address):
    print(f"[BUYING] Token: {token_address}")
    # Logika dummy transfer agar mudah diuji (ganti dengan Jupiter TX real untuk live version)
    try:
        tx = Transaction()
        lamports = int(BUY_AMOUNT_SOL * 1_000_000_000)
        instr = transfer(TransferParams(from_pubkey=my_address, to_pubkey=my_address, lamports=lamports))
        tx.add(instr)
        response = client.send_transaction(tx, wallet, opts=TxOpts(skip_preflight=True, preflight_commitment="confirmed"))
        print("[✅] Transaksi terkirim:", response)
    except Exception as e:
        print("[❌] Gagal kirim transaksi:", str(e))

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
                print(f"⚠️ Tidak ada harga dari Jupiter untuk {token['name']}")
    
    time.sleep(5)
