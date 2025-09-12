
import os
import requests
from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from app.config.tokens import TOKENS
import time
import math

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

        if not volatility and market.get("price_change_percentage_24h") is not None:
            try:
                volatility = abs(market.get("price_change_percentage_24h")) / 100
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
            return None

        best_pair = max(pairs, key=lambda x: float(x.get("liquidity", {}).get("usd", 0) or 0))

        return {
            "id": best_pair.get("baseToken", {}).get("address", "").lower(),
            "symbol": (best_pair.get("baseToken", {}).get("symbol") or "").upper(),
            "name": best_pair.get("baseToken", {}).get("name"),
            "price": float(best_pair.get("priceUsd") or 0),
            "change_24h": float((best_pair.get("priceChange") or {}).get("h24", 0) or 0),
            "change_7d": float((best_pair.get("priceChange") or {}).get("h7d", 0) or 0),
            "volume_24h": float((best_pair.get("volume") or {}).get("h24", 0) or 0),
            "market_cap": None,
            "liquidity": float((best_pair.get("liquidity") or {}).get("usd", 0) or 0),
            "circulating_supply": None,
            "total_supply": None,
            "atl": None,
            "volatility": None,
        }
    except Exception as e:
        print(f"[ERROR] DexScreener fetch {address}: {e}")
        return None
    
def fetch_from_cmc_bulk(symbols: List[str]) -> Dict[str, Dict[str, Any]]:
    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {"X-CMC_PRO_API_KEY": os.getenv("CMC_API_KEY")}
        
        result: Dict[str, Dict[str, Any]] = {}
        chunk_size = 25  

        for i in range(0, len(symbols), chunk_size):
            chunk = symbols[i:i+chunk_size]
            params = {"symbol": ",".join([s.upper() for s in chunk]), "convert": "USD"}
            
            res = requests.get(url, headers=headers, params=params, timeout=20)
            if res.status_code != 200:
                print(f"[WARN] CMC bulk fetch {chunk} {res.status_code}")
                continue

            data = res.json().get("data", {})
            for sym, token_data in data.items():
                quote = token_data.get("quote", {}).get("USD", {})
                result[sym.upper()] = {
                    "id": str(token_data.get("id")),
                    "symbol": sym.upper(),
                    "name": token_data.get("name"),
                    "price": quote.get("price"),
                    "change_24h": quote.get("percent_change_24h"),
                    "change_7d": quote.get("percent_change_7d"),
                    "volume_24h": quote.get("volume_24h"),
                    "market_cap": quote.get("market_cap"),
                    "circulating_supply": token_data.get("circulating_supply"),
                    "total_supply": token_data.get("total_supply"),
                    "atl": None,
                    "volatility": None,
                    "self_reported_market_cap": token_data.get("self_reported_market_cap")
                }
            time.sleep(1)
        return result
    except Exception as e:
        print(f"[ERROR] CMC bulk fetch: {e}")
        return {}

def fetch_from_geckoterminal(gt_id: str) -> Optional[Dict[str, Any]]:
    try:
        parts = gt_id.split('/')
        url = f"https://api.geckoterminal.com/api/v2/networks/{parts[0]}/tokens/{parts[1].lower()}"
        res = requests.get(url, timeout=15)
        if res.status_code != 200:
            print(f"[WARN] GT {gt_id} {res.status_code}")
            return None

        raw = res.json()
        attributes = raw.get("data", {}).get("attributes", {})
        if not attributes:
            print(f"[WARN] GT {gt_id}: no attributes in response {raw}")
            return None

        price = float(attributes.get("price_usd") or 0)
        high_24h = float(attributes.get("high_24h_usd") or 0)
        low_24h = float(attributes.get("low_24h_usd") or 0)
        market_cap = float(attributes.get("market_cap_usd") or 0)
        fdv = float(attributes.get("fdv_usd") or 0)

        volatility = None
        if high_24h > 0 and low_24h > 0 and price > 0:
            tmp_vol = (high_24h - low_24h) / price
            if tmp_vol < 10:  
                volatility = tmp_vol
        if not volatility and attributes.get("price_change_percentage_24h") is not None:
            volatility = abs(float(attributes.get("price_change_percentage_24h"))) / 100

        circulating_supply = None
        total_supply = None
        if market_cap > 0 and price > 0:
            circulating_supply = market_cap / price
        if fdv > 0 and price > 0:
            total_supply = fdv / price

        return {
            "price": price,
            "change_24h": float(attributes.get("price_change_percentage_24h") or 0),
            "volume_24h": float((attributes.get("volume_usd") or {}).get("h24", 0)),
            "market_cap": market_cap if market_cap > 0 else None,
            "fdv": fdv if fdv > 0 else None,
            "liquidity": float(attributes.get("liquidity_usd") or 0),
            "volatility": volatility,
            "circulating_supply": circulating_supply,
            "total_supply": total_supply,
        }
    except Exception as e:
        print(f"[ERROR] GeckoTerminal fetch {gt_id}: {e}")
        return None

