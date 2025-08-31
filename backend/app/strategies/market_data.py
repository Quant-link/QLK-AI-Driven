import os
import requests
from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from app.config.tokens import TOKENS

router = APIRouter()

CG_BASE_URL = os.getenv("COINGECKO_BASE_URL", "https://pro-api.coingecko.com/api/v3")
CG_HEADERS = {"accept": "application/json"}
CG_KEY = os.getenv("COINGECKO_API_KEY")
if CG_KEY:
    CG_HEADERS["x-cg-pro-api-key"] = CG_KEY

def fetch_from_coingecko(cg_id: str) -> Optional[Dict[str, Any]]:
    try:
        url = f"{CG_BASE_URL}/coins/{cg_id}"
        res = requests.get(url, headers=CG_HEADERS, timeout=15)
        if res.status_code != 200:
            print(f"[WARN] CG {cg_id} {res.status_code}")
            return None
        data = res.json()
        market = data.get("market_data", {}) or {}

        price = (market.get("current_price") or {}).get("usd")
        high_24h = (market.get("high_24h") or {}).get("usd")
        low_24h = (market.get("low_24h") or {}).get("usd")

        volatility = None
        if high_24h and low_24h and price:
            try:
                volatility = (high_24h - low_24h) / price
            except Exception:
                volatility = None

        return {
            "id": data.get("id"),
            "symbol": (data.get("symbol") or "").upper(),
            "name": data.get("name"),
            "price": price,
            "change_24h": market.get("price_change_percentage_24h"),
            "change_7d": market.get("price_change_percentage_7d"),
            "volume_24h": (market.get("total_volume") or {}).get("usd"),
            "market_cap": (market.get("market_cap") or {}).get("usd"),
            "liquidity": (market.get("total_value_locked") or {}).get("usd"),
            "circulating_supply": market.get("circulating_supply"),
            "total_supply": market.get("total_supply"),
            "fdv": (market.get("fully_diluted_valuation") or {}).get("usd"),
            "ath": (market.get("ath") or {}).get("usd"),
            "atl": (market.get("atl") or {}).get("usd"),
            "volatility": volatility,
        }
    except Exception as e:
        print(f"[ERROR] CG fetch {cg_id}: {e}")
        return None

def fetch_from_coinbase(symbol: str) -> Optional[Dict[str, Any]]:
    try:
        url = f"https://api.coinbase.com/v2/prices/{symbol}-USD/spot"
        res = requests.get(
            url,
            headers={"CB-ACCESS-KEY": os.getenv("COINBASE_API_KEY", "")},
            timeout=10
        )
        if res.status_code != 200:
            return None
        data = res.json().get("data", {})
        return {
            "id": symbol.lower(),
            "symbol": symbol.upper(),
            "name": symbol.upper(),
            "price": float(data.get("amount")),
            "change_24h": None,  
            "change_7d": None,
            "volume_24h": None,
            "market_cap": None,
            "liquidity": None,
            "circulating_supply": None,
            "total_supply": None,
            "fdv": None,
            "ath": None,
            "atl": None,
            "volatility": None,
        }
    except Exception as e:
        print(f"[ERROR] Coinbase fetch {symbol}: {e}")
        return None

def fetch_from_dexscreener(address: str) -> Optional[Dict[str, Any]]:
    try:
        url = f"https://api.dexscreener.com/latest/dex/search?q={address}"
        print(f"🔍 Fetching (search) {address} from {url}...")
        res = requests.get(url, timeout=15)
        if res.status_code != 200:
            return None
        data = res.json()
        pairs = data.get("pairs")
        if not pairs:
            print(f"[WARN] No pairs found for {address}")
            return None

        best_pair = max(pairs, key=lambda x: float(x.get("liquidity", {}).get("usd", 0) or 0))

        return {
            "id": best_pair.get("baseToken", {}).get("address", "").lower(),
            "symbol": (best_pair.get("baseToken", {}).get("symbol") or "").upper(),
            "name": best_pair.get("baseToken", {}).get("name"),
            "price": float(best_pair.get("priceUsd") or 0),
            "change_24h": float((best_pair.get("priceChange") or {}).get("h24", 0) or 0),
            "change_7d": float((best_pair.get("priceChange") or {}).get("h7d", 0) or 0),  # ✅ düzeltildi
            "volume_24h": float((best_pair.get("volume") or {}).get("h24", 0) or 0),
            "market_cap": None,
            "liquidity": float((best_pair.get("liquidity") or {}).get("usd", 0) or 0),
            "circulating_supply": None,
            "total_supply": None,
            "fdv": None,
            "ath": None,
            "atl": None,
            "volatility": None,
        }
    except Exception as e:
        print(f"[ERROR] DexScreener fetch {address}: {e}")
        return None

def get_token_data(symbol: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    cg_id = meta.get("cg_id")
    address = meta.get("address")

    data = {}
    if cg_id:
        cg_data = fetch_from_coingecko(cg_id) or {}
        data.update(cg_data)

    if (not data.get("price") or data.get("price") == 0) and symbol:
        cb_data = fetch_from_coinbase(symbol) or {}
        data["price"] = cb_data.get("price")

    if address:
        ds_data = fetch_from_dexscreener(address) or {}
        for key in ["liquidity", "volume_24h"]:
            if not data.get(key):
                data[key] = ds_data.get(key)

    enriched = {
        "id": data.get("id") or symbol.lower(),
        "symbol": data.get("symbol") or symbol.upper(),
        "name": data.get("name") or symbol.upper(),
        "price": data.get("price") or 0.0,
        "change_24h": data.get("change_24h") or 0.0,
        "change_7d": data.get("change_7d") or 0.0,
        "volume_24h": data.get("volume_24h") or 0.0,
        "market_cap": data.get("market_cap") or 0.0,
        "liquidity": data.get("liquidity") or 0.0,
        "circulating_supply": data.get("circulating_supply") or 0.0,
        "total_supply": data.get("total_supply") or 0.0,
        "fdv": data.get("fdv") or 0.0,
        "ath": data.get("ath") or 0.0,
        "atl": data.get("atl") or 0.0,
        "volatility": data.get("volatility") or 0.0,
    }

    return enriched

@router.get("/market_data")
def get_market_data() -> Dict[str, List[Dict[str, Any]]]:
    out = []
    for sym, meta in TOKENS.items():
        token_data = get_token_data(sym, meta)

        if not token_data.get("price") or token_data.get("price") == 0:
            continue
        if not token_data.get("market_cap") and not token_data.get("volume_24h"):
            continue

        out.append(token_data)

    return {"tokens": out}
