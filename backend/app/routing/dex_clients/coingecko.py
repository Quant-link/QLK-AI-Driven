import os, time, requests, logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

_CG_HEADERS = {"accept": "application/json"}
_api_key = os.getenv("COINGECKO_API_KEY")
if _api_key:
    _CG_HEADERS["x-cg-pro-api-key"] = _api_key

CG_BASE_URL = os.getenv("COINGECKO_BASE_URL", "https://pro-api.coingecko.com/api/v3")

ETH_RPC_URL = os.getenv("ETH_RPC_URL") 

def _to_checksum(addr: str) -> str:
    if not addr:
        return addr
    try:
        from eth_utils import to_checksum_address
        return to_checksum_address(addr)
    except Exception:
        return addr.lower()

def _rpc_get_decimals(address: str) -> Optional[int]:
    if not ETH_RPC_URL:
        return None
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [
                {
                    "to": address,
                    "data": "0x313ce567"
                },
                "latest"
            ]
        }
        r = requests.post(ETH_RPC_URL, json=payload, timeout=10)
        r.raise_for_status()
        result = r.json().get("result")
        if result and result != "0x":
            return int(result, 16)
    except Exception:
        pass
    return None

def _cg_get(path: str, params: Dict) -> Optional[dict]:
    try:
        r = requests.get(f"{CG_BASE_URL}{path}", headers=_CG_HEADERS, params=params, timeout=15)
        if r.status_code != 200:
            logger.warning(f"[WARN] CG {path} {r.status_code}")
            return None
        return r.json()
    except Exception as e:
        logger.error(f"[ERROR] CG request failed {path}: {e}")
        return None

def fetch_token_on_ethereum_by_cgid(cg_id: str):
    if not cg_id:
        return None
    detail = _cg_get(
        f"/coins/{cg_id}",
        {
            "localization": "false",
            "tickers": "false",
            "market_data": "false",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "false",
        }
    )
    if not detail:
        return None
    symbol = (detail.get("symbol") or "").upper()
    platforms = detail.get("detail_platforms") or detail.get("platforms") or {}
    eth_plat = platforms.get("ethereum") or platforms.get("Ethereum")
    if not eth_plat:
        return None
    address = (eth_plat.get("contract_address") or "").strip()
    if not address:
        return None
    try:
        from eth_utils import to_checksum_address
        address = to_checksum_address(address)
    except Exception:
        address = address.lower()
    decimals = eth_plat.get("decimal_place")
    if decimals is None:
        decimals = _rpc_get_decimals(address) or 18
    return {"symbol": symbol or "UNKNOWN", "address": address, "decimals": int(decimals)}

def fetch_usd_price_by_cgid(cg_id: str) -> float:
    if not cg_id:
        return 0.0
    data = _cg_get(
        "/simple/price",
        {"ids": cg_id, "vs_currencies": "usd"}
    )
    try:
        return float((data or {}).get(cg_id, {}).get("usd", 0.0))
    except Exception:
        return 0.0

_MARKETS_CACHE = {"ts": 0.0, "data": {}}
_MARKETS_TTL = int(os.getenv("COINGECKO_MARKETS_TTL_SEC", "60"))

def fetch_market_snapshot(tokens: List[Dict]) -> Dict[str, Dict]:
    now = time.time()
    if _MARKETS_CACHE["data"] and now - _MARKETS_CACHE["ts"] < _MARKETS_TTL:
        return {t["symbol"].upper(): _MARKETS_CACHE["data"].get(t["symbol"].upper()) for t in tokens}

    ids = [t["cg_id"] for t in tokens if t.get("cg_id")]
    out: Dict[str, Dict] = {}

    if ids:
        payloads = _cg_get(
            "/coins/markets",
            {
                "vs_currency": "usd",
                "ids": ",".join(ids),
                "order": "market_cap_desc",
                "per_page": len(ids),
                "page": 1,
                "sparkline": "false",
                "price_change_percentage": "24h,7d"
            }
        ) or []

        for p in payloads:
            sym = (p.get("symbol") or "").upper()
            out[sym] = {
                "price": p.get("current_price"),
                "change_24h": p.get("price_change_percentage_24h_in_currency"),
                "change_7d": p.get("price_change_percentage_7d_in_currency"),
                "market_cap": p.get("market_cap"),
                "circulating_supply": p.get("circulating_supply"),
                "total_supply": p.get("total_supply"),
                "fdv": p.get("fully_diluted_valuation"),
                "ath": p.get("ath"),
                "atl": p.get("atl"),
            }

    for t in tokens:
        sym = t["symbol"].upper()
        if sym not in out:
            address = t.get("address")
            if not address:
                continue
            try:
                ds_url = f"https://api.dexscreener.com/latest/dex/search?q={address}"
                r = requests.get(ds_url, timeout=10)
                if r.status_code != 200:
                    continue
                pairs = r.json().get("pairs", [])
                if not pairs:
                    continue

                filtered = [
                    p for p in pairs
                    if p.get("quoteToken", {}).get("symbol", "").upper() in ("USDT", "USDC", "USD")
                ]
                if not filtered:
                    filtered = pairs

                best = max(filtered, key=lambda x: x.get("liquidity", {}).get("usd", 0))

                out[sym] = {
                    "price": float(best.get("priceUsd", 0)),
                    "change_24h": best.get("priceChange", {}).get("h24"),
                    "change_7d": best.get("priceChange", {}).get("h7"),
                    "market_cap": None,
                    "circulating_supply": None,
                    "total_supply": None,
                    "fdv": None,
                    "ath": None,
                    "atl": None,
                    "liquidity": best.get("liquidity", {}).get("usd"),
                    "volume_24h": best.get("volume", {}).get("h24"),
                }
                logger.info(f"[FALLBACK] Used DexScreener for {sym}")
            except Exception as e:
                logger.error(f"[ERROR] DexScreener fallback failed for {sym}: {e}")

    _MARKETS_CACHE["data"] = out
    _MARKETS_CACHE["ts"] = time.time()
    return {t["symbol"].upper(): out.get(t["symbol"].upper()) for t in tokens}
