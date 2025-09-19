import time
from typing import Optional
from app.utils.math_utils import calculate_slippage
from app.config.constants import QLK_SUPPORTED_DEX
from app.aggregator.price_feed import get_usd_per_qlk

_CG_CACHE = {"ts": 0.0, "usd_per_qlk": None}
_CG_TTL = 300

DEX_LABELS = {
    "uniswap": "Uniswap",
    "uniswap_v2": "Uniswap V2",
    "uniswap_v3": "Uniswap V3",
    "sushiswap": "SushiSwap",
}

def get_usd_per_qlk_cached() -> Optional[float]:
    now = time.time()
    if _CG_CACHE["usd_per_qlk"] and now - _CG_CACHE["ts"] < _CG_TTL:
        return _CG_CACHE["usd_per_qlk"]

    price = get_usd_per_qlk()
    if price:
        _CG_CACHE.update({"ts": now, "usd_per_qlk": price})
    return price


def route_supports_qlk(dex: str) -> bool:
    return (dex or "").lower() in QLK_SUPPORTED_DEX


def _get_gas_cost_usd(chain: str, gas_costs: dict, speed: str = "fast") -> Optional[float]:
    if chain in gas_costs and isinstance(gas_costs[chain], dict):
        return float(gas_costs[chain].get(speed))
    return None


def detect_arbitrage(token_data: dict, gas_costs: dict, amount_usd: float = 10000.0):
    opportunities = []
    usd_per_qlk = get_usd_per_qlk_cached()
    if not usd_per_qlk:
        return {"opportunities": []}

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

                gas_buy = _get_gas_cost_usd(buy.get("chain"), gas_costs)
                gas_sell = _get_gas_cost_usd(sell.get("chain"), gas_costs)
                if gas_buy is None or gas_sell is None:
                    continue

                gas_cost_usd = gas_buy + gas_sell
                gross_profit = spread_pct * amount_usd
                net_profit = gross_profit - gas_cost_usd
                if net_profit <= 0:
                    continue

                net_profit_qlk = net_profit / usd_per_qlk
                opportunities.append({
                    "symbol": sym,
                    "buy_from": DEX_LABELS.get((buy.get("dex") or "").lower(), buy.get("dex")),
                    "sell_to": DEX_LABELS.get((sell.get("dex") or "").lower(), sell.get("dex")),
                    "buy_price": buy_price,
                    "sell_price": sell_price,
                    "spread_pct": round(spread_pct * 100, 4),
                    "gross_profit_usd": round(gross_profit, 4),
                    "net_profit_usd": round(net_profit, 4),
                    "net_profit_qlk": round(net_profit_qlk, 4),
                    "gas_cost_usd": round(gas_cost_usd, 4),
                    "timestamp": buy.get("timestamp") or sell.get("timestamp"),
                    "volume": min(buy.get("volume", 0), sell.get("volume", 0)),
                })

    return {"opportunities": opportunities}
