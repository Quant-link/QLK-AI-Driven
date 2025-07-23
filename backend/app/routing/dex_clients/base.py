from decimal import Decimal
from typing import Protocol

class DexClient(Protocol):
    name: str

    def get_quote(self, from_symbol: str, to_symbol: str, amount: Decimal) -> Decimal:
        ...

    def swap(self, from_symbol: str, to_symbol: str, amount: Decimal) -> str:
        ...
