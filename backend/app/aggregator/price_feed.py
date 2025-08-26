import requests
import random
import math
import time
import os
from app.config.tokens import TOKENS


def fetch_token_data(symbol):
    if symbol not in TOKENS:
        return []

    token_info = TOKENS[symbol]

    if "address" in token_info and token_info["address"]:
        address = token_info["address"]
        url = f"https://api.dexscreener.com/latest/dex/search?q={address}"
        is_pairs_api = False

    elif "search" in token_info and token_info["search"]:
        search_term = token_info["search"]
        url = f"https://api.dexscreener.com/latest/dex/search?q={search_term}"
        is_pairs_api = False

    else:
        print(f"⚠️ {symbol} has no usable address or search term.")
        return []

    print(f"\n🔍 Fetching ({'pairs' if is_pairs_api else 'search'}) {symbol} from {url}...")
    try:
        response = requests.get(url, timeout=10)
    except Exception as e:
        print(f"❌ Request error for {symbol}: {e}")
        return []

    if response.status_code != 200:
        print(f"❌ Failed to fetch {symbol}, status={response.status_code}")
        return []

    data = response.json()

    if is_pairs_api:
        pair = data.get("pair")
        if not pair:
            print(f"[WARN] No pairs found for {symbol} from {url}")
            return []
        pairs = [pair]
    else:
        pairs = data.get("pairs", [])
        if not pairs:
            print(f"[WARN] No pairs found for {symbol} from {url}")
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
                "volatility": round(random.uniform(0.0, 5.0), 2),
                "timestamp": pair.get("timestamp") or None,
                "chain": (pair.get("chainId") or token_info.get("chain")) 
            })
        except Exception as e:
            print(f"⚠️ Parse error for {symbol}: {e}")
            continue

    return results


def fetch_gas_costs() -> dict:
    try:
        eth_resp = requests.get(
            "https://api.etherscan.io/api?module=gastracker&action=gasoracle",
            timeout=3
        )
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
    if liquidity_usd <= 0:
        return 100.0

    slippage_factor = math.sqrt(trade_size_usd / liquidity_usd)
    volatility_adjustment = 1.2

    slippage_pct = slippage_factor * volatility_adjustment * 100
    return min(slippage_pct, 50.0)


def fetch_token_data_extended(symbol: str):
    from app.config.constants import QLK_SUPPORTED_DEX

    raw = fetch_token_data(symbol)
    if not raw:
        return []

    filtered = []
    for e in raw:
        dex = (e.get("dex") or "").lower()
        item = dict(e)
        item["dex"] = dex 
        if dex in QLK_SUPPORTED_DEX:
            filtered.append(item)

    return filtered if filtered else raw


_CG_CACHE = {"ts": 0, "usd_per_qlk": None}
_CG_TTL = 60  # saniye

def get_usd_per_qlk() -> float | None:
    now = time.time()
    if _CG_CACHE["usd_per_qlk"] and now - _CG_CACHE["ts"] < _CG_TTL:
        return _CG_CACHE["usd_per_qlk"]

    qlk_id = "quantlink"
    base_url = os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")
    api_key = os.getenv("COINGECKO_API_KEY")

    headers = {"accept": "application/json"}
    if api_key:
        headers["x-cg-pro-api-key"] = api_key

    url = f"{base_url}/simple/price"
    params = {"ids": qlk_id, "vs_currencies": "usd"}

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)
        r.raise_for_status()
        data = r.json()
        price = float(data[qlk_id]["usd"])
        _CG_CACHE.update({"ts": now, "usd_per_qlk": price})
        return price
    except Exception as e:
        print(f"[ERROR] Failed to fetch QLK price: {e}")
        return None
