import requests
import time
import datetime
import telebot

# Token dan user ID langsung ditulis di script (hardcoded)
TOKEN_TELEGRAM = "8184173057:AAFxfvVPUpwoWHP3LPnZM1b1qQy–E96sGA"
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
