import requests
import random
from app.config.tokens import TOKENS
import math

def fetch_token_data(symbol):
    if symbol not in TOKENS:
        return []

    token_info = TOKENS[symbol]

    if "address" in token_info:
        chain = token_info["chain"]
        address = token_info["address"]
        url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{address}"
        is_pairs_api = True

    elif "id" in token_info:
        search_term = token_info["id"]
        url = f"https://api.dexscreener.com/latest/dex/search?q={search_term}"
        is_pairs_api = False

    else:
        print(f"⚠️ {symbol} has no usable address or id.")
        return []

    print(f"\n🔍 Fetching {symbol} from {url}...")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"❌ Failed to fetch {symbol}")
        return []

    data = response.json()

    # Parse response
    if is_pairs_api:
        if "pair" not in data:
            print(f"❌ No pair found for {symbol}")
            return []

        pair = data["pair"]
        pairs = [pair]
    else:
        pairs = data.get("pairs", [])
        if not pairs:
            print(f"❌ No pairs found for {symbol}")
            return []

    results = []
    for pair in pairs[:3]:  
        try:
            results.append({
                "symbol": symbol.upper(),
                "dex": pair.get("dexId", None),
                "price": float(pair["priceUsd"]),
                "liquidity": float(pair["liquidity"]["usd"]),
                "volume": float(pair["volume"]["h24"]),
                "volatility": round(random.uniform(0.0, 5.0), 2)
            })
        except Exception as e:
            print(f"⚠️ Parse error for {symbol}: {e}")
            continue

    return results

def fetch_gas_costs() -> dict:
    try:
        eth_resp = requests.get("https://api.etherscan.io/api?module=gastracker&action=gasoracle", timeout=3)
        eth_data = eth_resp.json()
        eth = {
            "standard": float(eth_data["result"]["SafeGasPrice"]),
            "fast": float(eth_data["result"]["ProposeGasPrice"]),
            "instant": float(eth_data["result"]["FastGasPrice"]),
        }

        return {
            "ethereum": eth,
            "bsc": {"standard": 5, "fast": 6, "instant": 8},
            "polygon": {"standard": 35, "fast": 45, "instant": 60}
        }

    except Exception as e:
        print(f"[ERROR] Gas API failed: {e}")
        return {
            "ethereum": {"standard": 25, "fast": 30, "instant": 40},
            "bsc": {"standard": 5, "fast": 6, "instant": 8},
            "polygon": {"standard": 35, "fast": 45, "instant": 60}
        }
    
def calculate_slippage(trade_size_usd: float, liquidity_usd: float) -> float:
    """
    Calculates estimated slippage (%) for a given trade size and liquidity.
    """
    if liquidity_usd <= 0:
        return 100.0  
    
    slippage_factor = math.sqrt(trade_size_usd / liquidity_usd)
    volatility_adjustment = 1.2  

    slippage_pct = slippage_factor * volatility_adjustment * 100
    return min(slippage_pct, 50.0)  