import requests
from decimal import Decimal
from typing import Dict, Any, Optional, Tuple, List

from app.strategies.arbitrage_and_twap import TOKEN_INFO

OPENOCEAN_QUOTE_URL = "https://open-api.openocean.finance/v3/eth/quote"

DEX_LABELS: Dict[str, str] = {
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

def _pretty(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    k = name.upper().replace(" ", "_").replace("-", "_")
    return DEX_LABELS.get(k, name)

def _resolve(symbol: str) -> Tuple[str, int]:
    key = symbol.lower()
    if key not in TOKEN_INFO:
        raise ValueError(f"Unsupported token: {symbol}")
    info = TOKEN_INFO[key]
    return info["address"], int(info["decimals"])

def _extract_best_dex_from_oo(data: Dict[str, Any]) -> Optional[str]:
    # 1) protocols
    protos = data.get("protocols")
    if isinstance(protos, list) and protos:
        flat: List[Dict[str, Any]] = []
        for it in protos:
            if isinstance(it, list):
                for sub in it:
                    if isinstance(sub, dict):
                        flat.append(sub)
            elif isinstance(it, dict):
                flat.append(it)
        if flat:
            flat.sort(key=lambda x: (x.get("part") or x.get("percent") or 0), reverse=True)
            cand = flat[0]
            nm = cand.get("name") or cand.get("dex") or cand.get("id")
            p = _pretty(nm)
            if p:
                return p

    # 2) routes / route / pathList / paths / legs
    for key in ("routes", "route", "pathList", "paths", "legs"):
        rv = data.get(key)
        if isinstance(rv, list) and rv:
            first = rv[0]
            if isinstance(first, dict):
                nm = first.get("dex") or first.get("name") or first.get("protocol")
                p = _pretty(nm)
                if p:
                    return p

    # 3) routers: ["UNISWAP_V3", ...]
    routers = data.get("routers")
    if isinstance(routers, list) and routers:
        p = _pretty(str(routers[0]))
        if p:
            return p

    return None

def get_openocean_quote(
    from_id: str,
    to_id: str,
    amount: float,
    protocols: Optional[List[str]] = None,
) -> dict:
    params = {
        "inTokenAddress": from_id,
        "outTokenAddress": to_id,
        "amount": str(int(Decimal(str(amount)) * (Decimal(10) ** 18))),
        "slippage": 1,
    }
    if protocols:
        params["dexes"] = ",".join(protocols)

    resp = requests.get(OPENOCEAN_QUOTE_URL, params=params, timeout=20)
    resp.raise_for_status()
    payload = resp.json() or {}
    data = payload.get("data") or {}

    # outAmount & decimals
    raw_out = int(data.get("outAmount", 0))
    out_token = data.get("outToken") or {}
    try:
        to_dec = int(out_token.get("decimals", 18))
    except Exception:
        to_dec = 18
    expected_out = float(Decimal(raw_out) / (Decimal(10) ** to_dec))

    # dex etiketi
    dex_label = _extract_best_dex_from_oo(data)

    # gas info
    est_gas = None
    gas_price = None
    if isinstance(data.get("estimatedGas"), (int, str)):
        try:
            est_gas = int(data["estimatedGas"])
        except Exception:
            pass
    if isinstance(data.get("gasPrice"), (int, str)):
        try:
            gas_price = int(data["gasPrice"])
        except Exception:
            pass

    return {
        "expectedAmountOut": expected_out,
        "dex": dex_label,
        "protocols": data.get("protocols"),
        "bestRoute": data.get("routes") or data.get("route"),
        "path": [from_id, to_id],
        "estimatedGas": est_gas,
        "gasPrice": gas_price,
        "source": "OpenOcean",
    }

# ----------------------- Backward-compatible Client (shim) -----------------------

class OpenOceanClient:
    name = "OpenOcean"

    def __init__(self):
        _ = TOKEN_INFO

    def get_quote(self, from_symbol: str, to_symbol: str, amount: Decimal) -> Decimal:
        from_addr, from_dec = _resolve(from_symbol)
        to_addr, to_dec     = _resolve(to_symbol)
        amt_float = float(amount) 
        data = get_openocean_quote(from_addr, to_addr, amt_float, protocols=None)

        return Decimal(str(data.get("expectedAmountOut", 0)))

    def swap(self, *args, **kwargs):
        raise NotImplementedError("On-chain swap is not implemented in this backend.")
