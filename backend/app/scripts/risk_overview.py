from decimal import Decimal, DivisionByZero, getcontext
from app.strategies.risk import set_stop_loss, calculate_position_size
from app.strategies.arbitrage_and_twap import fetch_all_usd_prices, TOKEN_INFO

getcontext().prec = 28

def main():
    total_usd = Decimal("10000")
    risk_pct   = Decimal("2")     
    min_price  = Decimal("0.01")   

    usd_prices = fetch_all_usd_prices()

    # Başlık
    print(f"{'SYMBOL':<10} {'ENTRY':>10} {'STOP-LOSS':>12} {'SIZE':>12}")
    print("-" * 46)

    for sym in sorted(TOKEN_INFO.keys(), key=str.lower):
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

# ✅ FastAPI endpoint'i için JSON döndüren fonksiyon
def get_risk_data_as_json():
    total_usd = Decimal("10000")
    risk_pct = Decimal("2")
    min_price = Decimal("0.01")

    usd_prices = fetch_all_usd_prices()
    tokens = []

    for sym in sorted(TOKEN_INFO.keys(), key=str.lower):
        entry = usd_prices.get(sym.lower())
        if entry is None or entry < min_price:
            continue

        stop = set_stop_loss(entry, risk_pct)
        try:
            size = calculate_position_size(total_usd, risk_pct, stop, entry)
        except DivisionByZero:
            continue

        tokens.append({
            "id": sym.lower(),
            "symbol": sym.upper(),
            "name": sym.upper(),
            "price": float(entry),
            "stop_loss": float(stop),
            "position_size": float(size),
            "volatility": 2.0,
            "change24h": 0.0
        })

    return {"tokens": tokens}

if __name__ == "__main__":
    main()
