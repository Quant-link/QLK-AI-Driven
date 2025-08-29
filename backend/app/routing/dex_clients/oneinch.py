import os
import requests
from decimal import Decimal
from functools import lru_cache
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv
from app.config.tokens import TOKENS
load_dotenv()

CHAIN_ID = int(os.getenv("ONEINCH_CHAIN_ID", "1"))
ONEINCH_API_KEY = os.getenv("ONEINCH_API_KEY", "")
BASE = f"https://api.1inch.dev/swap/v5.2/{CHAIN_ID}"

TOKENS_URL = f"{BASE}/tokens"
QUOTE_URL  = f"{BASE}/quote"
SWAP_URL   = f"{BASE}/swap" 

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {ONEINCH_API_KEY}",
}

# ----------------------------- Helpers -----------------------------

PROTOCOL_LABELS: Dict[str, str] = {
    "UNISWAP": "Uniswap",
    "UNISWAP_V2": "Uniswap V2",
    "UNISWAP_V3": "Uniswap V3",
    "SUSHI": "SushiSwap",
    "SUSHISWAP": "SushiSwap",
    "CURVE": "Curve",
    "BALANCER": "Balancer",
    "RAYDIUM": "Raydium",
    "PANCAKESWAP": "PancakeSwap",
    "OSMOSIS": "Osmosis",
    "PULSEX": "PulseX",
    "PUMPSWAP": "PumpSwap",
    "SWAPPI": "Swappi",
}

ETH_SENTINEL = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

