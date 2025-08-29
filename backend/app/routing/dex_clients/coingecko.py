import os, time, requests
from typing import List, Dict, Optional

_CG_HEADERS = {"accept": "application/json"}
_api_key = os.getenv("COINGECKO_API_KEY")
if _api_key:
    _CG_HEADERS["x-cg-pro-api-key"] = _api_key

CG_BASE_URL = os.getenv("COINGECKO_BASE_URL", "https://pro-api.coingecko.com/api/v3")

_CG_CACHE = {"ts": 0.0, "data": None}
_CG_TTL = int(os.getenv("COINGECKO_TOP100_TTL_SEC", "300")) 

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

def _cg_get(path: str, params: Dict) -> dict:
    r = requests.get(f"{CG_BASE_URL}{path}", headers=_CG_HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def fetch_top_100_tokens() -> List[Dict]:
    now = time.time()
    if _CG_CACHE["data"] and now - _CG_CACHE["ts"] < _CG_TTL:
        return _CG_CACHE["data"]

    markets = _cg_get(
        "/coins/markets",
        {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h"
        }
    )

    out: List[Dict] = []

    for m in markets:
        coin_id = m.get("id")
        symbol = (m.get("symbol") or "").upper()
        if not coin_id:
            continue
        try:
            detail = _cg_get(
                f"/coins/{coin_id}",
                {
                    "localization": "false",
                    "tickers": "false",
                    "market_data": "false",
                    "community_data": "false",
                    "developer_data": "false",
                    "sparkline": "false",
                }
            )
        except Exception:
            continue

        platforms = detail.get("detail_platforms") or detail.get("platforms") or {}
        eth_plat = platforms.get("ethereum") or platforms.get("Ethereum")
        if not eth_plat:
            continue

        address = (eth_plat.get("contract_address") or "").strip()
        if not address:
            continue

        address = _to_checksum(address)

        decimals = eth_plat.get("decimal_place")
        if decimals is None:
            decimals = _rpc_get_decimals(address) or 18

        if len(address) != 42 or not address.startswith("0x"):
            continue

        out.append({
            "symbol": symbol,
            "chain": "ethereum",
            "address": address,
            "decimals": int(decimals)
        })

    must_have = [
        ("ETH",  "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 18), 
        ("USDC", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 6),
        ("USDT", "0xdAC17F958D2ee523a2206206994597C13D831ec7", 6),
        ("DAI",  "0x6B175474E89094C44Da98b954EedeAC495271d0F", 18),
        ("WBTC", "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599", 8),
    ]
    have = {t["symbol"]: t for t in out}
    for sym, addr, dec in must_have:
        if sym not in have:
            out.append({"symbol": sym, "chain": "ethereum", "address": _to_checksum(addr), "decimals": dec})

    seen = set()
    dedup: List[Dict] = []
    for t in out:
        if t["symbol"] in seen:
            continue
        seen.add(t["symbol"])
        dedup.append(t)

    _CG_CACHE["data"] = dedup
    _CG_CACHE["ts"] = time.time()
    return dedup

import os

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
    return {"symbol": symbol or "QLK", "address": address, "decimals": int(decimals)}

def fetch_usd_price_by_cgid(cg_id: str) -> float:
    if not cg_id:
        return 0.0
    data = _cg_get(
        "/simple/price",
        {"ids": cg_id, "vs_currencies": "usd"}
    )
    try:
        return float(data.get(cg_id, {}).get("usd", 0.0))
    except Exception:
        return 0.0
