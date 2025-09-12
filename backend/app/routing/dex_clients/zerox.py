import requests
from decimal import Decimal
from typing import Tuple, Optional
from app.config.tokens import TOKENS

from app.routing.dex_clients.base import DexClient

ZEROX_PRICE_URL = "https://api.0x.org/swap/v1/price"
ZEROX_SWAP_URL  = "https://api.0x.org/swap/v1/quote"

class ZeroXClient(DexClient):
    name = "0x"

    def __init__(self, chain: str = "ethereum"):
        self.chain = chain

    def _resolve(self, symbol: str) -> Tuple[str, int]:
        sym = symbol.upper()
        if sym not in TOKENS:
            raise KeyError(f"Token {sym} not found in TOKENS")
        info = TOKENS[sym]
        return info["address"], info["decimals"]

    def get_quote(self, from_symbol: str, to_symbol: str, amount: Decimal) -> Optional[Decimal]:
        from_symbol = from_symbol.upper()
        to_symbol   = to_symbol.upper()

        try:
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

            if resp.status_code == 404:
                return None

            resp.raise_for_status()
            data = resp.json()
            buy_int = int(data.get("buyAmount", 0))
            if buy_int == 0:
                return None
            return Decimal(buy_int) / (Decimal(10) ** to_decimals)

        except Exception as e:
            print(f"[ZeroXClient] get_quote error: {e}")
            return None

    def swap(self, from_symbol: str, to_symbol: str, amount: Decimal) -> str:
        from_symbol = from_symbol.upper()
        to_symbol   = to_symbol.upper()

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

        if resp.status_code == 404:
            raise RuntimeError(f"No swap route found on 0x for {from_symbol}->{to_symbol}")

        resp.raise_for_status()
        data = resp.json()
        return f"{data['to']}?data={data['data']}"
