from app.routing.dex_clients.kyber import get_kyber_route
from app.routing.dex_clients.oneinch import get_oneinch_route
from app.routing.dex_clients.openocean import get_openocean_quote  # fonksiyon adı doğru kullanıldı
from fastapi import APIRouter
from app.strategies.arbitrage_and_twap import fetch_all_usd_prices, TOKEN_INFO
import random
from decimal import Decimal

def get_best_route(from_token: str, to_token: str, amount: float):
    routes = []

    try:
        oneinch = get_oneinch_route(from_token, to_token, amount)
        if oneinch:
            routes.append({"source": "1inch", **oneinch})
    except Exception as e:
        print(f"[1inch Error] {e}")

    try:
        kyber = get_kyber_route(from_token, to_token, amount)
        if kyber:
            routes.append({"source": "kyber", **kyber})
    except Exception as e:
        print(f"[Kyber Error] {e}")

    try:
        openocean = get_openocean_quote(from_token, to_token, amount)  # doğru fonksiyon çağrısı
        if openocean:
            routes.append({"source": "OpenOcean", **openocean})
    except Exception as e:
        print(f"[OpenOcean Error] {e}")

    if not routes:
        return None

    return max(routes, key=lambda r: r["expectedAmountOut"])

# API Router for Routes
router = APIRouter()

@router.get("/api/routes")
def get_routes_data():
    """
    Optimal routes verilerini döndürür - Routes sayfasındaki tablo için
    """
    try:
        usd_prices = fetch_all_usd_prices()
        routes_data = []

        # Popüler trading pair'ları için route verileri oluştur
        popular_pairs = [
            ("eth", "usdt"), ("btc", "usdt"), ("link", "usdt"),
            ("uni", "usdt"), ("aave", "usdt"), ("eth", "usdc"),
            ("btc", "usdc"), ("dai", "usdt")
        ]

        for from_token, to_token in popular_pairs:
            if from_token in usd_prices and to_token in usd_prices:
                amount = random.uniform(100, 10000)

                # Mock route data - gerçek projede get_best_route fonksiyonunu kullanabilirsiniz
                dexes = ["Uniswap V3", "1inch", "OpenOcean", "Kyber", "SushiSwap", "Curve"]
                best_dex = random.choice(dexes)

                from_price = float(usd_prices[from_token])
                to_price = float(usd_prices[to_token])

                expected_output = (amount / from_price) * to_price
                slippage = random.uniform(0.1, 2.0)
                gas_cost = random.uniform(5, 50)

                # Route efficiency hesaplama
                efficiency = random.uniform(85, 99)

                routes_data.append({
                    "id": len(routes_data) + 1,
                    "from_token": from_token.upper(),
                    "to_token": to_token.upper(),
                    "amount": round(amount, 2),
                    "best_dex": best_dex,
                    "expected_output": round(expected_output, 6),
                    "slippage": round(slippage, 2),
                    "gas_cost_usd": round(gas_cost, 2),
                    "efficiency": round(efficiency, 1),
                    "route_hops": random.randint(1, 3),
                    "execution_time": random.uniform(2, 15),
                    "price_impact": round(slippage * 0.8, 2)
                })

        return {"routes": routes_data}

    except Exception as e:
        print(f"[ERROR] Routes data fetch failed: {e}")
        return {"routes": []}

@router.get("/api/route_details/{from_token}/{to_token}")
def get_route_details(from_token: str, to_token: str, amount: float = 1000):
    """
    Belirli bir pair için detaylı route bilgisi döndürür
    """
    try:
        # Gerçek route hesaplama
        best_route = get_best_route(from_token, to_token, amount)

        if best_route:
            return {
                "from_token": from_token.upper(),
                "to_token": to_token.upper(),
                "amount": amount,
                "best_route": best_route
            }
        else:
            return {"error": "No route found"}

    except Exception as e:
        print(f"[ERROR] Route details fetch failed: {e}")
        return {"error": "Failed to fetch route details"}
