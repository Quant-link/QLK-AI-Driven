import logging
import requests
import math
import time
import os
from typing import Optional
from decimal import Decimal
from app.config.tokens import TOKENS
import json

_TOKEN_CACHE = {}
_TOKEN_CACHE_TTL = 60 

def fetch_token_data(symbol):
    now = time.time()

    if symbol in _TOKEN_CACHE:
        ts, cached_data = _TOKEN_CACHE[symbol]
        if now - ts < _TOKEN_CACHE_TTL:
            logging.debug(f"[CACHE] Returning cached result for {symbol}")
            return cached_data

    token_info = TOKENS.get(symbol)
    if not token_info:
        return []

    address = token_info.get("address")
    if address:
        url = f"https://api.dexscreener.com/latest/dex/search?q={address}"
    elif token_info.get("search"):
        search_term = token_info["search"]
        url = f"https://api.dexscreener.com/latest/dex/search?q={search_term}"
    else:
        logging.warning(f"⚠️ {symbol} has no usable address or search term.")
        return []

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 429:
            logging.warning(f"[RATE LIMIT] DexScreener rate-limited for {symbol}, retrying...")
            time.sleep(3) 
            response = requests.get(url, timeout=10)
        time.sleep(1.0) 
    except Exception as e:
        logging.error(f"❌ Request error for {symbol}: {e}")
        return []

    if response.status_code != 200:
        logging.error(f"❌ Failed to fetch {symbol}, status={response.status_code}")
        return []

    data = response.json()
    pairs = data.get("pairs", [])
    if not pairs:
        logging.warning(f"[WARN] No pairs found for {symbol} from {url}")
        _TOKEN_CACHE[symbol] = (now, [])
        return []

    results = []
    for pair in pairs[:3]:  
        try:
            results.append({
                "symbol": symbol.upper(),
                "dex": pair.get("dexId"),
                "price": float(pair["priceUsd"]),
                "liquidity": float(pair["liquidity"]["usd"]),
                "volume": float(pair["volume"]["h24"]),
                "volatility": None,
                "timestamp": pair.get("timestamp") or None,
                "chain": pair.get("chainId") or token_info.get("chain")
            })
        except Exception as e:
            logging.warning(f"⚠️ Parse error for {symbol}: {e}")
            continue

    _TOKEN_CACHE[symbol] = (now, results)
    return results

def fetch_gas_costs() -> dict:
    try:
        eth_resp = requests.get(
            "https://api.etherscan.io/api?module=gastracker&action=gasoracle",
            timeout=3
        )
        eth_data = eth_resp.json()
        return {
            "ethereum": {
                "standard": float(eth_data["result"]["SafeGasPrice"]),
                "fast": float(eth_data["result"]["ProposeGasPrice"]),
                "instant": float(eth_data["result"]["FastGasPrice"]),
            }
        }
    except Exception as e:
        logging.error(f"[ERROR] Gas API failed: {e}")
        return {}

def calculate_slippage(trade_size_usd: float, liquidity_usd: float) -> float:
    if liquidity_usd <= 0:
        return 100.0
    slippage_factor = math.sqrt(trade_size_usd / liquidity_usd)
    return min(slippage_factor * 1.2 * 100, 50.0)

def fetch_token_data_extended(symbol: str):
    try:
        from app.strategies.arbitrage_and_twap import fetch_price_from_uniswap_sushi
        data = fetch_price_from_uniswap_sushi("QLK", symbol, Decimal("1"))
        logging.debug(f"[DEBUG] Raw data from fetch_price_from_uniswap_sushi for {symbol}: {json.dumps(data, indent=2, default=str)}")

        if data:
            best_pair = max(data, key=lambda x: x.get("liquidity", 0))
            return [{
                "symbol": symbol.upper(),
                "dex": best_pair["dex"],
                "price": float(best_pair["price"]),
                "liquidity": best_pair["liquidity"],
                "volume": best_pair["volume"],
                "volatility": None,
                "timestamp": None,
                "chain": "ethereum",
                "pairAddress": best_pair["pairAddress"]
            }]
        else:
            logging.warning(f"[TOKEN_DATA] No liquidity for {symbol}")
            return []
    except Exception as e:
        logging.error(f"[TOKEN_DATA] Failed to fetch price for {symbol}: {e}")
        return []

_CG_CACHE = {"ts": 0, "usd_per_qlk": None}
_CG_TTL = 60

def get_usd_per_qlk() -> Optional[float]:
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
        logging.error(f"[ERROR] Failed to fetch QLK price: {e}")
        return None
