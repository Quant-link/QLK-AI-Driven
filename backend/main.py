from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.tokens import TOKENS
from app.aggregator.price_feed import fetch_token_data, fetch_gas_costs
from app.ai.arbitrage_detector import detect_arbitrage
from app.strategies.arbitrage_and_twap import (
    fetch_all_usd_prices,
    get_arbitrage_opportunities_api,
    fetch_price_from_1inch,
    fetch_price_from_openocean
)
from app.strategies.risk import set_stop_loss, calculate_position_size

# Import all routers
from app.strategies.arbitrage_and_twap import router as arbitrage_router
from app.strategies.dca import router as dca_router
from app.strategies.risk import router as risk_router
from app.strategies.market_data import router as market_data_router
from app.routing.route_finder import router as routes_router

import logging
from decimal import Decimal, DivisionByZero, getcontext

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(arbitrage_router)
app.include_router(dca_router)
app.include_router(risk_router)
app.include_router(market_data_router)
app.include_router(routes_router)
# Arbitrage endpoint is now handled by the arbitrage router

# Risk data endpoint is now handled by the risk router

def main():
    """
    print("\n🔍 Running Arbitrage Analysis...\n")

    token_data = {}
    usd_prices = fetch_all_usd_prices()
    gas_costs = fetch_gas_costs()

    for symbol in TOKENS:
        data = fetch_token_data_extended(symbol, usd_prices)
        if data and len(data) >= 2:
            token_data[symbol] = data

    print("🧠 Arbitrage Opportunities:")
    results = detect_arbitrage(token_data, gas_costs)
    if not results:
        print("🚫 No arbitrage opportunities found.")
    else:
        print(f"✅ Found {len(results)} opportunities:\n")
        for opp in results:
            print(f"🔁 {opp['symbol']}: Buy from {opp['buy_from']} @ ${opp['buy_price']} → Sell to {opp['sell_to']} @ ${opp['sell_price']}")
            print(f"   Spread: {opp['spread_pct']}% | Net Profit: ${opp['net_profit_usd']}")
            print(f"   Risk: {opp['risk_score']} | Confidence: {opp['confidence']}")
            print(f"   Bridge Cost: ${opp['bridge_cost_usd']} | Gas Cost: ${opp['gas_cost_usd']}")
            print(f"   ETA: {opp['execution_time_sec']} sec\n")
    """
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