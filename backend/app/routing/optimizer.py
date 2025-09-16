from app.routing.route_finder import get_best_route
from app.config.tokens import TOKENS
import argparse
from typing import Dict, Any, Optional
from decimal import Decimal

def get_best_quote(from_token: str, to_token: str, amount: float) -> dict:
    """Mevcut quote sistemi - geriye uyumluluk için"""
    route = get_best_route(from_token.upper(), to_token.upper(), amount)

    if not route:
        return {"success": False, "message": "No optimal route found."}

    # Hata durumları için özel handling
    if isinstance(route, dict) and not route.get("success", True):
        return route  # Hata mesajını olduğu gibi döndür

    return {
        "success": True,
        "source": route.get("source"),
        "bestDex": route.get("bestDex"),
        "expectedAmountOut": route.get("expectedAmountOut"),
        "path": route.get("path")
    }

def get_best_quote_with_execution_data(from_token: str, to_token: str, amount: float) -> dict:
    """Gelişmiş quote sistemi - execution data ile birlikte"""
    try:
        from_token = from_token.upper()
        to_token = to_token.upper()

        # ETH ↔ WETH özel durumu kontrolü (dönüşüm yapmadan önce)
        is_eth_weth_swap = (
            (from_token == "ETH" and to_token == "WETH") or
            (from_token == "WETH" and to_token == "ETH")
        )

        if is_eth_weth_swap:
            # ETH ↔ WETH için özel handling - dönüşüm yapma
            route_from_token = from_token
            route_to_token = to_token
        else:
            # Normal durumda ETH → WETH dönüşümü (DEX'ler WETH kullanır)
            route_from_token = "WETH" if from_token == "ETH" else from_token
            route_to_token = "WETH" if to_token == "ETH" else to_token

        # Token bilgilerini doğrula
        if route_from_token not in TOKENS or route_to_token not in TOKENS:
            return {"success": False, "message": "Token not supported"}

        from_token_info = TOKENS[route_from_token]
        to_token_info = TOKENS[route_to_token]

        # Sadece Ethereum tokenlarını destekle (şimdilik)
        if from_token_info.get("chain") != "ethereum" or to_token_info.get("chain") != "ethereum":
            return {"success": False, "message": "Only Ethereum tokens supported currently"}

        # En iyi route'u bul (WETH kullanarak)
        route = get_best_route(route_from_token, route_to_token, amount)

        if not route:
            return {"success": False, "message": "No optimal route found."}

        # Hata durumları için özel handling
        if isinstance(route, dict) and not route.get("success", True):
            error_type = route.get("error", "UNKNOWN")
            if error_type == "PAIR_NOT_SUPPORTED":
                return {
                    "success": False,
                    "message": route.get("message", "Token pair not supported"),
                    "error": "PAIR_NOT_SUPPORTED",
                    "supported_pairs": route.get("supported_pairs", [])
                }
            elif error_type == "NO_LIQUIDITY":
                return {
                    "success": False,
                    "message": route.get("message", "No liquidity available"),
                    "error": "NO_LIQUIDITY",
                    "supported_dexes": route.get("supported_dexes", [])
                }
            else:
                return {
                    "success": False,
                    "message": route.get("message", "Route finding failed"),
                    "error": error_type
                }

        # Execution data ekle
        execution_data = prepare_execution_data(route, from_token_info, to_token_info, amount)

        # ETH handling bilgisini ekle
        execution_data["is_eth_swap"] = from_token == "ETH" or to_token == "ETH"
        execution_data["original_from_token"] = from_token
        execution_data["original_to_token"] = to_token

        # Expected amount out ekle (slippage protection için)
        execution_data["expected_amount_out"] = route.get("expectedAmountOut", 0)

        result = {
            "success": True,
            "from_token": from_token,
            "to_token": to_token,
            "amount": amount,
            "source": route.get("source"),
            "bestDex": route.get("bestDex"),
            "expectedAmountOut": route.get("expectedAmountOut"),
            "path": route.get("path"),
            "execution_data": execution_data,
            "gas_estimate": route.get("estimatedGas"),
            "gas_price": route.get("gasPrice"),
            "price_impact": calculate_price_impact(amount, route.get("expectedAmountOut", 0)),
        }

        print(f"[OPTIMIZER] Best route: {route.get('source')} - {route.get('expectedAmountOut')} {to_token}")
        return result

    except Exception as e:
        print(f"[OPTIMIZER ERROR] {e}")
        return {"success": False, "message": f"Quote generation failed: {str(e)}"}

def prepare_execution_data(route: Dict[str, Any], from_token_info: Dict, to_token_info: Dict, amount: float) -> Dict[str, Any]:
    """Route bilgisine göre execution data hazırla"""
    source = route.get("source", "").lower()

    base_data = {
        "from_address": from_token_info.get("address"),
        "to_address": to_token_info.get("address"),
        "from_decimals": from_token_info.get("decimals", 18),
        "to_decimals": to_token_info.get("decimals", 18),
        "amount_wei": str(int(amount * (10 ** from_token_info.get("decimals", 18)))),
    }

    if "1inch" in source:
        return {
            **base_data,
            "execution_method": "1inch_api",
            "api_endpoint": "https://api.1inch.io/v5.0/1/swap",
            "requires_api_key": True
        }
    elif "openocean" in source:
        return {
            **base_data,
            "execution_method": "openocean_api",
            "api_endpoint": "https://open-api.openocean.finance/v3/eth/swap_quote",
            "requires_api_key": False
        }
    elif "uniswap" in source or "sushiswap" in source:
        return {
            **base_data,
            "execution_method": "direct_contract",
            "router_address": get_router_address(source),
            "requires_api_key": False
        }
    else:
        return {
            **base_data,
            "execution_method": "fallback",
            "requires_api_key": False
        }

def get_router_address(source: str) -> str:
    """Source'a göre router address döndür"""
    source_lower = source.lower()

    if "uniswap v2" in source_lower:
        return "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    elif "uniswap v3" in source_lower:
        return "0xE592427A0AEce92De3Edee1F18E0157C05861564"
    elif "sushiswap" in source_lower:
        return "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
    else:
        return "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"  # Default Uniswap V2

def calculate_price_impact(amount_in: float, amount_out: float) -> float:
    """Basit price impact hesaplama"""
    if amount_in == 0 or amount_out == 0:
        return 0.0

    # Bu basit bir hesaplama - gerçek price impact daha karmaşık
    # Şimdilik placeholder olarak bırakıyorum
    return 0.1  # %0.1 sabit price impact

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--from', dest='from_token', required=True)
    parser.add_argument('--to', dest='to_token', required=True)
    parser.add_argument('--amount', type=float, required=True)
    args = parser.parse_args()

    print(f"🔍 Finding best route from {args.from_token} to {args.to_token} for {args.amount}...")

    route = get_best_route(args.from_token.upper(), args.to_token.upper(), args.amount)

    if route:
        print(f"\n✅ Best Route Found via {route.get('source')}")
        if 'bestDex' in route:
            print(f"  Best DEX: {route['bestDex']}")
        print(f"  Expected Output: {route.get('expectedAmountOut')} {args.to_token.upper()}")
        if 'path' in route:
            print(f"  Path: {route['path']}")
    else:
        print("❌ No optimal route found.")

if __name__ == "__main__":
    main()
