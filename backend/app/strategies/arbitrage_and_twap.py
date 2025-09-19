import json
import time
import logging
import math
from decimal import Decimal
import requests
from typing import Union, Tuple
from fastapi import APIRouter
from app.config.tokens import TOKENS
from app.aggregator.price_feed import fetch_token_data_extended, fetch_gas_costs
from app.ai.arbitrage_detector import detect_arbitrage
from app.utils.math_utils import calculate_slippage

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("output.log", mode="w", encoding="utf-8"),
    ],
)


def fetch_all_usd_prices() -> dict:
    import os
    api_key = os.getenv("COINGECKO_API_KEY")
    base = os.getenv("COINGECKO_BASE_URL", "https://pro-api.coingecko.com/api/v3")
    qlk_id = os.getenv("QLK_CG_ID", "quantlink")

    headers = {"accept": "application/json"}
    if api_key:
        headers["x-cg-pro-api-key"] = api_key

    ids = ["ethereum", "tether", "usd-coin", "dai",
           "bitcoin", "chainlink", "uniswap", "aave", qlk_id]

    url = f"{base}/simple/price"
    params = {"ids": ",".join(ids), "vs_currencies": "usd"}

    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json() or {}
        prices = {
            "eth": Decimal(str(data.get("ethereum", {}).get("usd") or "0")),
            "usdt": Decimal(str(data.get("tether", {}).get("usd") or "0")),
            "usdc": Decimal(str(data.get("usd-coin", {}).get("usd") or "0")),
            "dai": Decimal(str(data.get("dai", {}).get("usd") or "0")),
            "btc": Decimal(str(data.get("bitcoin", {}).get("usd") or "0")),
            "link": Decimal(str(data.get("chainlink", {}).get("usd") or "0")),
            "uni": Decimal(str(data.get("uniswap", {}).get("usd") or "0")),
            "aave": Decimal(str(data.get("aave", {}).get("usd") or "0")),
            "qlk": Decimal(str(data.get(qlk_id, {}).get("usd") or "0")),
        }
        return prices
    except Exception as e:
        logging.error(f"[CoinGecko Error] {e}")
        return {}

def fetch_price_from_uniswap_sushi(from_symbol: str,
                                   to_symbol: str,
                                   amount: Decimal):
    try:
        base_address = TOKENS[from_symbol.upper()]["address"]
        url = f"https://api.dexscreener.com/latest/dex/tokens/{base_address}"

        max_retries = 3
        backoff = 3
        resp = None

        for attempt in range(max_retries):
            try:
                resp = requests.get(url, timeout=10)
                if resp.status_code == 429:
                    logging.warning(f"[UNISWAP/SUSHI] 429 Too Many Requests "
                                    f"(attempt {attempt+1}/{max_retries}), {backoff}s expected...")
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                resp.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                logging.error(f"[UNISWAP/SUSHI] Request error ({attempt+1}/{max_retries}): {e}")
                time.sleep(backoff)
                backoff *= 2
        else:
            logging.error(f"[UNISWAP/SUSHI] {from_symbol}->{to_symbol} için {max_retries} failed the attempt.")
            return []

        data = resp.json()
        pairs = data.get("pairs", [])
        if not pairs:
            logging.warning(f"[UNISWAP/SUSHI] No pairs found for {from_symbol}")
            return []

        valid_pairs = [
            p for p in pairs
            if p.get("dexId") in ["uniswap", "uniswap_v3", "sushiswap"]
        ]

        if not valid_pairs:
            logging.warning(f"[UNISWAP/SUSHI] No Uniswap/Sushi pools for {from_symbol}")
            return []

        valid_pairs.sort(key=lambda x: float(x.get("liquidity", {}).get("usd", 0)), reverse=True)

        results = []
        for p in valid_pairs:
            try:
                results.append({
                    "dex": p.get("dexId"),
                    "price": Decimal(str(p.get("priceUsd", "0"))),
                    "liquidity": float(p.get("liquidity", {}).get("usd", 0)),
                    "volume": float(p.get("volume", {}).get("h24", 0)),
                    "pairAddress": p.get("pairAddress")
                })
            except Exception as parse_err:
                logging.error(f"[UNISWAP/SUSHI] Parse error: {parse_err}")
                continue

        logging.debug(f"[UNISWAP/SUSHI] Found {len(results)} pools for {from_symbol}, top 3: "
                      f"{json.dumps(results[:3], indent=2, default=str)}")

        time.sleep(1.0)
        return results

    except Exception as e:
        logging.error(f"[UNISWAP/SUSHI] Price fetch failed for {from_symbol}->{to_symbol}: {e}")
        return []


def best_direct_quote(from_symbol: str,
                      to_symbol: str,
                      amount: Decimal,
                      usd_prices: dict[str, Decimal]) -> Union[Decimal, None]:
    results = fetch_price_from_uniswap_sushi(from_symbol, to_symbol, amount)
    if not results:
        return None
    best_pair = max(results, key=lambda x: x.get("liquidity", 0))
    return best_pair["price"]

def best_single_quote(from_symbol: str,
                      to_symbol: str,
                      amount: Decimal,
                      usd_prices: dict[str, Decimal]) -> Union[Decimal, None]:
    direct = best_direct_quote(from_symbol, to_symbol, amount, usd_prices)
    if direct:
        return direct

    best = None
    for mid in ("WETH", "USDC"):
        a1 = best_direct_quote(from_symbol, mid, amount, usd_prices)
        if not a1:
            continue
        a2 = best_direct_quote(mid, to_symbol, amount, usd_prices)
        if not a2:
            continue
        price = a1 * a2
        if best is None or price > best:
            best = price
    return best

