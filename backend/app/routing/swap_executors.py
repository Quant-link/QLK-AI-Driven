"""
Gerçek DEX API'leri kullanarak swap transaction'ları oluşturan modül
"""
import os
import requests
import time
from typing import Dict, Any, Optional
from decimal import Decimal
from app.config.tokens import TOKENS

class OneInchSwapExecutor:
    """1inch API kullanarak gerçek swap transaction'ları oluşturur"""
    
    def __init__(self):
        self.api_key = os.getenv("ONEINCH_API_KEY")
        self.base_url = "https://api.1inch.io/v5.0/1"
        self.chain_id = "1"  # Ethereum mainnet
        
    def build_swap_transaction(self, quote_data: Dict[str, Any], user_address: str, slippage_tolerance: float = 1.0) -> Optional[Dict[str, Any]]:
        """1inch API kullanarak swap transaction oluştur"""
        try:
            if not self.api_key:
                print("[1INCH ERROR] API key not found")
                return None
                
            execution_data = quote_data.get("execution_data", {})
            
            params = {
                "fromTokenAddress": execution_data.get("from_address"),
                "toTokenAddress": execution_data.get("to_address"), 
                "amount": execution_data.get("amount_wei"),
                "fromAddress": user_address,
                "slippage": slippage_tolerance,
                "disableEstimate": "false",
                "allowPartialFill": "false"
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "accept": "application/json"
            }
            
            url = f"{self.base_url}/swap"
            
            print(f"[1INCH] Building swap transaction...")
            print(f"[1INCH] URL: {url}")
            print(f"[1INCH] Params: {params}")
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"[1INCH ERROR] Status: {response.status_code}, Response: {response.text}")
                return None
                
            data = response.json()
            
            # 1inch response format'ını standart format'a çevir
            tx_data = data.get("tx", {})
            
            result = {
                "to": tx_data.get("to"),
                "data": tx_data.get("data"),
                "value": tx_data.get("value", "0"),
                "gas": tx_data.get("gas"),
                "gasPrice": tx_data.get("gasPrice"),
                "from": user_address,
                "chainId": 1,
                "source": "1inch"
            }
            
            print(f"[1INCH] ✅ Transaction built successfully")
            return result
            
        except Exception as e:
            print(f"[1INCH ERROR] {e}")
            return None

class OpenOceanSwapExecutor:
    """OpenOcean API kullanarak gerçek swap transaction'ları oluşturur"""
    
    def __init__(self):
        self.base_url = "https://open-api.openocean.finance/v3/eth"
        
    def build_swap_transaction(self, quote_data: Dict[str, Any], user_address: str, slippage_tolerance: float = 1.0) -> Optional[Dict[str, Any]]:
        """OpenOcean API kullanarak swap transaction oluştur"""
        try:
            execution_data = quote_data.get("execution_data", {})
            
            params = {
                "inTokenAddress": execution_data.get("from_address"),
                "outTokenAddress": execution_data.get("to_address"),
                "amount": execution_data.get("amount_wei"),
                "gasPrice": "5000000000",  # 5 gwei
                "slippage": int(slippage_tolerance * 100),  # OpenOcean expects percentage * 100
                "account": user_address
            }
            
            url = f"{self.base_url}/swap_quote"
            
            print(f"[OPENOCEAN] Building swap transaction...")
            print(f"[OPENOCEAN] URL: {url}")
            print(f"[OPENOCEAN] Params: {params}")
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"[OPENOCEAN ERROR] Status: {response.status_code}, Response: {response.text}")
                return None
                
            data = response.json()
            
            if data.get("code") != 200:
                print(f"[OPENOCEAN ERROR] API Error: {data.get('error')}")
                return None
                
            swap_data = data.get("data", {})
            
            result = {
                "to": swap_data.get("to"),
                "data": swap_data.get("data"),
                "value": swap_data.get("value", "0"),
                "gas": swap_data.get("estimatedGas"),
                "gasPrice": swap_data.get("gasPrice"),
                "from": user_address,
                "chainId": 1,
                "source": "openocean"
            }
            
            print(f"[OPENOCEAN] ✅ Transaction built successfully")
            return result
            
        except Exception as e:
            print(f"[OPENOCEAN ERROR] {e}")
            return None

class UniswapSwapExecutor:
    """Uniswap contract'ları kullanarak direkt swap transaction'ları oluşturur"""
    
    def __init__(self):
        self.router_v2 = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
        self.router_v3 = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
        
    def build_swap_transaction(self, quote_data: Dict[str, Any], user_address: str, slippage_tolerance: float = 1.0) -> Optional[Dict[str, Any]]:
        """Uniswap contract kullanarak swap transaction oluştur"""
        try:
            # Bu kısım daha karmaşık - Web3 contract interaction gerekiyor
            # Şimdilik basit bir placeholder
            print(f"[UNISWAP] Building swap transaction...")
            print(f"[UNISWAP] TODO: Implement direct contract interaction")
            
            # Placeholder - gerçek implementation sonraki adımda
            return None
            
        except Exception as e:
            print(f"[UNISWAP ERROR] {e}")
            return None

def get_swap_executor(source: str):
    """Source'a göre uygun executor döndür"""
    source_lower = source.lower()
    
    if "1inch" in source_lower:
        return OneInchSwapExecutor()
    elif "openocean" in source_lower:
        return OpenOceanSwapExecutor()
    elif "uniswap" in source_lower or "sushiswap" in source_lower:
        return UniswapSwapExecutor()
    else:
        return None
