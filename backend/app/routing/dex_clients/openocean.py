import requests
from decimal import Decimal

from app.routing.dex_clients.base import DexClient
from app.strategies.arbitrage_and_twap import TOKEN_INFO

OPENOCEAN_QUOTE_URL = "https://open-api.openocean.finance/v3/eth/quote"
OPENOCEAN_SWAP_URL  = "https://open-api.openocean.finance/v3/eth/swap"

class OpenOceanClient(DexClient):
    name = "OpenOcean"

    def __init__(self, chain: str = "eth"):
        self.chain = chain

    def _resolve(self, symbol: str) -> (str, int): # type: ignore
        key = symbol.lower()
        if key not in TOKEN_INFO:
            raise ValueError(f"Unsupported token: {symbol}")
        info = TOKEN_INFO[key]
        return info["address"], info["decimals"]

    def get_quote(self, from_symbol: str, to_symbol: str, amount: Decimal) -> Decimal:
        from_addr, from_decimals = self._resolve(from_symbol)
        to_addr, to_decimals     = self._resolve(to_symbol)

        params = {
            "inTokenAddress":  from_addr,
            "outTokenAddress": to_addr,
            "amount":           str(int(amount * (Decimal(10) ** from_decimals))),
            "slippage":         1,
            "gasPrice":         str(30 * 10**9),
        }
        resp = requests.get(OPENOCEAN_QUOTE_URL, params=params)
        resp.raise_for_status()
        data = resp.json().get("data", {})

        raw_int = int(data.get("outAmount", 0))
        out_token_info = data.get("outToken", {})
        decimals = int(out_token_info.get("decimals", TOKEN_INFO[to_symbol.lower()]["decimals"]))
        return Decimal(raw_int) / (Decimal(10) ** decimals)

    def swap(self, from_symbol: str, to_symbol: str, amount: Decimal) -> str:
        from_addr, from_decimals = self._resolve(from_symbol)
        to_addr, _               = self._resolve(to_symbol)

        params = {
            "inTokenAddress":  from_addr,
            "outTokenAddress": to_addr,
            "amount":           str(int(amount * (Decimal(10) ** from_decimals))),
            "slippage":         1,
            "gasPrice":         str(30 * 10**9),
        }
        resp = requests.get(OPENOCEAN_SWAP_URL, params=params)
        resp.raise_for_status()
        swap_data = resp.json().get("data", {})
        return swap_data.get("txHash", "")

def get_openocean_quote(from_token: str, to_token: str, amount: float) -> dict:
    """
    OpenOcean quote bilgisi döndürür
    """
    try:
        # Mock data döndür - gerçek implementasyon için API entegrasyonu gerekli
        return {
            "expectedAmountOut": amount * 0.98,  # %2 slippage
            "path": [from_token, to_token],
            "gasEstimate": 180000,
            "priceImpact": 0.15
        }
    except Exception as e:
        print(f"OpenOcean quote error: {e}")
        return None
