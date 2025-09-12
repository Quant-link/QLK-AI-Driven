from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.tokens import TOKENS
from app.aggregator.price_feed import fetch_token_data_extended, fetch_gas_costs
from app.ai.arbitrage_detector import detect_arbitrage
from app.strategies.arbitrage_and_twap import (
    fetch_all_usd_prices,
    router as arbitrage_router,
)
from app.strategies.risk import set_stop_loss, calculate_position_size 
from app.strategies.dca import router as dca_router, start_dca_all
from app.strategies.market_data import router as market_data_router
from app.routing.route_finder import router as routes_router
from app.strategies.risk import router as risk_management_router

import logging
from decimal import Decimal, DivisionByZero

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(arbitrage_router, prefix="/api")
app.include_router(dca_router, prefix="/api")
app.include_router(market_data_router, prefix="/api")
app.include_router(routes_router, prefix="/api")
app.include_router(risk_management_router, prefix="/api")

@app.get("/api/arbitrage")
def get_arbitrage():
    token_data = {}
    for symbol in TOKENS.keys():
        entries = fetch_token_data_extended(symbol)
        if entries:
            token_data[symbol] = entries

    gas_costs = fetch_gas_costs()
    result = detect_arbitrage(token_data, gas_costs)
    return result

@app.on_event("startup")
def auto_start_dca():
    try:
        start_dca_all(
            from_symbol="USDT",
            to_symbol="qlk",
            total_usd_5=500,
            total_usd_10=500,
            total_usd_15=500,
            delay_seconds=60,
        )
        print("[AUTO] ✅ DCA plans started automatically on startup")
    except Exception as e:
        print("[AUTO] ❌ Failed to start DCA:", e, flush=True)

def main():
    print("\n📊 Risk Overview\n")
    total_usd = Decimal("10000")
    risk_pct = Decimal("2")
    min_price = Decimal("0.01")

    usd_prices = fetch_all_usd_prices()

    print(f"{'SYMBOL':<10} {'ENTRY':>10} {'STOP-LOSS':>12} {'SIZE':>12}")
    print("-" * 46)

    for sym in sorted(TOKENS.keys(), key=str.lower):
        entry = usd_prices.get(sym.lower())

        if entry is None or entry < min_price:
            continue

        stop = set_stop_loss(entry, risk_pct)
        try:
            size = calculate_position_size(total_usd, risk_pct, stop, entry)
        except DivisionByZero:
            continue

        e_str = f"{entry:.4f}"
        s_str = f"{stop:.4f}"
        z_str = f"{size:.4f}"

        print(f"{sym:<10} {e_str:>10} {s_str:>12} {z_str:>12}")


if __name__ == "__main__":
    main()
