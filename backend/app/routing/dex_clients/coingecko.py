import requests
from decimal import Decimal
from typing import Tuple, Dict

from app.routing.dex_clients.base import DexClient

def fetch_top_100_tokens() -> list:
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

def get_token_info() -> Dict[str, Dict]:
    from app.strategies.arbitrage_and_twap import TOKEN_INFO
    return TOKEN_INFO

class CoingeckoClient(DexClient):
    name = "Coingecko"
    
    def __init__(self):
        self.prices = None

    def _ensure_prices(self):
        if self.prices is None:
            data = fetch_top_100_tokens()
            # symbol.lower() -> current_price (USD)
            self.prices = { item["symbol"].lower(): Decimal(str(item["current_price"])) for item in data }

    def _resolve(self, symbol: str) -> Tuple[str, int]:
        token_info = get_token_info()
        info = token_info[symbol.lower()]
        return info["address"], info["decimals"]

    def get_quote(self, from_symbol: str, to_symbol: str, amount: Decimal) -> Decimal:
        self._ensure_prices()
        from_sym = from_symbol.lower()
        to_sym   = to_symbol.lower()

        if from_sym not in self.prices or to_sym not in self.prices:
            raise ValueError(f"Coingecko: Unsupported symbol {from_symbol} or {to_symbol}")

        price_from = self.prices[from_sym]   
        price_to   = self.prices[to_sym]     

        usd_value = amount * price_from      
        return usd_value / price_to

    def swap(self, from_symbol: str, to_symbol: str, amount: Decimal) -> str:
        return ""
