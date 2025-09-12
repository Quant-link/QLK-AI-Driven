import requests
import time
import logging
from decimal import Decimal
from typing import Tuple, Optional

from app.routing.dex_clients.base import DexClient
from app.config.tokens import TOKENS

chain_mapping = {
    "ethereum": "ethereum",
    "bsc": "bsc",
    "polygon": "polygon",
    "arbitrum": "arbitrum",
    "base": "base",
    "avalanche": "avalanche",
    "solana": "solana",
    "aptos": "aptos"
}

DEXSCREENER_API = "https://api.dexscreener.com/latest/dex/tokens"

class DexScreenerClient(DexClient):
    name = "DexScreener"

    def __init__(self, chain: str = "ethereum"):
        self.chain = chain

    def _resolve(self, symbol: str) -> Optional[str]:
        sym = symbol.upper()
        info = TOKENS.get(sym)
        if not info:
            return None
        return info["address"]

    def get_quote(self, from_symbol: str, to_symbol: str, amount: Decimal) -> Optional[Decimal]:
        try:
            from_addr = self._resolve(from_symbol)
            to_addr   = self._resolve(to_symbol)

            if not from_addr or not to_addr:
                return None

            url = f"{DEXSCREENER_API}/{from_addr}"
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            pairs = data.get("pairs", [])
            if not pairs:
                return None

            best_pair = max(pairs, key=lambda p: float(p.get("liquidity", {}).get("usd", 0)))

            price_usd = Decimal(str(best_pair["priceUsd"]))
            if from_symbol.upper() == "USDT":
                return amount / price_usd
            else:
                return amount * price_usd

        except Exception as e:
            logging.warning(f"[DexScreener] Quote error {from_symbol}->{to_symbol}: {e}")
            time.sleep(0.5)
            return None

    def swap(self, from_symbol: str, to_symbol: str, amount: Decimal) -> str:
        return f"Simulated swap {amount} {from_symbol}->{to_symbol} via DexScreener"