def check_arbitrage_opportunity(from_symbol: str,
                                to_symbol: str,
                                amount: Decimal,
                                usd_prices: dict[str, Decimal],
                                min_profit_pct: Decimal = Decimal("0.01")
) -> Union[Tuple[str, str, Decimal, Decimal], Tuple[None, None, None, None]]:
    prices = fetch_price_from_uniswap_sushi(from_symbol, to_symbol, amount)
    if not prices or len(prices) < 2:
        return None, None, None, None

    lowest = min(prices, key=lambda x: x["price"])
    highest = max(prices, key=lambda x: x["price"])
    if lowest["dex"] == highest["dex"]:
        return None, None, None, None

    profit_pct = ((highest["price"] - lowest["price"]) / lowest["price"]) * Decimal("100")
    usd_price_to = _usd_price_for(to_symbol, usd_prices)
    net_profit_usd = (highest["price"] - lowest["price"]) * usd_price_to

    if profit_pct >= min_profit_pct and net_profit_usd > 0:
        return lowest["dex"], highest["dex"], profit_pct, net_profit_usd
    return None, None, None, None

router = APIRouter()

@router.get("/api/arbitrage")
def get_arbitrage_opportunities_api():
    token_data = {}
    gas_costs = fetch_gas_costs()

    for symbol in TOKENS.keys():
        data = fetch_token_data_extended(symbol)
        if data and len(data) >= 2:
            token_data[symbol] = data

    logging.info(f"🔎 DEBUG token_data keys: {list(token_data.keys())}")
    results = detect_arbitrage(token_data, gas_costs)
    return results

@router.get("/api/qlk/top100")
def qlk_top100_quotes(amount: float = 1.0):
    usd = fetch_all_usd_prices()
    base = Decimal(str(amount))
    rows = scan_qlk_vs_top_tokens(base, usd)
    rows.sort(key=lambda r: (not r["has_liquidity"], -float(r["out"]) if r["has_liquidity"] else 0))
    return {"count": len(rows), "amount_in_qlk": str(base), "results": rows}

def execute_twap(from_symbol: str,
                 to_symbol: str,
                 total_usd: Decimal,
                 usd_prices: dict[str, Decimal],
                 steps: int = 10,
                 delay: int = 2) -> Union[Decimal, None]:
    logging.info(f"🚀 Starting TWAP for {from_symbol} → {to_symbol}")
    token_usd_price = _usd_price_for(from_symbol, usd_prices)
    if token_usd_price is None or token_usd_price <= 0:
        logging.error(f"❌ Cannot TWAP {from_symbol}: no USD price")
        return None

    total_token = total_usd / token_usd_price
    step_token = total_token / steps
    collected: list[Decimal] = []

    for i in range(steps):
        out_amt = best_single_quote(from_symbol, to_symbol, step_token, usd_prices)
        if out_amt is None or out_amt <= 0:
            logging.warning(f"⚠️ TWAP step {i+1} failed: no quote")
            time.sleep(delay)
            continue
        usd_per_to = _usd_price_for(to_symbol, usd_prices)
        if usd_per_to <= 0:
            logging.warning(f"⚠️ TWAP step {i+1}: missing USD price for {to_symbol}")
            time.sleep(delay)
            continue

        price_per_token_usd = (out_amt * usd_per_to) / step_token
        collected.append(price_per_token_usd)
        logging.info(f"🔄 TWAP step {i+1}/{steps}: out={out_amt}, avg_usd_per_{from_symbol}={price_per_token_usd:.6f}")
        time.sleep(delay)

    if not collected:
        logging.error("❌ TWAP failed, no valid steps")
        return None

    return sum(collected) / Decimal(len(collected))

def _norm(sym: str) -> str:
    return (sym or "").strip().upper()

def _token_info(sym: str) -> dict:
    s = _norm(sym)
    t = TOKENS.get(s)
    if not t:
        raise KeyError(f"Token {s} not found in tokens.json")
    return {"address": t["address"], "decimals": int(t["decimals"])}

def _map_eth_to_weth(sym: str) -> str:
    return "WETH" if _norm(sym) == "ETH" else _norm(sym)

def _usd_price_for(symbol: str, usd_prices: dict[str, Decimal]) -> Decimal:
    s = _norm(symbol)
    alias = {
        "WETH": "eth",
        "WEETH": "eth",
        "STETH": "eth",
        "WSTETH": "eth",
        "RETH": "eth",
        "EZETH": "eth",
        "WBETH": "eth",
        "WBTC": "btc",
    }
    key = alias.get(s, s.lower())
    val = usd_prices.get(key)
    return val if isinstance(val, Decimal) else Decimal(str(val or "0"))

def scan_qlk_vs_top_tokens(base_amount_qlk: Decimal,
                           usd_prices: dict[str, Decimal]) -> list[dict]:
    results: list[dict] = []
    for sym in sorted(TOKENS.keys()):
        if sym.upper() == "QLK":
            continue
        out_amt = best_single_quote("QLK", sym, base_amount_qlk, usd_prices)
        results.append({
            "pair": f"QLK->{sym}",
            "in": str(base_amount_qlk),
            "out": str(out_amt or Decimal("0")),
            "has_liquidity": bool(out_amt and out_amt > 0),
        })
    return results
