import requests
from decimal import Decimal
from typing import Tuple

from app.routing.dex_clients.base import DexClient
from app.strategies.arbitrage_and_twap import TOKEN_INFO

ZEROX_PRICE_URL = "https://api.0x.org/swap/v1/price"
ZEROX_SWAP_URL  = "https://api.0x.org/swap/v1/quote"

class ZeroXClient(DexClient):
    name = "0x"

    def __init__(self, chain: str = "ethereum"):
        self.chain = chain

    def _resolve(self, symbol: str) -> Tuple[str, int]:
        info = TOKEN_INFO[symbol.lower()]
        return info["address"], info["decimals"]

    def get_quote(self, from_symbol: str, to_symbol: str, amount: Decimal) -> Decimal:
        from_addr, from_decimals = self._resolve(from_symbol)
        to_addr, to_decimals     = self._resolve(to_symbol)
        sell_amount = int(amount * (Decimal(10) ** from_decimals))

        resp = requests.get(
            ZEROX_PRICE_URL,
            params={
                "sellToken":  from_addr,
                "buyToken":   to_addr,
                "sellAmount": sell_amount
            },
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        buy_int = int(data.get("buyAmount", 0))  # 18-decimal raw integer
        return Decimal(buy_int) / (Decimal(10) ** to_decimals)

    def swap(self, from_symbol: str, to_symbol: str, amount: Decimal) -> str:
        from_addr, from_decimals = self._resolve(from_symbol)
        to_addr, _               = self._resolve(to_symbol)
        sell_amount = int(amount * (Decimal(10) ** from_decimals))

        resp = requests.get(
            ZEROX_SWAP_URL,
            params={
                "sellToken":  from_addr,
                "buyToken":   to_addr,
                "sellAmount": sell_amount
            },
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        return f"{data['to']}?data={data['data']}"