def _pretty_protocol_name(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    key = str(raw).strip().upper().replace(" ", "_").replace("-", "_")
    return PROTOCOL_LABELS.get(key) or PROTOCOL_LABELS.get(key.replace("_EXCHANGE", ""))

def _flatten_protocols(proto_field: Any) -> List[Dict[str, Any]]:
    flat: List[Dict[str, Any]] = []
    if isinstance(proto_field, list):
        for item in proto_field:
            if isinstance(item, list):
                for sub in item:
                    if isinstance(sub, dict):
                        flat.append(sub)
            elif isinstance(item, dict):
                flat.append(item)
    elif isinstance(proto_field, dict):
        flat.append(proto_field)
    return flat

def _pick_best_dex_from_1inch(quote_json: Dict[str, Any]) -> str:
    protos = _flatten_protocols(quote_json.get("protocols"))
    if protos:
        protos_sorted = sorted(
            protos,
            key=lambda x: (x.get("part") or x.get("percent") or 0),
            reverse=True,
        )
        cand = protos_sorted[0]
        name = cand.get("name") or cand.get("id") or cand.get("dex")
        pretty = _pretty_protocol_name(name)
        if pretty:
            return pretty

    route = quote_json.get("route") or quote_json.get("routes")
    if isinstance(route, list) and route:
        first = route[0]
        if isinstance(first, dict):
            name = first.get("name") or first.get("dex") or first.get("protocol")
            pretty = _pretty_protocol_name(name)
            if pretty:
                return pretty

    return "1inch"

@lru_cache(maxsize=1)
def _token_map() -> Dict[str, Dict[str, Any]]:
    if not ONEINCH_API_KEY:
        return {}
    resp = requests.get(TOKENS_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    tokens = resp.json().get("tokens", {}) or {}
    out: Dict[str, Dict[str, Any]] = {}
    for addr, meta in tokens.items():
        if isinstance(addr, str):
            out[addr.lower()] = meta
        if isinstance(meta, dict) and isinstance(meta.get("address"), str):
            out[meta["address"].lower()] = meta
    out[ETH_SENTINEL.lower()] = {"address": ETH_SENTINEL, "decimals": 18, "symbol": "ETH"}
    return out

@lru_cache(maxsize=1)
def _symbol_to_address() -> Dict[str, Tuple[str, int]]:
    m = _token_map()
    res: Dict[str, Tuple[str, int]] = {}
    for addr, meta in m.items():
        sym = (meta.get("symbol") or "").upper()
        try:
            dec = int(meta.get("decimals", 18))
        except Exception:
            dec = 18
        if sym:
            res[sym] = (meta.get("address", addr), dec)
    return res

def _decimals_for_address(address: str, default: int = 18) -> int:
    try:
        meta = _token_map().get(address.lower())
        if meta and "decimals" in meta:
            return int(meta["decimals"])
    except Exception:
        pass
    return default

# ----------------------------- Main -----------------------------
def get_oneinch_route(
    from_id: str,
    to_id: str,
    amount: float,
    protocols: Optional[List[str]] = None,
) -> dict:
    if not ONEINCH_API_KEY:
        raise RuntimeError("ONEINCH_API_KEY missing in environment")

    from_dec = _decimals_for_address(from_id, default=18)
    amount_wei = int(Decimal(str(amount)) * (Decimal(10) ** from_dec))

    params = {
        "src": from_id,
        "dst": to_id,
        "amount": str(amount_wei),
    }
    if protocols:
        params["protocols"] = ",".join(protocols)

    r = requests.get(QUOTE_URL, headers=HEADERS, params=params, timeout=20)
    r.raise_for_status()
    q = r.json() or {}

    # -------- DEBUG --------
    try:
        import json
        print("\n--- 1inch QUOTE RAW RESPONSE ---")
        print(json.dumps(q, indent=2)[:8000])
        print("--- END RESPONSE ---\n")
    except Exception:
        pass

    to_amount_raw = q.get("toAmount") or 0
    try:
        to_amount_raw = int(to_amount_raw)
    except Exception:
        to_amount_raw = 0

    to_dec = 18
    to_token = q.get("toToken") or {}
    try:
        to_dec = int(to_token.get("decimals", 18))
    except Exception:
        pass

    expected_out = float(Decimal(to_amount_raw) / (Decimal(10) ** to_dec))

    best_dex = _pick_best_dex_from_1inch(q)

    gas_est = None
    try:
        if isinstance(q.get("gas"), (int, str)):
            gas_est = int(q["gas"])
    except Exception:
        pass

    gas_price = None

    return {
        "expectedAmountOut": expected_out,
        "dex": best_dex,
        "protocols": q.get("protocols"),
        "bestRoute": q.get("route") or q.get("routes"),
        "path": [from_id, to_id],
        "estimatedGas": gas_est,
        "gasPrice": gas_price,
        "source": "1inch",
    }

# ----------------------------- Client -----------------------------

class OneInchClient:
    name = "1inch"

    def __init__(self):
        if not ONEINCH_API_KEY:
            raise RuntimeError("ONEINCH_API_KEY missing in environment")
        _ = _token_map()
        _ = _symbol_to_address()

    def _resolve_symbol(self, symbol: str) -> Tuple[str, int]:
        sym = symbol.upper()
        if sym not in TOKENS:
            raise KeyError(f"Token {sym} not found in TOKENS")
        info = TOKENS[sym]
        return info["address"], info["decimals"]

    def get_quote(self, from_symbol: str, to_symbol: str, amount: Decimal) -> Decimal:
            from_symbol = from_symbol.upper()
            to_symbol = to_symbol.upper()

            from_addr, from_dec = self._resolve_symbol(from_symbol)
            to_addr, to_dec     = self._resolve_symbol(to_symbol)

            amount_wei = int(Decimal(amount) * (Decimal(10) ** from_dec))
            params = {"src": from_addr, "dst": to_addr, "amount": str(amount_wei)}
            r = requests.get(QUOTE_URL, headers=HEADERS, params=params, timeout=20)
            r.raise_for_status()
            q = r.json() or {}

            to_amount_raw = q.get("toAmount") or 0
            try:
                to_amount_raw = int(to_amount_raw)
            except Exception:
                to_amount_raw = 0

            tdec = int((q.get("toToken") or {}).get("decimals", to_dec))
            return Decimal(to_amount_raw) / (Decimal(10) ** tdec)

    def swap(self, from_symbol: str, to_symbol: str, amount: Decimal) -> str:
        from_symbol = from_symbol.upper()
        to_symbol   = to_symbol.upper()

        from_addr, from_dec = self._resolve_symbol(from_symbol)
        to_addr, _to_dec    = self._resolve_symbol(to_symbol)

        sell_amount = int(Decimal(amount) * (Decimal(10) ** from_dec))

        params = {
            "src": from_addr,
            "dst": to_addr,
            "amount": str(sell_amount),
            "from": os.getenv("SIM_FROM_ADDRESS", ""),  
            "slippage": os.getenv("SLIPPAGE_BPS", "1"),
            "disableEstimate": "true",                 
            "allowPartialFill": "false"               
        }

        r = requests.get(SWAP_URL, headers=HEADERS, params=params, timeout=20)
        r.raise_for_status()
        data = r.json() or {}

        tx = data.get("tx")
        if tx and isinstance(tx, dict):
            return f"{tx.get('to')}?data={tx.get('data')}"
        if "to" in data and "data" in data:
            return f"{data['to']}?data={data['data']}"

        return str(data)
