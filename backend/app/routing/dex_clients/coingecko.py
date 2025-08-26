import os, time, requests
from decimal import Decimal
from typing import Tuple, Dict

from app.routing.dex_clients.base import DexClient

_CG_HEADERS = {"accept": "application/json"}
_api_key = os.getenv("COINGECKO_API_KEY")
if _api_key:
    _CG_HEADERS["x-cg-pro-api-key"] = _api_key

_CG_CACHE = {"ts": 0.0, "data": None}
_CG_TTL = 300 

def fetch_top_100_tokens() -> list:
    now = time.time()
    if _CG_CACHE["data"] and now - _CG_CACHE["ts"] < _CG_TTL:
        return _CG_CACHE["data"]

    base_url = os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")
    url = f"{base_url}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False,
    }

    for i in range(3):
        r = requests.get(url, params=params, headers=_CG_HEADERS, timeout=10)
        if r.status_code != 429:
            r.raise_for_status()
            data = r.json()
            _CG_CACHE.update({"ts": now, "data": data})
            return data
        time.sleep(1.5 * (i + 1)) 

    r.raise_for_status()


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
            self.prices = {
                item["symbol"].lower(): Decimal(str(item["current_price"]))
                for item in data
            }

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

def get_usd_per_qlk() -> float:
    qlk_id = os.getenv("QLK_CG_ID", "quantlink")

    base_url = os.getenv("COINGECKO_BASE_URL", "https://api.coingecko.com/api/v3")
    url = f"{base_url}/simple/price"
    params = {"ids": qlk_id, "vs_currencies": "usd"}
    r = requests.get(url, params=params, headers=_CG_HEADERS, timeout=10)
    r.raise_for_status()

    data = r.json()
    return float(data[qlk_id]["usd"])
