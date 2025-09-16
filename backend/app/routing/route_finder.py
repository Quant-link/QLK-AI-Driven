import os, requests, random, time
from typing import Optional, Dict, Any, List, Tuple
from fastapi import APIRouter, Query

from app.routing.dex_clients.oneinch import get_oneinch_route
from app.routing.dex_clients.openocean import get_openocean_quote
from app.strategies.arbitrage_and_twap import fetch_all_usd_prices
from app.config.tokens import TOKENS
from app.config.tokens import get_token
from app.config.dex_config import (
    get_dex_eth_address,
    is_pair_supported,
    get_supported_dexes_for_pair,
    get_dex_endpoint_info
)
from eth_abi import encode
# Mainnet Router Addresses
UNISWAP_V2_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
UNISWAP_V3_QUOTER = "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6"
SUSHISWAP_ROUTER = "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F"
from web3 import Web3
from decimal import Decimal

# ---------- RPC ----------
ETH_RPC_URL = os.getenv("ETH_RPC_URL", "")
w3: Optional[Web3] = Web3(Web3.HTTPProvider(ETH_RPC_URL)) if ETH_RPC_URL else None

# ---------- ABIs ----------
UNIV2_ROUTER_ABI = [
    {
        "constant": True,
        "inputs": [
            {"name": "amountIn", "type": "uint256"},
            {"name": "path", "type": "address[]"}
        ],
        "name": "getAmountsOut",
        "outputs": [{"name": "amounts", "type": "uint256[]"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

UNIV3_QUOTER_ABI = [
    {
        "inputs": [
            {"internalType":"address","name":"tokenIn","type":"address"},
            {"internalType":"address","name":"tokenOut","type":"address"},
            {"internalType":"uint24","name":"fee","type":"uint24"},
            {"internalType":"uint256","name":"amountIn","type":"uint256"},
            {"internalType":"uint160","name":"sqrtPriceLimitX96","type":"uint160"}
        ],
        "name":"quoteExactInputSingle",
        "outputs":[
            {"internalType":"uint256","name":"amountOut","type":"uint256"},
            {"internalType":"uint160","name":"sqrtPriceX96After","type":"uint160"},
            {"internalType":"uint32","name":"initializedTicksCrossed","type":"uint32"},
            {"internalType":"uint256","name":"gasEstimate","type":"uint256"}
        ],
        "stateMutability":"nonpayable",
        "type":"function"
    }
]

UNISWAP_V2_ROUTER = Web3.to_checksum_address("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D")
SUSHI_ROUTER      = Web3.to_checksum_address("0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F")
UNISWAP_V3_QUOTER = Web3.to_checksum_address("0x61fFE014bA17989E743c5F6cB21bF9697530B21e")

V3_COMMON_FEES = [500, 3000, 10000]

ALLOWED_PROTOCOLS = [
    "UNISWAP_V2","UNISWAP_V3","SUSHI","CURVE","BALANCER",
    "RAYDIUM","PANCAKESWAP","OSMOSIS","PULSEX","PUMPSWAP","SWAPPI",
]

TOKEN_ADDRESS_MAP = {
    "USDT":   "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "USDC":   "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "DAI":    "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "WBTC":   "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    "WETH":   "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    "BTC":    "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    "LINK":   "0x514910771AF9Ca656af840dff83E8264EcF986CA",
    "UNI":    "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "AAVE":   "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9",
    "QLK":    "0xe226B7Ae83a44Bb98F67BEA28C4ad73B0925C49E",
    "MATIC":  "0x7D1AfA7B718fb893dB30A3aBc0Cfc608AaCfeBB0",
    "CRV":    "0xD533a949740bb3306d119CC777fa900bA034cd52",
    "COMP":   "0xc00e94Cb662C3520282E6f5717214004A7f26888",
    "MKR":    "0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2",
    "SNX":    "0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F",
    "SUSHI":  "0x6B3595068778DD592e39A122f4f5a5cF09C90fE2",
    "1INCH":  "0x111111111117dC0aa78b770fA6A738034120C302",
}
ETH_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

def _is_evm_address(x: str) -> bool:
    return isinstance(x, str) and x.startswith("0x") and len(x) == 42

def _cg_headers() -> dict:
    h = {"accept": "application/json"}
    api_key = os.getenv("COINGECKO_API_KEY")
    if api_key:
        h["x-cg-pro-api-key"] = api_key
    return h

def _resolve_via_coingecko(token_id: str) -> Optional[str]:
    base = os.getenv("COINGECKO_BASE_URL", "https://pro-api.coingecko.com/api/v3")
    url = f"{base}/coins/{token_id}"
    params = {"localization":"false","tickers":"false","market_data":"false","community_data":"false","developer_data":"false","sparkline":"false"}
    r = requests.get(url, headers=_cg_headers(), params=params, timeout=15)
    r.raise_for_status()
    data = r.json() or {}
    platforms = data.get("platforms", {}) or {}
    preferred = ["ethereum","arbitrum-one","base","polygon-pos","optimistic-ethereum","bsc"]
    for k in preferred:
        addr = platforms.get(k)
        if addr and _is_evm_address(addr):
            return addr
    for _, addr in platforms.items():
        if _is_evm_address(addr):
            return addr
    return None

def _resolve_token_input(tok: str) -> str:
    if _is_evm_address(tok):
        return tok
    u = tok.upper()
    if u == "ETH":
        return ETH_ADDRESS
    if u in TOKEN_ADDRESS_MAP:
        return TOKEN_ADDRESS_MAP[u]
    if u == "QLK":
        env_addr = os.getenv("QLK_ADDRESS")
        if env_addr and _is_evm_address(env_addr):
            return env_addr
        cg_id = os.getenv("QLK_CG_ID", "quantlink")
        addr = _resolve_via_coingecko(cg_id)
        if not addr:
            raise RuntimeError("QLK adresi CoinGecko'dan çözümlenemedi.")
        return addr
    return tok

def _decimals_for(addr_or_symbol: str) -> int:
    a = addr_or_symbol.lower()
    if a in (TOKEN_ADDRESS_MAP.get("USDC","").lower(), TOKEN_ADDRESS_MAP.get("USDT","").lower()):
        return 6
    if a == TOKEN_ADDRESS_MAP.get("WBTC","").lower():
        return 8
    return 18

def _as_float(x) -> float:
    try:
        return float(x)
    except Exception:
        return 0.0

def _is_eth_weth_pair(from_token: str, to_token: str) -> bool:
    """ETH ↔ WETH pair kontrolü"""
    eth_tokens = {"ETH", "WETH"}
    return (from_token in eth_tokens and to_token in eth_tokens and from_token != to_token)

def _get_alternative_pairs(from_token: str, to_token: str) -> List[str]:
    """Alternatif pair önerileri"""
    alternatives = []

    # ETH ile olan pairler
    if from_token != "ETH":
        alternatives.append(f"{from_token}/ETH")
    if to_token != "ETH":
        alternatives.append(f"ETH/{to_token}")

    # Stablecoin pairler
    stablecoins = ["USDT", "USDC", "DAI"]
    for stable in stablecoins:
        if from_token != stable:
            alternatives.append(f"{from_token}/{stable}")
        if to_token != stable:
            alternatives.append(f"{stable}/{to_token}")

    return alternatives[:5]  # İlk 5 öneri

def _best_label(raw: Dict[str, Any], default: str) -> str:
    for k in ("dex","protocol","bestDex","source"):
        v = raw.get(k)
        if isinstance(v,str) and v.strip():
            return v
    return default

def _to_checksum(addr_or_eth: str) -> str:
    if addr_or_eth.lower() == ETH_ADDRESS.lower():
        return Web3.to_checksum_address(TOKEN_ADDRESS_MAP["WETH"])
    return Web3.to_checksum_address(addr_or_eth)

def _current_gas_wei() -> int:
    if not w3:
        return int(Web3.to_wei(20, "gwei"))

    try:
        fh = w3.eth.fee_history(5, "latest", [25, 50, 75])
        base = fh["baseFeePerGas"][-1] 
        rewards = fh.get("reward") or []
        tips = []
        for arr in rewards:
            if arr:
                tips.append(arr[1])
        tip = int(sum(tips) / len(tips)) if tips else int(Web3.to_wei(2, "gwei"))
        return int(base) + int(tip)
    except Exception as e:
        print("[Gas] fee_history failed:", e)

    try:
        api_key = os.getenv("ETHERSCAN_API_KEY")
        if api_key:
            url = f"https://api.etherscan.io/api"
            params = {"module": "gastracker", "action": "gasoracle", "apikey": api_key}
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json() or {}
            if data.get("status") == "1":
                propose = data["result"].get("ProposeGasPrice")
                if propose:
                    return int(Web3.to_wei(float(propose), "gwei"))
    except Exception as e:
        print("[Gas] Etherscan API failed:", e)

    try:
        return int(w3.eth.gas_price)
    except Exception as e:
        print("[Gas] w3.eth.gas_price failed:", e)

    return int(Web3.to_wei(20, "gwei"))

def _v2_quote(router_addr: str, token_in: str, token_out: str, amount: float, label: str) -> Optional[Dict[str, Any]]:
    if not w3:
        return None
    try:
        router = w3.eth.contract(address=Web3.to_checksum_address(router_addr), abi=UNIV2_ROUTER_ABI)
        t_in  = _to_checksum(token_in)
        t_out = _to_checksum(token_out)
        dec_in  = _decimals_for(token_in)
        dec_out = _decimals_for(token_out)
        amt_in_wei = int(Decimal(str(amount)) * (Decimal(10) ** dec_in))

        print(f"[{label}] Checking pool: {t_in} → {t_out}")
        print(f"[{label}] Amount: {amt_in_wei} wei")

        amounts = router.functions.getAmountsOut(amt_in_wei, [t_in, t_out]).call()
        out_raw = int(amounts[-1])
        expected = float(Decimal(out_raw) / (Decimal(10) ** dec_out))

        print(f"[{label}] ✅ Pool exists! Output: {expected}")

        # Dinamik gas estimation - swap türüne göre
        def estimate_gas_for_swap(token_in_addr: str, token_out_addr: str) -> int:
            # ETH adresi kontrolü (hem zero address hem de WETH)
            eth_addresses = [
                "0x0000000000000000000000000000000000000000",  # Zero address (ETH)
                "0xC02aaA39b223FE8056b4c6bD41c659F2488D",      # WETH
                "0xc02aaa39b223fe8056b4c6bd41c659f2488d"       # WETH lowercase
            ]

            is_eth_in = token_in_addr.lower() in [addr.lower() for addr in eth_addresses]
            is_eth_out = token_out_addr.lower() in [addr.lower() for addr in eth_addresses]

            print(f"[GAS DEBUG] In: {token_in_addr} -> ETH: {is_eth_in}")
            print(f"[GAS DEBUG] Out: {token_out_addr} -> ETH: {is_eth_out}")

            if is_eth_in and not is_eth_out:
                # ETH → Token: ~120,000 gas
                print(f"[GAS DEBUG] ETH → Token: 120K gas")
                return 120_000
            elif not is_eth_in and is_eth_out:
                # Token → ETH: ~180,000 gas
                print(f"[GAS DEBUG] Token → ETH: 180K gas")
                return 180_000
            elif not is_eth_in and not is_eth_out:
                # Token → Token: ~250,000 gas
                print(f"[GAS DEBUG] Token → Token: 250K gas")
                return 250_000
            else:
                # ETH → ETH (shouldn't happen)
                print(f"[GAS DEBUG] ETH → ETH: 120K gas")
                return 120_000

        gas_units = estimate_gas_for_swap(token_in, token_out)

        return {
            "expectedAmountOut": expected,
            "dex": label,
            "path": [token_in, token_out],
            "source": label,
            "estimatedGas": gas_units,
            "gasPrice": _current_gas_wei(),
        }
    except Exception as e:
        print(f"[{label}] ❌ Pool check failed: {e}")
        return None

def _v3_quote_quoter(quoter_addr: str, token_in: str, token_out: str, amount: float, label: str) -> Optional[Dict[str, Any]]:
    if not w3:
        return None
    try:
        quoter = w3.eth.contract(address=Web3.to_checksum_address(quoter_addr), abi=UNIV3_QUOTER_ABI)
        t_in  = _to_checksum(token_in)
        t_out = _to_checksum(token_out)
        dec_in  = _decimals_for(token_in)
        dec_out = _decimals_for(token_out)
        amt_in_wei = int(Decimal(str(amount)) * (Decimal(10) ** dec_in))

        best_out = 0
        used_fee = None
        gas_units = None

        for fee in V3_COMMON_FEES:
            try:
                res = quoter.functions.quoteExactInputSingle(t_in, t_out, fee, amt_in_wei, 0).call()
                out_raw = int(res[0])
                g_est   = int(res[3]) if len(res) >= 4 else None
                if out_raw > best_out:
                    best_out = out_raw
                    used_fee = fee
                    gas_units = g_est
            except Exception:
                continue

        if best_out == 0:
            return None

        expected = float(Decimal(best_out) / (Decimal(10) ** dec_out))
        name = f"Uniswap V3 ({used_fee/10000:.2%})" if used_fee else "Uniswap V3"

        # Dinamik gas estimation - swap türüne göre
        def estimate_v3_gas_for_swap(token_in_addr: str, token_out_addr: str) -> int:
            # ETH adresi kontrolü
            eth_address = "0x0000000000000000000000000000000000000000"
            weth_address = "0xC02aaA39b223FE8056b4c6bD41c659F2488D"

            is_eth_in = token_in_addr.lower() in [eth_address.lower(), weth_address.lower()]
            is_eth_out = token_out_addr.lower() in [eth_address.lower(), weth_address.lower()]

            if is_eth_in and not is_eth_out:
                # ETH → Token: ~140,000 gas (V3 biraz daha fazla)
                return 140_000
            elif not is_eth_in and is_eth_out:
                # Token → ETH: ~200,000 gas
                return 200_000
            elif not is_eth_in and not is_eth_out:
                # Token → Token: ~280,000 gas (V3 concentrated liquidity)
                return 280_000
            else:
                # ETH → ETH (shouldn't happen)
                return 140_000

        dynamic_gas_units = estimate_v3_gas_for_swap(token_in, token_out)
        gas_units = gas_units if gas_units and gas_units > 0 else dynamic_gas_units

        return {
            "expectedAmountOut": expected,
            "dex": name,
            "path": [token_in, token_out],
            "source": "Uniswap V3",
            "estimatedGas": gas_units,
            "gasPrice": _current_gas_wei(),
        }
    except Exception:
        return None

def get_best_route(from_token: str, to_token: str, amount: float):
    """
    Ana route bulma fonksiyonu - DEX pair desteği kontrolü ile
    """
    print(f"[ROUTE] 🔍 Searching route: {from_token} → {to_token} ({amount})")

    # 1. ETH ↔ WETH özel durumu - önce kontrol et (token resolution'dan önce)
    if _is_eth_weth_pair(from_token, to_token):
        print(f"[ETH↔WETH] ✅ Special case detected: {from_token} → {to_token}")
        from_id = _resolve_token_input(from_token)
        to_id = _resolve_token_input(to_token)
        return {
            "expectedAmountOut": amount,  # 1:1 ratio
            "dex": "WETH Contract",
            "path": [from_id, to_id],
            "source": "WETH Wrap/Unwrap",
            "estimatedGas": 50_000,  # Wrap/unwrap gas cost
            "gasPrice": _current_gas_wei(),
        }

    # 2. Pair desteğini kontrol et
    supported_dexes = get_supported_dexes_for_pair(from_token, to_token)
    if not supported_dexes:
        print(f"[ROUTE] ❌ No DEX supports pair: {from_token} → {to_token}")
        return {
            "success": False,
            "error": "PAIR_NOT_SUPPORTED",
            "message": f"No liquidity pools found for {from_token}/{to_token} pair",
            "supported_pairs": _get_alternative_pairs(from_token, to_token)
        }

    print(f"[ROUTE] ✅ Supported DEXes: {supported_dexes}")

    # 3. Token resolution
    routes: List[Dict[str,Any]] = []
    from_id = _resolve_token_input(from_token)
    to_id   = _resolve_token_input(to_token)

    if not from_id or not to_id:
        print(f"[ROUTE] ❌ Token resolution failed: {from_token}→{from_id}, {to_token}→{to_id}")
        return None

    # 4. Uniswap routing (sadece destekliyorsa)
    if "uniswap" in supported_dexes and w3:
        # Uniswap için ETH → WETH dönüşümü
        uniswap_from = get_dex_eth_address("uniswap") if from_token == "ETH" else from_id
        uniswap_to = get_dex_eth_address("uniswap") if to_token == "ETH" else to_id

        print(f"[UNISWAP] Checking routes for {from_token}→{to_token}")
        r = _v2_quote(UNISWAP_V2_ROUTER, uniswap_from, uniswap_to, amount, "Uniswap V2")
        if r:
            routes.append(r)
            print(f"[UNISWAP V2] ✅ Found route: {r.get('expectedAmountOut')}")
        r = _v2_quote(SUSHI_ROUTER, uniswap_from, uniswap_to, amount, "SushiSwap")
        if r:
            routes.append(r)
            print(f"[SUSHISWAP] ✅ Found route: {r.get('expectedAmountOut')}")
        r = _v3_quote_quoter(UNISWAP_V3_QUOTER, uniswap_from, uniswap_to, amount, "Uniswap V3")
        if r:
            routes.append(r)
            print(f"[UNISWAP V3] ✅ Found route: {r.get('expectedAmountOut')}")

    time.sleep(0.1)

    # 5. OpenOcean (sadece destekliyorsa)
    if "openocean" in supported_dexes:
        try:
            # ETH adresini OpenOcean formatına çevir
            oo_from = get_dex_eth_address("openocean") if from_token == "ETH" else from_id
            oo_to = get_dex_eth_address("openocean") if to_token == "ETH" else to_id

            print(f"[OPENOCEAN] Checking route for {from_token}→{to_token}")
            oo = get_openocean_quote(oo_from, oo_to, amount, protocols=ALLOWED_PROTOCOLS)
            if oo:
                routes.append({"source": "OpenOcean", **oo})
                print(f"[OPENOCEAN] ✅ Found route: {oo.get('expectedAmountOut')}")
        except Exception as e:
            print(f"[OpenOcean Error] {e}")

    # 6. 1inch (sadece destekliyorsa)
    if "1inch" in supported_dexes:
        try:
            # ETH adresini 1inch formatına çevir
            oneinch_from = get_dex_eth_address("1inch") if from_token == "ETH" else from_id
            oneinch_to = get_dex_eth_address("1inch") if to_token == "ETH" else to_id

            print(f"[1INCH] Checking route for {from_token}→{to_token}")
            one = get_oneinch_route(oneinch_from, oneinch_to, amount, protocols=ALLOWED_PROTOCOLS)
            if one:
                routes.append({"source": "1inch", **one})
                print(f"[1INCH] ✅ Found route: {one.get('expectedAmountOut')}")
        except Exception as e:
            print(f"[1inch Error] {e}")

    if not routes:
        print(f"[ROUTE] ❌ No routes found for {from_token} → {to_token}")
        return {
            "success": False,
            "error": "NO_LIQUIDITY",
            "message": f"No liquidity available for {from_token}/{to_token} pair on supported DEXes",
            "supported_dexes": supported_dexes
        }

    best_route = max(routes, key=lambda r: _as_float(r.get("expectedAmountOut", 0)))
    print(f"[ROUTE] 🏆 Best route: {best_route.get('source')} - {best_route.get('expectedAmountOut', 'N/A')}")
    return best_route

router = APIRouter()
@router.get("/api/routes")
def get_routes_data(amount: float = Query(500, description="Base trade amount for route calculation")):
    try:
        usd_prices = fetch_all_usd_prices()
        routes_data = []

        live_pairs = [
            ("qlk", "usdt"), ("usdt", "qlk"),
            ("qlk", "eth"), ("eth", "qlk"),
            ("eth", "usdt"), ("btc", "usdt"),
            ("link", "usdt"), ("uni", "usdt"),
            ("aave", "usdt"), ("eth", "usdc"),
            ("btc", "usdc"), ("dai", "usdt"),
        ]

        eth_price = float(usd_prices.get("eth") or 1800.0)

        for idx, (from_token, to_token) in enumerate(live_pairs, start=1):
            best = get_best_route(from_token, to_token, amount)
            if not best:
                continue

            expected_out = _as_float(best.get("expectedAmountOut"))
            if expected_out <= 0:
                continue

            slippage = _as_float(best.get("slippage")) or 0.5

            try:
                est: int
                gpw: int

                source = (best.get("source") or best.get("dex") or "").lower()
                path = best.get("path") or []
                frm = path[0] if path else _resolve_token_input(from_token)
                to  = path[-1] if path else _resolve_token_input(to_token)

                got = None
                tx_obj = best.get("tx") or {}
                if isinstance(tx_obj, dict):
                    tx_to   = tx_obj.get("to", to)
                    tx_data = tx_obj.get("data", "0x")
                    tx_val  = int(tx_obj.get("value", 0))
                else:
                    tx_to   = to
                    tx_data = "0x"
                    tx_val  = 0

                est = _estimate_gas_units_for_route(best, None, None)
                gpw = _current_gas_wei()

                eth_price_effective = float(usd_prices.get("eth") or 1800.0)
                gas_usd = est * (gpw * 1e-18) * eth_price_effective
            except Exception as e:
                print("[GasCost Error]", e)
                gas_usd = 0.0

            from_price = float(usd_prices.get(from_token.lower(), 0) or 0)
            to_price   = float(usd_prices.get(to_token.lower(), 0) or 0)

            ideal_out = (amount / from_price) * to_price if from_price > 0 and to_price > 0 else 0.0

            if ideal_out > 0:
                raw_eff = (expected_out / ideal_out) * 100.0
                if raw_eff < 0:
                    eff = 0.0
                else:
                    eff = min(raw_eff, 200.0)
            else:
                eff = 0.0

            best_dex = _best_label(best, "Unknown")

            routes_data.append({
                "id": idx,
                "from_token": from_token.upper(),
                "to_token": to_token.upper(),
                "amount": round(amount, 2),
                "best_dex": best_dex,
                "expected_output": expected_out,
                "slippage": round(slippage, 2),
                "gas_cost_usd": round(gas_usd, 4) if gas_usd else 0,
                "efficiency": round(eff, 1) if eff else 0,
                "execution_time": random.uniform(2, 12),
                "path": best.get("path"),
            })

        return {"routes": routes_data}

    except Exception as e:
        print(f"[ERROR] Routes data fetch failed: {e}")
        return {"routes": []}


@router.get("/api/route_details/{from_token}/{to_token}")
def get_route_details(from_token: str, to_token: str, amount: float = 1000):
    try:
        best_route = get_best_route(from_token, to_token, amount)
        if best_route:
            return {
                "from_token": from_token.upper(),
                "to_token": to_token.upper(),
                "amount": amount,
                "best_route": best_route
            }
        else:
            return {"error": "No route found"}
    except Exception as e:
        print(f"[ERROR] Route details fetch failed: {e}")
        return {"error": "Failed to fetch route details"}

def _estimate_gas_units_for_route(best: Dict[str, Any], from_id: str, to_id: str) -> int:
    try:
        eg = int(best.get("estimatedGas") or 0)
        if eg > 0:
            return eg
    except Exception:
        pass

    dex_name = (best.get("dex") or best.get("source") or "").lower()

    if "uniswap v2" in dex_name or "uniswap_v2" in dex_name:
        base_units = 120_000
    elif "sushi" in dex_name:
        base_units = 140_000
    elif "uniswap v3" in dex_name or "uniswap_v3" in dex_name:
        base_units = 160_000
    else:
        base_units = 130_000

    hop_units = base_units
    protos = best.get("protocols")
    if protos:
        flat = []
        if isinstance(protos, list):
            for it in protos:
                if isinstance(it, list):
                    for sub in it:
                        if isinstance(sub, dict):
                            flat.append(sub)
                elif isinstance(it, dict):
                    flat.append(it)
        elif isinstance(protos, dict):
            flat.append(protos)

        if flat:
            names = []
            for x in flat:
                nm = (x.get("name") or x.get("dex") or x.get("id") or "").lower()
                if nm:
                    names.append(nm)
            hop_count = max(1, len(set(names)))
            hop_units = 110_000 + (hop_count - 1) * 55_000

    est_units = max(base_units, hop_units)

    path = best.get("path") or []
    has_eth = any((isinstance(a, str) and a.lower() == ETH_ADDRESS.lower()) for a in path)
    if has_eth:
        est_units += 10_000  

    return int(est_units)

def _tenderly_simulate_tx(from_addr: str, to_addr: str, data: str = "0x", value: int = 0) -> Optional[Tuple[int, int]]:
    access_key = os.getenv("TENDERLY_ACCESS_KEY")
    account = os.getenv("TENDERLY_ACCOUNT")
    project = os.getenv("TENDERLY_PROJECT")

    if not (access_key and account and project):
        return None

    url = f"https://api.tenderly.co/api/v1/account/{account}/project/{project}/simulate"
    headers = {
        "Content-Type": "application/json",
        "X-Access-Key": access_key
    }

    payload = {
        "network_id": "1",
        "from": from_addr,
        "to": to_addr,
        "input": data,
        "gas": 8_000_000,
        "value": str(value),
        "save": False,
        "save_if_fails": False
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        sim = r.json()
        gas_used = int(sim["simulation"]["gas_used"])
        gas_price = int(sim["simulation"]["gas_price"])
        return gas_used, gas_price
    except Exception as e:
        print("[Tenderly Error]", e)
        return None

def _oneinch_swap_gas(from_id: str, to_id: str, amount_float: float) -> Optional[Tuple[int, int]]:
    api_key = os.getenv("ONEINCH_API_KEY")
    chain_id = int(os.getenv("ONEINCH_CHAIN_ID", "1") or "1")
    from_addr = os.getenv("SIM_FROM_ADDRESS")
    if not (api_key and from_addr):
        return None

    base = f"https://api.1inch.dev/swap/v5.2/{chain_id}/swap"
    headers = {"accept": "application/json", "Authorization": f"Bearer {api_key}"}

    try:
        from_dec = _decimals_for(from_id)
    except Exception:
        from_dec = 18
    amount_wei = int(Decimal(str(amount_float)) * (Decimal(10) ** from_dec))

    params = {
        "src": from_id,
        "dst": to_id,
        "amount": str(amount_wei),
        "fromAddress": from_addr,
        "slippage": "1",     
        "disableEstimate": "false"
    }

    try:
        r = requests.get(base, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json() or {}
        tx = data.get("tx") or {}
        gas = tx.get("gas") or data.get("estimatedGas")
        gas_price = tx.get("gasPrice") or data.get("gasPrice")
        if gas and gas_price:
            return int(gas), int(gas_price)
    except Exception as e:
        print("[1inch swap gas] failed:", e)

    return None

def _zeroex_quote_gas(from_id: str, to_id: str, amount_float: float) -> Optional[Tuple[int, int]]:
    try:
        base = os.getenv("ZEROEX_BASE", "https://api.0x.org")
        url = f"{base}/swap/v1/quote"

        def _as_0x_token(addr: str) -> str:
            return "ETH" if addr.lower() == ETH_ADDRESS.lower() else Web3.to_checksum_address(addr)

        sell_addr = from_id if _is_evm_address(from_id) or from_id.lower() == ETH_ADDRESS.lower() else _resolve_token_input(from_id)
        buy_addr  = to_id   if _is_evm_address(to_id)   or to_id.lower() == ETH_ADDRESS.lower()   else _resolve_token_input(to_id)

        sell_token = _as_0x_token(sell_addr)
        buy_token  = _as_0x_token(buy_addr)

        sell_dec = 18 if sell_token == "ETH" else _decimals_for(sell_addr)
        sell_amount_wei = int(Decimal(str(amount_float)) * (Decimal(10) ** sell_dec))

        params = {
            "sellToken": sell_token,
            "buyToken": buy_token,
            "sellAmount": str(sell_amount_wei),
        }
        headers = {}
        zkey = os.getenv("ZEROEX_API_KEY")
        if zkey:
            headers["0x-api-key"] = zkey

        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        q = r.json() or {}

        eg = q.get("estimatedGas") or q.get("gas")
        gp = q.get("gasPrice")
        if eg and gp:
            return int(eg), int(gp)
    except Exception as e:
        print("[0x quote gas] failed:", e)

    return None

def fetch_1inch_swap_tx(from_token, to_token, amount, user_address):
    try:
        from_info = TOKENS[from_token]
        to_info = TOKENS[to_token]
        amount_wei = str(int(amount * (10 ** from_info["decimals"])))
        url = "https://api.1inch.io/v5.0/11155111/swap"
        params = {
            "fromTokenAddress": from_info["address"],
            "toTokenAddress": to_info["address"],
            "amount": amount_wei,
            "fromAddress": user_address,
            "slippage": 1
        }

        headers = {}
        api_key = os.getenv("ONEINCH_API_KEY")
        if api_key:
            print(f"[DEBUG] ✅ ONEINCH_API_KEY yüklendi: {api_key[:6]}****")
            headers["Authorization"] = f"Bearer {api_key}"

        print(f"[DEBUG] 1inch swap GET URL: {url}")
        print(f"[DEBUG] 1inch swap params: {params}")

        res = requests.get(url, params=params, headers=headers, timeout=15)
        print(f"[DEBUG] 1inch raw response status: {res.status_code}")
        print(f"[DEBUG] 1inch raw response text: {res.text[:300]}...")

        if res.status_code != 200:
            print(f"[1inch Swap Error] Status={res.status_code} Response={res.text}")
            return None

        data = res.json()
        return data.get("tx")
    except Exception as e:
        print("[1inch Swap Error]", e)
        return None

def build_swap_tx(from_token: str, to_token: str, amount: float, user_address: str):
    try:
        print(f"[DEBUG] 🔄 build_swap_tx() called with from={from_token}, to={to_token}, amount={amount}, user={user_address}")

        from_token_info = get_token(from_token, chain="sepolia")
        to_token_info = get_token(to_token, chain="sepolia")

        amount_in_wei = int(amount * (10 ** from_token_info["decimals"]))
        deadline = int(time.time()) + 600
        path = [from_token_info["address"], to_token_info["address"]]

        data = (
            Web3.keccak(text="swapExactETHForTokens(uint256,address[],address,uint256)")[:4]
            + encode(
                ["uint256", "address[]", "address", "uint256"],
                [0, path, user_address, deadline]
            )
        )

        return {
            "to": Web3.to_checksum_address(UNISWAP_V2_ROUTER),
            "data": data.hex(),
            "value": amount_in_wei,
            "gas": 200000,
            "gasPrice": _current_gas_wei(),
            "from": Web3.to_checksum_address(user_address),
        }

    except Exception as e:
        print("[SwapTx Error]", e)
        return None


def get_tx_status(tx_hash: str) -> Dict[str, Any]:
    try:
        if not w3:
            return {"status": "unknown"}
        receipt = w3.eth.get_transaction_receipt(tx_hash)
        if not receipt:
            return {"status": "pending"}
        status = receipt.get("status")
        return {"status": "success" if status == 1 else "failed", "blockNumber": receipt.get("blockNumber"), "gasUsed": receipt.get("gasUsed")}
    except Exception as e:
        print("[TxStatus Error]", e)
        return {"status": "unknown"}


def _tenderly_simulate_tx(from_addr: str, to_addr: str, data: str = "0x", value: int = 0) -> Optional[Tuple[int, int]]:
    acc = os.getenv("TENDERLY_ACCOUNT")
    proj = os.getenv("TENDERLY_PROJECT")
    key = os.getenv("TENDERLY_ACCESS_KEY")

    if not (acc and proj and key):
        return None

    url = f"https://api.tenderly.co/api/v1/account/{acc}/project/{proj}/simulate"
    headers = {
        "X-Access-Key": key,
        "Content-Type": "application/json"
    }
    payload = {
        "network_id": "1",
        "from": from_addr,
        "to": to_addr,
        "input": data,
        "gas": 8_000_000,
        "gas_price": str(_current_gas_wei()),   
        "value": str(value),                    
        "save": False,
        "save_if_fails": True
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=20)
        r.raise_for_status()
        sim = r.json()
        tx = sim.get("transaction", {})
        gas_used = int(tx.get("gas_used") or 0)
        gas_price = int(tx.get("effective_gas_price") or _current_gas_wei())
        if gas_used > 0:
            return gas_used, gas_price
    except Exception as e:
        print("[Tenderly Error]", e)

    return None
