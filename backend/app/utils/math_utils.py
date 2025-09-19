import math

def calculate_slippage(trade_size_usd: float, liquidity_usd: float) -> float:
    if liquidity_usd <= 0:
        return 100.0
    slippage_factor = math.sqrt(trade_size_usd / liquidity_usd)
    volatility_adjustment = 1.2
    return min(slippage_factor * volatility_adjustment * 100, 50.0)
