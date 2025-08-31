import os
import requests
import math
from decimal import Decimal, DivisionByZero, getcontext
from fastapi import APIRouter
from app.strategies.risk import set_stop_loss, calculate_position_size
from app.config.tokens import TOKENS

getcontext().prec = 28
router = APIRouter()

CG_BASE_URL = os.getenv("COINGECKO_BASE_URL", "https://pro-api.coingecko.com/api/v3")
CG_KEY = os.getenv("COINGECKO_API_KEY")


def fetch_batch_market_data():
    ids = [meta["cg_id"] for _, meta in TOKENS.items() if meta.get("cg_id") and meta["cg_id"] != "null"]
    if not ids:
        return {}

    url = f"{CG_BASE_URL}/simple/price"
    params = {
        "ids": ",".join(ids),
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true",
        "include_last_updated_at": "true",
    }

    headers = {"accept": "application/json"}
    if CG_KEY:
        headers["x-cg-pro-api-key"] = CG_KEY

    try:
        res = requests.get(url, params=params, headers=headers, timeout=30)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"[ERROR] Batch fetch failed: {e}")
        return {}


def fetch_price_history(cg_id: str, days: int = 30):
    url = f"{CG_BASE_URL}/coins/{cg_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    headers = {"accept": "application/json"}
    if CG_KEY:
        headers["x-cg-pro-api-key"] = CG_KEY

    try:
        r = requests.get(url, params=params, headers=headers, timeout=30)
        r.raise_for_status()
        prices = [p[1] for p in r.json().get("prices", [])]
        return prices
    except Exception as e:
        print(f"[ERROR] fetch_price_history failed for {cg_id}: {e}")
        return []


def calc_risk_metrics(prices: list[float]) -> dict:
    if not prices or len(prices) < 2:
        return {"risk_score": 0, "sharpe_ratio": 0, "max_drawdown": 0}

    returns = [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]

    avg_return = sum(returns) / len(returns)
    std_dev = (sum((r - avg_return) ** 2 for r in returns) / len(returns)) ** 0.5
    sharpe = (avg_return / std_dev * math.sqrt(252)) if std_dev > 0 else 0

    peak, max_dd = prices[0], 0
    for p in prices:
        if p > peak:
            peak = p
        dd = (peak - p) / peak
        max_dd = max(max_dd, dd)

    risk_score = min(1, max_dd * 2)

    return {
        "risk_score": float(risk_score),
        "sharpe_ratio": float(sharpe),
        "max_drawdown": float(max_dd),
    }

@router.get("/risk_management")
def get_risk_data_as_json():
    total_usd = Decimal("10000")   
    risk_pct = Decimal("2")        
    min_price = Decimal("0.01")

    market_data = fetch_batch_market_data()
    tokens = []

    for sym, meta in TOKENS.items():
        cg_id = meta.get("cg_id")
        if not cg_id or cg_id == "null":
            continue

        md = market_data.get(cg_id, {})
        price = md.get("usd")
        if price is None or price < float(min_price):
            continue

        # Stop-loss & position size
        entry = Decimal(str(price))
        stop = set_stop_loss(entry, risk_pct)
        try:
            size = calculate_position_size(total_usd, risk_pct, stop, entry)
        except DivisionByZero:
            continue

        prices = fetch_price_history(cg_id, days=30)
        metrics = calc_risk_metrics(prices)

        tokens.append({
            "id": sym.lower(),
            "symbol": sym.upper(),
            "name": sym.upper(),
            "current_price": float(entry),
            "stop_loss": float(stop),
            "position_size": float(size),
            "risk_percentage": float(risk_pct),
            "change_24h": md.get("usd_24h_change", 0.0),
            "volume_24h": md.get("usd_24h_vol", 0.0),
            "market_cap": md.get("usd_market_cap", 0.0),
            "risk_score": metrics["risk_score"],
            "sharpe_ratio": metrics["sharpe_ratio"],
            "max_drawdown": metrics["max_drawdown"],
            "status": "active" if metrics["risk_score"] < 0.7 else "high_risk"
        })

    return {"risk_data": tokens}
