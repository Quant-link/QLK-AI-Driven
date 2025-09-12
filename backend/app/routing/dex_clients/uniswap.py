import os
import requests
from decimal import Decimal
from typing import Tuple
from app.config.tokens import TOKENS
from app.routing.dex_clients.base import DexClient

UNISWAP_URL = "https://api.uniswap.org/v2/quote"
API_KEY = os.getenv("UNISWAP_API_KEY")

class UniswapClient(DexClient):
    name = "Uniswap"

    def __init__(self, chain: str = "ethereum"):
        self.chain = chain

    def _resolve(self, symbol: str) -> Tuple[str, int]:
        sym = symbol.upper()
        if sym not in TOKENS:
            raise KeyError(f"Token {sym} not found in TOKENS")
        info = TOKENS[sym]
        return info["address"], info["decimals"]

    def get_quote(self, from_symbol: str, to_symbol: str, amount: Decimal) -> Decimal:
        from_addr, from_decimals = self._resolve(from_symbol)
        to_addr, to_decimals = self._resolve(to_symbol)

        sell_amount = int(amount * (Decimal(10) ** from_decimals))

        headers = {"Authorization": f"Bearer {API_KEY}"}
        params = {
            "tokenInAddress": from_addr,
            "tokenInChainId": 1,   
            "tokenOutAddress": to_addr,
            "tokenOutChainId": 1,
            "amount": str(sell_amount),
        }

        resp = requests.get(UNISWAP_URL, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        out_amount = int(data["quote"]["quoteAmount"])
        return Decimal(out_amount) / (Decimal(10) ** to_decimals)

    def swap(self, from_symbol: str, to_symbol: str, amount: Decimal) -> str:
        return f"uniswap-swap({from_symbol}->{to_symbol}, amount={amount})"
