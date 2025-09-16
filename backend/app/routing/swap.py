import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from fastapi import APIRouter, HTTPException
from app.routing.optimizer import get_best_quote_with_execution_data
from app.routing.route_finder import build_swap_tx, get_tx_status
from app.config.tokens import TOKENS

router = APIRouter()

# In-memory quote cache (production'da Redis kullanılacak)
QUOTE_CACHE: Dict[str, Dict[str, Any]] = {}
QUOTE_EXPIRY_MINUTES = 5

def clean_expired_quotes():
    """Süresi dolmuş quote'ları temizle"""
    current_time = datetime.now()
    expired_keys = []

    for quote_id, quote_data in QUOTE_CACHE.items():
        if current_time > quote_data["expires_at"]:
            expired_keys.append(quote_id)

    for key in expired_keys:
        del QUOTE_CACHE[key]

def cache_quote(quote_data: Dict[str, Any]) -> str:
    """Quote'u cache'e kaydet ve ID döndür"""
    clean_expired_quotes()

    quote_id = str(uuid.uuid4())
    quote_data["quote_id"] = quote_id
    quote_data["created_at"] = datetime.now()
    quote_data["expires_at"] = datetime.now() + timedelta(minutes=QUOTE_EXPIRY_MINUTES)

    QUOTE_CACHE[quote_id] = quote_data
    return quote_id

def get_cached_quote(quote_id: str) -> Optional[Dict[str, Any]]:
    """Cache'den quote al"""
    clean_expired_quotes()
    return QUOTE_CACHE.get(quote_id)

@router.get("/tokens")
def get_tokens():
    """Gerçek token listesini döndür"""
    # Token listesini refresh et
    from app.config.tokens import refresh_tokens
    current_tokens = refresh_tokens()

    tokens = []
    for symbol, token_data in current_tokens.items():
        if token_data.get("chain") == "ethereum":  # Şimdilik sadece Ethereum
            tokens.append({
                "symbol": symbol,
                "address": token_data.get("address"),
                "decimals": token_data.get("decimals", 18),
                "chain": token_data.get("chain")
            })

    return {"tokens": tokens}

@router.post("/quote")
def get_quote(from_token: str, to_token: str, amount: float):
    """Gelişmiş quote sistemi - execution data ile birlikte"""
    try:
        # Minimum amount kontrolü
        minimum_amounts = {
            'ETH': 0.001,    # 0.001 ETH minimum
            'USDT': 5,       # 5 USDT minimum
            'USDC': 5,       # 5 USDC minimum
            'DAI': 5,        # 5 DAI minimum
            'WETH': 0.001,   # 0.001 WETH minimum
        }

        min_amount = minimum_amounts.get(from_token.upper(), 0.001)
        if amount < min_amount:
            return {
                "success": False,
                "message": f"Minimum swap amount for {from_token} is {min_amount}"
            }

        # Mevcut get_best_quote fonksiyonunu kullan ama execution data ekle
        result = get_best_quote_with_execution_data(from_token, to_token, amount)

        if not result.get("success"):
            return result

        # Quote'u cache'e kaydet
        quote_id = cache_quote(result)
        result["quote_id"] = quote_id

        print(f"[QUOTE] Created quote {quote_id} for {from_token}→{to_token}, amount: {amount}")
        return result

    except Exception as e:
        print(f"[QUOTE ERROR] {e}")
        return {"success": False, "message": f"Quote generation failed: {str(e)}"}

@router.post("/swap")
def get_swap_tx(quote_id: str, user_address: str, slippage_tolerance: float = 1.0):
    """Quote ID kullanarak swap transaction oluştur"""
    try:
        # Cache'den quote'u al
        quote_data = get_cached_quote(quote_id)
        if not quote_data:
            raise HTTPException(status_code=400, detail="Quote not found or expired")

        # Source'a göre transaction oluştur
        source = quote_data.get("source", "").lower()

        # ETH swap'ları için öncelikle 1inch kullan (daha güvenilir)
        is_eth_swap = quote_data.get("execution_data", {}).get("is_eth_swap", False)

        print(f"[SWAP] Source: {source}, ETH Swap: {is_eth_swap}")

        if source == "1inch":
            tx = build_1inch_swap_tx(quote_data, user_address, slippage_tolerance)
        elif source == "openocean":
            tx = build_openocean_swap_tx(quote_data, user_address, slippage_tolerance)
        elif source in ["uniswap v2", "uniswap v3", "sushiswap"] or is_eth_swap:
            tx = build_uniswap_swap_tx(quote_data, user_address, slippage_tolerance)
        else:
            # Fallback - Uniswap kullan
            tx = build_uniswap_swap_tx(quote_data, user_address, slippage_tolerance)

        if not tx:
            return {"success": False, "message": "Swap transaction could not be built."}

        print(f"[SWAP] Built transaction for quote {quote_id}, source: {source}")
        return {"success": True, "tx": tx, "quote_id": quote_id}

    except Exception as e:
        print(f"[SWAP ERROR] {e}")
        return {"success": False, "message": f"Swap preparation failed: {str(e)}"}

@router.get("/status")
def get_status(tx_hash: str):
    return get_tx_status(tx_hash)

# Gerçek executor'ları import et
from app.routing.swap_executors import get_swap_executor

def build_1inch_swap_tx(quote_data: Dict, user_address: str, slippage: float) -> Optional[Dict]:
    """1inch API kullanarak swap transaction oluştur"""
    executor = get_swap_executor("1inch")
    if executor:
        return executor.build_swap_transaction(quote_data, user_address, slippage)
    return None

def build_openocean_swap_tx(quote_data: Dict, user_address: str, slippage: float) -> Optional[Dict]:
    """OpenOcean API kullanarak swap transaction oluştur"""
    executor = get_swap_executor("openocean")
    if executor:
        return executor.build_swap_transaction(quote_data, user_address, slippage)
    return None

def build_uniswap_swap_tx(quote_data: Dict, user_address: str, slippage: float) -> Optional[Dict]:
    """Uniswap contract kullanarak swap transaction oluştur"""
    executor = get_swap_executor("uniswap")
    if executor:
        return executor.build_swap_transaction(quote_data, user_address, slippage)
    return None
