import os
import requests
from decimal import Decimal
from typing import Dict, Any, Optional, Tuple, List

from app.config.tokens import TOKENS, get_token

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
    k = str(name).upper().replace(" ", "_").replace("-", "_")
    return DEX_LABELS.get(k, name)

def _rpc_get_decimals(address: str) -> Optional[int]:
    ETH_RPC_URL = os.getenv("ETH_RPC_URL") or os.getenv("ETHEREUM_RPC_URL")
    if not ETH_RPC_URL:
        return None
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [
                { "to": address, "data": "0x313ce567" },
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

def _resolve(symbol: str) -> Tuple[str, int]:
    sym = (symbol or "").upper()
    rec = TOKENS.get(sym)

    if rec and rec.get("address"):
        return rec["address"], int(rec.get("decimals", 18))

    if sym == "QLK":
        from app.routing.dex_clients.coingecko import fetch_token_on_ethereum_by_cgid
        cg_id = os.getenv("QLK_CG_ID")  # örn. "quantlink"
        cg_tok = fetch_token_on_ethereum_by_cgid(cg_id) if cg_id else None
        if cg_tok and cg_tok.get("address"):
            TOKENS["QLK"] = {"symbol": "QLK", "chain": "ethereum",
                             "address": cg_tok["address"], "decimals": int(cg_tok["decimals"])}
            return cg_tok["address"], int(cg_tok["decimals"])
        addr = os.getenv("QLK_ADDRESS_ETHEREUM")
        if not addr:
            raise ValueError("QLK contract not found via CoinGecko and QLK_ADDRESS_ETHEREUM is not set.")
        dec = int(os.getenv("QLK_DECIMALS") or 18)
        TOKENS["QLK"] = {"symbol": "QLK", "chain": "ethereum", "address": addr, "decimals": dec}
        return addr, dec

    raise ValueError(f"Unsupported token symbol (not in TOKENS and no CG/env path): {symbol}")

def _amount_to_base_units(amount: float, decimals: int) -> str:
    quant = Decimal(str(amount)) * (Decimal(10) ** int(decimals))
    if quant.is_nan() or quant < 0:
        return "0"
    return str(int(quant))

def _extract_best_dex_from_oo(data: Dict[str, Any]) -> Optional[str]:
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

    for key in ("routes", "route", "pathList", "paths", "legs"):
        rv = data.get(key)
        if isinstance(rv, list) and rv:
            first = rv[0]
            if isinstance(first, dict):
                nm = first.get("dex") or first.get("name") or first.get("protocol")
                p = _pretty(nm)
                if p:
                    return p

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
    from_decimals: int,
    protocols: Optional[List[str]] = None,
) -> dict:
    params = {
        "inTokenAddress": from_id,
        "outTokenAddress": to_id,
        "amount": _amount_to_base_units(amount, from_decimals),
        "slippage": 1,
    }
    if protocols:
        params["dexes"] = ",".join(protocols)

    resp = requests.get(OPENOCEAN_QUOTE_URL, params=params, timeout=20)
    resp.raise_for_status()
    payload = resp.json() or {}
    data = payload.get("data") or {}

    raw_out = 0
    try:
        raw_out = int(data.get("outAmount", 0))
    except Exception:
        raw_out = 0

    out_token = data.get("outToken") or {}
    try:
        to_dec = int(out_token.get("decimals", 18))
    except Exception:
        to_dec = 18

    expected_out = float(Decimal(raw_out) / (Decimal(10) ** to_dec)) if raw_out else 0.0

    dex_label = _extract_best_dex_from_oo(data)

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
        pass 

    def get_quote(self, from_symbol: str, to_symbol: str, amount: Decimal) -> Decimal:
        # normalize
        from_symbol = from_symbol.upper()
        to_symbol = to_symbol.upper()

        from_addr, from_dec = _resolve(from_symbol)
        to_addr, _to_dec = _resolve(to_symbol)
        amt_float = float(amount)
        data = get_openocean_quote(
            from_addr,
            to_addr,
            amt_float,
            from_decimals=from_dec,
            protocols=None
        )
        return Decimal(str(data.get("expectedAmountOut", 0)))
