import requests

TOKEN_INFO = {
    "usdt": {"id": "tether", "address": "UNKNOWN", "decimals": 6},
    "usdc": {"id": "usd-coin", "address": "UNKNOWN", "decimals": 6},
    "weth": {"id": "weth", "address": "UNKNOWN", "decimals": 18},
    "steth": {"id": "steth", "address": "UNKNOWN", "decimals": 18},  
    "crv": {"id": "curve-dao-token", "address": "UNKNOWN", "decimals": 18},
    "frax": {"id": "frax", "address": "UNKNOWN", "decimals": 18},
}

def fetch_addresses():
    for symbol, info in TOKEN_INFO.items():
        try:
            r = requests.get(f"https://api.coingecko.com/api/v3/coins/{info['id']}")
            data = r.json()
            eth_addr = data.get("platforms", {}).get("ethereum")

            if eth_addr:
                TOKEN_INFO[symbol]["address"] = eth_addr
                print(f"✅ {symbol.upper()} → {eth_addr}")
            else:
                print(f"⚠️ {symbol.upper()} has no Ethereum address")
        except Exception as e:
            print(f"❌ Error on {symbol.upper()}: {e}")

if __name__ == "__main__":
    fetch_addresses()
