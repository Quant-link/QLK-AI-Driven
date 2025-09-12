import os
import math
import requests
import logging
from decimal import Decimal, DivisionByZero
from typing import Dict, List, Any, Optional
from fastapi import APIRouter
import json

TOKENS_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "tokens.json")
with open(TOKENS_PATH, "r") as f:
    raw_tokens = json.load(f)

if isinstance(raw_tokens, list):
    TOKENS: Dict[str, dict] = {t.get("symbol", "").upper(): t for t in raw_tokens if t.get("symbol")}
else:
    TOKENS: Dict[str, dict] = raw_tokens

logging.info(f"[TOKENS] ✅ {len(TOKENS)} token yüklendi. Örnek: {list(TOKENS.keys())[:5]}")

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
            logging.warning(f"[WARN] CG {cg_id} {res.status_code}")
            return None
        data = res.json()
        market = data.get("market_data", {}) or {}
        return {
            "price": (market.get("current_price") or {}).get("usd"),
            "high_24h": (market.get("high_24h") or {}).get("usd"),
            "low_24h": (market.get("low_24h") or {}).get("usd"),
        }
    except Exception as e:
        logging.error(f"[ERROR] CG fetch {cg_id}: {e}")
        return None


def set_stop_loss(entry_price: Decimal, risk_pct: Decimal) -> Decimal:
    return entry_price * (Decimal(1) - risk_pct / Decimal(100))


def calculate_position_size(total_usd: Decimal, risk_pct: Decimal, stop: Decimal, entry: Decimal) -> Decimal:
    risk_amount = total_usd * (risk_pct / Decimal(100))
    if entry <= stop:
        raise DivisionByZero("Stop loss >= entry price")
    return risk_amount / (entry - stop)


def fetch_price_history(cg_id: str, days: int = 30) -> List[Decimal]:
    try:
        url = f"{CG_BASE_URL}/coins/{cg_id}/market_chart"
        params = {"vs_currency": "usd", "days": days}
        res = requests.get(url, headers=CG_HEADERS, params=params, timeout=15)
        if res.status_code != 200:
            logging.warning(f"[WARN] CG history {cg_id} {res.status_code}")
            return []
        prices = res.json().get("prices", [])
        return [Decimal(str(p[1])) for p in prices if len(p) == 2]
    except Exception as e:
        logging.error(f"[ERROR] history {cg_id}: {e}")
        return []


def calculate_max_drawdown(prices: List[Decimal]) -> float:
    if not prices:
        return 0.0
    peak = prices[0]
    max_dd = Decimal(0)
    for p in prices:
        if p > peak:
            peak = p
        dd = (peak - p) / peak if peak > 0 else Decimal(0)
        if dd > max_dd:
            max_dd = dd
    return float(max_dd * 100)


def calculate_sharpe_ratio(prices: List[Decimal]) -> float:
    if len(prices) < 2:
        return 0.0
    returns = [(prices[i] / prices[i - 1] - 1) for i in range(1, len(prices))]
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    std_dev = math.sqrt(float(variance)) if variance > 0 else 0
    if std_dev == 0:
        return 0.0
    return float(mean_return) / std_dev * math.sqrt(365)


def calculate_risk_score(max_dd: float, sharpe: float) -> float:
    score = max(0.0, min(1.0, (1 / (1 + max_dd / 100)) * (1 + sharpe / 10)))
    return round(score, 2)


@router.get("/risk_management")
def get_risk_management() -> Dict[str, List[Dict[str, Any]]]:
    results: List[Dict[str, Any]] = []
    total_usd = Decimal("10000")
    risk_pct = Decimal("2")

    for sym, meta in TOKENS.items():
        try:
            cg_id = meta.get("cg_id") or meta.get("coingecko_id")
            if not cg_id:
                logging.warning(f"[WARN] {sym}: coingecko_id eksik, atlanıyor")
                continue

            cg_data = fetch_from_coingecko(cg_id)
            if not cg_data or not cg_data.get("price"):
                logging.warning(f"[WARN] {sym}: fiyat bulunamadı")
                continue

            entry = Decimal(str(cg_data["price"]))
            stop = set_stop_loss(entry, risk_pct)

            try:
                size = calculate_position_size(total_usd, risk_pct, stop, entry)
            except DivisionByZero:
                logging.error(f"[ERROR] {sym}: stop loss >= entry price, atlanıyor")
                continue

            prices = fetch_price_history(cg_id, days=30)
            max_dd = calculate_max_drawdown(prices)
            sharpe = calculate_sharpe_ratio(prices)
            risk_score = calculate_risk_score(max_dd, sharpe)

            results.append({
                "id": sym.lower(),
                "symbol": sym.upper(),
                "current_price": float(entry),
                "stop_loss": float(stop),
                "position_size": float(size),
                "risk_percentage": float(risk_pct),
                "volatility": 2.0,
                "risk_score": risk_score,
                "max_drawdown": max_dd,
                "sharpe_ratio": sharpe,
                "status": "active",
            })

        except Exception as e:
            logging.error(f"[ERROR] Risk hesaplama hatası ({sym}): {e}")

    logging.info(f"[DEBUG] risk_data oluşturuldu: {len(results)} token")
    return {"risk_data": results}