def get_token_data(symbol: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    cg_id = meta.get("cg_id") or meta.get("coingecko_id")
    address = meta.get("address")
    gt_id = meta.get("geckoterminal_id")
    data: Dict[str, Any] = {}

    if cg_id:
        cg_data = fetch_from_coingecko(cg_id) or {}
        data.update(cg_data)

    if (not data.get("price") or data.get("price") == 0) and symbol:
        cb_data = fetch_from_coinbase(symbol) or {}
        if cb_data:
            data.update(cb_data)

    if address:
        ds_data = fetch_from_dexscreener(address) or {}
        if ds_data:
            for key in ["liquidity", "volume_24h", "price"]:
                if data.get(key) is None and key in ds_data:
                    data[key] = ds_data[key]

    if gt_id:
        gt_data = fetch_from_geckoterminal(gt_id) or {}
        if gt_data:
            for key, value in gt_data.items():
                if not data.get(key):
                    data[key] = value

    if not data.get("market_cap") or data.get("market_cap") <= 0:
        if data.get("price") and data.get("circulating_supply"):
            try:
                data["market_cap"] = float(data["price"]) * float(data["circulating_supply"])
            except:
                data["market_cap"] = 0
        elif data.get("fdv"):
            data["market_cap"] = data["fdv"]
        elif data.get("volume_24h") and data.get("liquidity") and data.get("liquidity") > 0:
            try:
                ratio = float(data["volume_24h"]) / float(data["liquidity"])
                data["market_cap"] = float(data["volume_24h"]) * ratio
            except:
                data["market_cap"] = 0
        elif data.get("price") and data.get("total_supply"):
            try:
                data["market_cap"] = float(data["price"]) * float(data["total_supply"])
            except:
                data["market_cap"] = 0
        else:
            data["market_cap"] = 0

    if not data.get("circulating_supply") and data.get("market_cap") and data.get("price"):
        try:
            data["circulating_supply"] = float(data["market_cap"]) / float(data["price"])
        except:
            data["circulating_supply"] = None

    if not data.get("total_supply") and data.get("fdv") and data.get("price"):
        try:
            data["total_supply"] = float(data["fdv"]) / float(data["price"])
        except:
            data["total_supply"] = None

    vol = data.get("volatility")

    if vol is None:
        if data.get("change_24h") is not None:
            vol = abs(float(data["change_24h"])) / 100
        elif data.get("change_7d") is not None:
            vol = abs(float(data["change_7d"])) / 700
        elif data.get("volume_24h") and data.get("market_cap") and data["market_cap"] > 0:
            try:
                vol = float(data["volume_24h"]) / float(data["market_cap"])
            except:
                vol = 0
        else:
            vol = 0

    try:
        vol = float(vol)
        if vol < 0 or vol > 5:
            print(f"[CLAMP] {symbol}: crazy volatility {vol}, forced to 0")
            vol = 0
    except:
        vol = 0

    data["volatility"] = vol

    enriched = {
        "id": data.get("id") or symbol.lower(),
        "symbol": data.get("symbol") or symbol.upper(),
        "name": data.get("name") or symbol.upper(),
        "price": data.get("price") or 0,
        "change_24h": data.get("change_24h"),
        "change_7d": data.get("change_7d"),
        "volume_24h": data.get("volume_24h") or 0,
        "market_cap": data.get("market_cap") or 0,
        "liquidity": data.get("liquidity") or 0,
        "circulating_supply": data.get("circulating_supply"),
        "total_supply": data.get("total_supply"),
        "atl": data.get("atl"),
        "volatility": data.get("volatility") or 0,
    }

    print(f"[DEBUG] {symbol}: price={enriched['price']} mcap={enriched['market_cap']} vol={enriched['volatility']} supply={enriched['circulating_supply']}")
    return enriched


def get_token_data(symbol: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    cg_id = meta.get("cg_id") or meta.get("coingecko_id")
    address = meta.get("address")
    gt_id = meta.get("geckoterminal_id")
    data: Dict[str, Any] = {}

    if cg_id:
        cg_data = fetch_from_coingecko(cg_id) or {}
        data.update(cg_data)

    if (not data.get("price") or data.get("price") == 0) and symbol:
        cb_data = fetch_from_coinbase(symbol) or {}
        if cb_data:
            data.update(cb_data)

    if address:
        ds_data = fetch_from_dexscreener(address) or {}
        if ds_data:
            for key in ["liquidity", "volume_24h", "price"]:
                if data.get(key) is None and key in ds_data:
                    data[key] = ds_data[key]

    if gt_id:
        gt_data = fetch_from_geckoterminal(gt_id) or {}
        if gt_data:
            for key, value in gt_data.items():
                if not data.get(key):
                    data[key] = value

    if not data.get("market_cap"):
        if data.get("price") and data.get("circulating_supply"):
            try:
                data["market_cap"] = float(data["price"]) * float(data["circulating_supply"])
                print(f"[FALLBACK] {symbol}: market_cap calculated = {data['market_cap']}")
            except Exception:
                data["market_cap"] = None
        elif data.get("fdv"):
            data["market_cap"] = data["fdv"]
        elif data.get("volume_24h") and data.get("liquidity"):
            try:
                ratio = float(data["volume_24h"]) / max(float(data["liquidity"]), 1)
                data["market_cap"] = float(data["volume_24h"]) * ratio
                print(f"[ESTIMATED] {symbol}: market_cap estimated via vol/liquidity = {data['market_cap']}")
            except Exception:
                data["market_cap"] = None
        elif data.get("price") and data.get("total_supply"):
            try:
                data["market_cap"] = float(data["price"]) * float(data["total_supply"])
                print(f"[FALLBACK] {symbol}: market_cap from total_supply = {data['market_cap']}")
            except Exception:
                data["market_cap"] = None

    if not data.get("circulating_supply") and data.get("market_cap") and data.get("price"):
        try:
            data["circulating_supply"] = float(data["market_cap"]) / float(data["price"])
            print(f"[FALLBACK] {symbol}: supply estimated from mcap/price = {data['circulating_supply']}")
        except Exception:
            data["circulating_supply"] = None

    if not data.get("total_supply") and data.get("fdv") and data.get("price"):
        try:
            data["total_supply"] = float(data["fdv"]) / float(data["price"])
            print(f"[FALLBACK] {symbol}: total_supply estimated from fdv/price = {data['total_supply']}")
        except Exception:
            data["total_supply"] = None

    if data.get("volatility") is None:
        if data.get("change_24h") is not None:
            data["volatility"] = abs(data["change_24h"]) / 100
            print(f"[DEBUG] {symbol}: volatility from change_24h = {data['volatility']}")
        elif data.get("change_7d") is not None:
            data["volatility"] = abs(data["change_7d"]) / 700
            print(f"[DEBUG] {symbol}: volatility from change_7d = {data['volatility']}")
        elif data.get("volume_24h") and data.get("market_cap") and data["market_cap"] > 0:
            try:
                ratio = float(data["volume_24h"]) / float(data["market_cap"])
                data["volatility"] = ratio
                print(f"[FALLBACK] {symbol}: volatility estimated from volume/mcap = {ratio}")
            except Exception:
                data["volatility"] = None
        else:
            data["volatility"] = None

    try:
        vol = float(data.get("volatility") or 0)
        if vol < 0:
            vol = 0
        else:
            vol = math.log1p(vol)
        data["volatility"] = vol
    except Exception:
        data["volatility"] = 0

    enriched = {
        "id": data.get("id") or symbol.lower(),
        "symbol": data.get("symbol") or symbol.upper(),
        "name": data.get("name") or symbol.upper(),
        "price": data.get("price"),
        "change_24h": data.get("change_24h"),
        "change_7d": data.get("change_7d"),
        "volume_24h": data.get("volume_24h"),
        "market_cap": data.get("market_cap"),
        "liquidity": data.get("liquidity"),
        "circulating_supply": data.get("circulating_supply"),
        "total_supply": data.get("total_supply"),
        "atl": data.get("atl"),
        "volatility": data.get("volatility"),
    }

    print(f"[DEBUG] {symbol}: price={enriched['price']} mcap={enriched['market_cap']} vol={enriched['volatility']} supply={enriched['circulating_supply']}")
    return enriched


@router.get("/market_data")
def get_market_data() -> Dict[str, List[Dict[str, Any]]]:
    out = []

    symbols = list(TOKENS.keys())

    cmc_data_all = fetch_from_cmc_bulk(symbols)

    for sym, meta in TOKENS.items():
        token_data = get_token_data(sym, meta)

        cmc_info = cmc_data_all.get(sym.upper())
        if cmc_info:
            for k, v in cmc_info.items():
                if v is not None:
                    token_data[k] = v
            
            if not token_data.get("market_cap"):
                token_data["market_cap"] = cmc_info["self_reported_market_cap"]

            if not token_data.get("total_supply"):
                token_data["total_supply"] = cmc_info["max_supply"] 

            if not token_data.get("volume_24h"):
                token_data["volume_24h"] = cmc_info["volume_24h"]
            
            if not token_data.get("percent_change_24h"):
                token_data["percent_change_24h"] = cmc_info["change_24h"]
            
            if not token_data.get("percent_change_7d"):
                token_data["percent_change_7d"] = cmc_info["change_7d"]
            
            if not token_data.get("total_supply"):
                token_data["total_supply"] = cmc_info["total_supply"] 

        cg_id = meta.get("cg_id")
        if cg_id:
            coingecko_data = fetch_from_coingecko(cg_id)
            coingecko_info = coingecko_data.get(sym.upper())
            if coingecko_info:
                for k, v in coingecko_info.items():
                    if v is not None:
                        token_data[k] = v
            
                if not token_data.get("volume_24h"):
                    token_data["volume_24h"] = coingecko_info["priceChange"].get("h24") 
                if not token_data.get("total_supply"):
                    token_data["total_supply"] = coingecko_info["market_data"].get("total_supply")  

        address = meta.get("address")
        if address:
            dexsceener_data = fetch_from_dexscreener(address)
            if dexsceener_data:
                dexsceener_info = dexsceener_data.get(sym.lower())
                if dexsceener_info:
                    for k, v in dexsceener_info.items():
                        if v is not None:
                            token_data[k] = v
                
                    if not token_data.get("volume_24h"):
                        token_data["volume_24h"] = dexsceener_info["pairs"].get("h24")
                    if not token_data.get("market_cap"):
                        token_data["market_cap"] = dexsceener_info["pairs"].get("marketCap")
                    if not token_data.get("volume_24h"):
                        token_data["volume_24h"] = dexsceener_info["pairs"].get("volume").get("h24")  
                    if not token_data.get("total_supply"):
                        token_data["total_supply"] = dexsceener_info["market_data"].get("total_supply")                     

        if token_data.get("volatility") is None:
            if token_data.get("change_24h") is not None:
                token_data["volatility"] = abs(float(token_data["change_24h"])) / 100
                print(f"[DEBUG] {sym}: volatility from change_24h = {token_data['volatility']}")
            elif token_data.get("change_7d") is not None:
                token_data["volatility"] = abs(float(token_data["change_7d"])) / 700
                print(f"[DEBUG] {sym}: volatility from change_7d = {token_data['volatility']}")
            elif token_data.get("volume_24h") and token_data.get("market_cap") and token_data["market_cap"] > 0:
                try:
                    token_data["volatility"] = float(token_data["volume_24h"]) / float(token_data["market_cap"])
                    print(f"[FALLBACK] {sym}: volatility from volume/mcap = {token_data['volatility']}")
                except Exception as e:
                    print(f"[ERROR] {sym}: failed to calc fallback volatility ({e})")
                    token_data["volatility"] = None
            else:
                token_data["volatility"] = 0
                print(f"[DEBUG] {sym}: no volatility data, defaulted to 0")

        if not token_data.get("price"):
            continue
        out.append(token_data)

    return {"tokens": out}
