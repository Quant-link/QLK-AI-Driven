import json
import os
from app.routing.dex_clients.coingecko import fetch_top_100_tokens
from app.routing.dex_clients.dexscreener import get_token_info

TOKENS_PATH = os.path.join(os.path.dirname(__file__), "tokens.json")

# 🧱 Default fallback tokens (hardcoded)
TOKENS = {
    "ETH": {
        "chain": "ethereum",
        "address": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    },
    "USDC": {
        "chain": "ethereum",
        "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
    },
    "DAI": {
        "chain": "ethereum",
        "address": "0x6b175474e89094c44da98b954eedeac495271d0f"
    },
    "WBTC": {
        "chain": "ethereum",
        "address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    },
    "UNI": {
        "chain": "ethereum",
        "address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
    },
}

# 📥 Enrich token list with Coingecko + Dexscreener
def enrich_tokens_with_coingecko():
    top_tokens = fetch_top_100_tokens()
    enriched = []

    for token in top_tokens:
        try:
            token_id = token["id"]
            symbol = token["symbol"].upper()

            token_info = get_token_info(token_id) or get_token_info(symbol)

            if token_info:
                enriched.append({
                    "symbol": symbol,
                    "chain": token_info["chain"],
                    "address": token_info["address"]
                })
                print(f"✅ Added {symbol}: chain={token_info['chain']}, address={token_info['address']}")
            else:
                print(f"❌ No data for {symbol}")
        except Exception as e:
            print(f"⚠️ Error processing {token.get('symbol')}: {e}")
            continue

    return enriched

# 🔄 JSON dosyasından yükleme (dict formatında)
try:
    with open(TOKENS_PATH) as f:
        tokens_list = json.load(f)
        TOKENS = {
            token["symbol"]: {
                "chain": token["chain"],
                "address": token["address"]
            }
            for token in tokens_list
        }
except FileNotFoundError:
    TOKENS = {}
    print("⚠️ tokens.json not found, TOKENS dict is empty.")

# 🧪 CLI çalıştırıldığında yeni token listesi kaydet
if __name__ == "__main__":
    all_tokens = enrich_tokens_with_coingecko()
    with open(TOKENS_PATH, "w") as f:
        json.dump(all_tokens, f, indent=2)
    print(f"\n✅ Saved {len(all_tokens)} tokens to {TOKENS_PATH}")
