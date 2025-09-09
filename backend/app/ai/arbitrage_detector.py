import os
import time
import requests
from datetime import datetime
from typing import Union
from app.aggregator.price_feed import calculate_slippage
from app.config.constants import QLK_SUPPORTED_DEX, DEX_CHAINS
from app.config.constants import GAS_COSTS_USD, BRIDGE_COSTS_USD
from app.aggregator.price_feed import get_usd_per_qlk


BRIDGE_COSTS = {
    ("ethereum", "bsc"): {"fee_pct": 0.1, "time_minutes": 3},
    ("ethereum", "polygon"): {"fee_pct": 0.07, "time_minutes": 5},
    ("bsc", "polygon"): {"fee_pct": 0.06, "time_minutes": 4},
    ("polygon", "ethereum"): {"fee_pct": 0.08, "time_minutes": 6},
    ("bsc", "ethereum"): {"fee_pct": 0.1, "time_minutes": 3},
}

_CG_CACHE = {"ts": 0.0, "usd_per_qlk": None}
_CG_TTL = 300
DEFAULT_AMOUNT_USD = 10000.0
ALLOW_AGG = os.getenv("QLK_ALLOW_AGGREGATORS", "0") == "1"
DEX_LABELS = {
    "uniswap": "Uniswap",
    "uniswap_v2": "Uniswap V2",
    "uniswap_v3": "Uniswap V3",
    "sushiswap": "SushiSwap",
    "curve": "Curve",
    "balancer": "Balancer",
    "raydium": "Raydium",
    "pancakeswap": "PancakeSwap",
    "osmosis": "Osmosis",
    "pulsex": "PulseX",
    "pumpswap": "PumpSwap",
    "swappi": "Swappi",
}

def get_usd_per_qlk() -> Union[float, None]:
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

def route_supports_qlk(dex: str) -> bool:
    d = (dex or "").lower()
    if d in QLK_SUPPORTED_DEX:
        return True
    if ALLOW_AGG and d in {"1inch", "openocean"}:
        return True
    return False


def _get_gas_cost_usd(chain: str, gas_costs: dict, speed: str = "fast") -> float:
    chain = (chain or "").lower()
    if chain in gas_costs and isinstance(gas_costs[chain], dict):
        return float(gas_costs[chain].get(speed, 1.0))
    return 1.0


def detect_arbitrage(token_data: dict, gas_costs: dict):
    opportunities = []

    dex_map = {
        "uniswap": "Uniswap",
        "uniswap_v2": "Uniswap V2",
        "uniswap_v3": "Uniswap V3",
        "sushiswap": "SushiSwap",
        "curve": "Curve",
        "balancer": "Balancer",
        "raydium": "Raydium",
        "pancakeswap": "PancakeSwap",
        "osmosis": "Osmosis",
        "pulsex": "PulseX",
        "pumpswap": "PumpSwap",
        "swappi": "Swappi",
    }

    usd_per_qlk = get_usd_per_qlk() or 0.05

    DEFAULT_AMOUNT_USD = 10000.0

    for sym, entries in token_data.items():
        if len(entries) < 2:
            continue

        for buy in entries:
            for sell in entries:
                if buy == sell:
                    continue

                buy_price = buy.get("price")
                sell_price = sell.get("price")

                if not buy_price or not sell_price:
                    continue

                spread_pct = (sell_price - buy_price) / buy_price

                if spread_pct <= 0 or spread_pct > 2:
                    continue

                # Gas cost hesapla
                gas_cost_buy = gas_costs.get(buy.get("chain"), {}).get("standard", 1.0)
                gas_cost_sell = gas_costs.get(sell.get("chain"), {}).get("standard", 1.0)
                gas_cost_usd = gas_cost_buy + gas_cost_sell

                bridge_cost_usd = 0.0

                amount_usd = DEFAULT_AMOUNT_USD
                gross_profit = spread_pct * amount_usd
                net_profit = gross_profit - (gas_cost_usd + bridge_cost_usd)

                if net_profit <= 0:
                    continue

                net_profit_qlk = net_profit / usd_per_qlk if usd_per_qlk > 0 else 0

                buy_dex = dex_map.get((buy.get("dex") or "").lower(), "Other DEX")
                sell_dex = dex_map.get((sell.get("dex") or "").lower(), "Other DEX")

                opportunities.append({
                    "symbol": sym,
                    "buy_from": DEX_LABELS.get((buy.get("dex") or "").lower(), buy.get("dex") or "Unknown DEX"),
                    "sell_to": DEX_LABELS.get((sell.get("dex") or "").lower(), sell.get("dex") or "Unknown DEX"),
                    "buy_price": buy_price,
                    "sell_price": sell_price,
                    "spread_pct": round(spread_pct * 100, 4),
                    "gross_profit_usd": round(gross_profit, 4),
                    "net_profit_usd": round(net_profit, 4),
                    "net_profit_qlk": round(net_profit_qlk, 4),
                    "gas_cost_usd": round(gas_cost_usd, 4),
                    "bridge_cost_usd": round(bridge_cost_usd, 4),
                    "timestamp": buy.get("timestamp") or sell.get("timestamp"),
                    "volume": min(buy.get("volume", 0), sell.get("volume", 0)),
                })

    return {
        "opportunities": opportunities
    }
