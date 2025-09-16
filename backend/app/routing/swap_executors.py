"""
Gerçek DEX API'leri kullanarak swap transaction'ları oluşturan modül
"""
import os
import requests
import time
from typing import Dict, Any, Optional
from decimal import Decimal
from app.config.tokens import TOKENS
from eth_abi import encode

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

            # ETH handling - 1inch ETH için özel adres kullanır
            from_address = execution_data.get("from_address")
            to_address = execution_data.get("to_address")

            # ETH için 1inch'in özel adresi
            original_from_token = execution_data.get("original_from_token", quote_data.get("from_token", ""))
            original_to_token = execution_data.get("original_to_token", quote_data.get("to_token", ""))

            if original_from_token == "ETH":
                from_address = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
            if original_to_token == "ETH":
                to_address = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"

            params = {
                "fromTokenAddress": from_address,
                "toTokenAddress": to_address,
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

            # Quote'dan gas bilgilerini al, yoksa API'den gelen değerleri kullan
            quote_gas_estimate = quote_data.get("gas_estimate")
            quote_gas_price = quote_data.get("gas_price")

            # Gas bilgilerini öncelik sırasına göre belirle
            gas_estimate = tx_data.get("gas") or quote_gas_estimate or "0x30d40"  # 200K fallback
            gas_price = tx_data.get("gasPrice") or quote_gas_price or None

            # Gas price'ı hex formatına çevir
            if gas_price and isinstance(gas_price, int):
                gas_price = hex(gas_price)

            result = {
                "to": tx_data.get("to"),
                "data": tx_data.get("data"),
                "value": tx_data.get("value", "0"),
                "gas": gas_estimate,
                "gasPrice": gas_price,
                "from": user_address,
                "chainId": 1,
                "source": "1inch"
            }

            print(f"[1INCH] ✅ Transaction built - Gas: {gas_estimate}, Price: {gas_price}")
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

            # Quote'dan gas bilgilerini al, yoksa API'den gelen değerleri kullan
            quote_gas_estimate = quote_data.get("gas_estimate")
            quote_gas_price = quote_data.get("gas_price")

            # Gas bilgilerini öncelik sırasına göre belirle
            gas_estimate = swap_data.get("estimatedGas") or quote_gas_estimate or "0x30d40"  # 200K fallback
            gas_price = swap_data.get("gasPrice") or quote_gas_price or None

            # Gas price'ı hex formatına çevir
            if gas_price and isinstance(gas_price, int):
                gas_price = hex(gas_price)

            result = {
                "to": swap_data.get("to"),
                "data": swap_data.get("data"),
                "value": swap_data.get("value", "0"),
                "gas": gas_estimate,
                "gasPrice": gas_price,
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

    def _estimate_gas_for_swap_type(self, quote_data: Dict, execution_data: Dict) -> str:
        """Swap türüne göre dinamik gas estimation"""
        try:
            # Quote'dan gas bilgisini al
            quote_gas_estimate = quote_data.get("gas_estimate")
            if quote_gas_estimate:
                # Quote'dan gelen değeri hex formatına çevir
                if isinstance(quote_gas_estimate, int):
                    return hex(quote_gas_estimate)
                elif isinstance(quote_gas_estimate, str) and quote_gas_estimate.startswith('0x'):
                    return quote_gas_estimate
                else:
                    return hex(int(quote_gas_estimate))

            # Fallback: Swap türüne göre realistic gas estimates
            is_eth_swap = execution_data.get("is_eth_swap", False)
            original_from_token = execution_data.get("original_from_token", "")
            original_to_token = execution_data.get("original_to_token", "")

            if is_eth_swap and original_from_token == "ETH":
                # ETH → Token: ~120,000 gas
                return "0x1d4c0"  # 120,000
            elif is_eth_swap and original_to_token == "ETH":
                # Token → ETH: ~180,000 gas (approval zaten yapılmışsa)
                return "0x2bf20"  # 180,000
            else:
                # Token → Token: ~250,000 gas
                return "0x3d090"  # 250,000

        except Exception as e:
            print(f"[UNISWAP GAS] Estimation error: {e}")
            return "0x30d40"  # 200,000 fallback
        
    def build_swap_transaction(self, quote_data: Dict[str, Any], user_address: str, slippage_tolerance: float = 1.0) -> Optional[Dict[str, Any]]:
        """Uniswap/SushiSwap contract kullanarak swap transaction oluştur"""
        try:
            execution_data = quote_data.get("execution_data", {})
            router_address = execution_data.get("router_address", self.router_v2)

            print(f"[UNISWAP] Building swap transaction...")
            print(f"[UNISWAP] Router: {router_address}")
            print(f"[UNISWAP] ETH Swap: {execution_data.get('is_eth_swap', False)}")

            # ETH swap için özel handling
            is_eth_swap = execution_data.get("is_eth_swap", False)
            original_from_token = execution_data.get("original_from_token", "")
            original_to_token = execution_data.get("original_to_token", "")

            # Gerçek Uniswap transaction data oluştur
            if is_eth_swap and original_from_token == "ETH":
                # ETH → Token swap
                amount_wei = execution_data.get("amount_wei", "0")
                to_address = execution_data.get("to_address")

                # swapExactETHForTokens parametreleri
                # Gerçek slippage protection - quote'dan expected amount'ı al
                expected_amount_out = execution_data.get("expected_amount_out", 0)
                to_decimals = execution_data.get("to_decimals", 18)

                # Expected amount'ı wei'ye çevir
                expected_amount_wei = int(expected_amount_out * (10 ** to_decimals))

                # Slippage tolerance uygula (örn: %1 = 0.99)
                slippage_multiplier = (100 - slippage_tolerance) / 100
                amount_out_min = int(expected_amount_wei * slippage_multiplier)

                print(f"[UNISWAP] Expected: {expected_amount_out} tokens")
                print(f"[UNISWAP] Expected Wei: {expected_amount_wei}")
                print(f"[UNISWAP] Min Output (slippage {slippage_tolerance}%): {amount_out_min}")

                path = [execution_data.get("from_address"), to_address]  # WETH → Token
                to = user_address  # Recipient
                deadline = int(time.time()) + 1200  # 20 dakika

                # ABI encode
                function_sig = "0x7ff36ab5"  # swapExactETHForTokens(uint256,address[],address,uint256)
                encoded_params = encode(
                    ['uint256', 'address[]', 'address', 'uint256'],
                    [amount_out_min, path, to, deadline]
                ).hex()

                call_data = function_sig + encoded_params

                print(f"[UNISWAP] ETH→Token swap: {amount_wei} wei")
                print(f"[UNISWAP] Path: {path}")

                # Ensure value is in hex format
                hex_value = amount_wei if amount_wei.startswith('0x') else f"0x{hex(int(amount_wei))[2:]}"

                # Dinamik gas estimation
                gas_estimate = self._estimate_gas_for_swap_type(quote_data, execution_data)

                # Gas price'ı quote'dan al
                gas_price = quote_data.get("gas_price")
                if gas_price and isinstance(gas_price, int):
                    gas_price = hex(gas_price)

                return {
                    "to": router_address,
                    "data": call_data,
                    "value": hex_value,
                    "gas": gas_estimate,
                    "gasPrice": gas_price,
                }
            elif is_eth_swap and original_to_token == "ETH":
                # Token → ETH swap
                amount_wei = execution_data.get("amount_wei", "0")
                from_address = execution_data.get("from_address")

                # swapExactTokensForETH parametreleri
                amount_in = int(amount_wei)  # Input token amount
                expected_amount_out = execution_data.get("expected_amount_out", 0)
                to_decimals = execution_data.get("to_decimals", 18)

                # Expected amount'ı wei'ye çevir (ETH için 18 decimal)
                expected_amount_wei = int(expected_amount_out * (10 ** to_decimals))

                # Slippage tolerance uygula
                slippage_multiplier = (100 - slippage_tolerance) / 100
                amount_out_min = int(expected_amount_wei * slippage_multiplier)

                path = [from_address, execution_data.get("to_address")]  # Token → WETH
                to = user_address  # Recipient
                deadline = int(time.time()) + 1200  # 20 dakika

                print(f"[UNISWAP] Token→ETH swap: {amount_in} wei")
                print(f"[UNISWAP] Min ETH output: {amount_out_min} wei")
                print(f"[UNISWAP] Path: {path}")

                # ABI encode
                function_sig = "0x18cbafe5"  # swapExactTokensForETH(uint256,uint256,address[],address,uint256)
                encoded_params = encode(
                    ['uint256', 'uint256', 'address[]', 'address', 'uint256'],
                    [amount_in, amount_out_min, path, to, deadline]
                ).hex()

                call_data = function_sig + encoded_params

                # Dinamik gas estimation
                gas_estimate = self._estimate_gas_for_swap_type(quote_data, execution_data)

                # Gas price'ı quote'dan al
                gas_price = quote_data.get("gas_price")
                if gas_price and isinstance(gas_price, int):
                    gas_price = hex(gas_price)

                return {
                    "to": router_address,
                    "data": call_data,
                    "value": "0x0",
                    "gas": gas_estimate,
                    "gasPrice": gas_price,
                }
            else:
                # Token → Token swap
                amount_wei = execution_data.get("amount_wei", "0")
                from_address = execution_data.get("from_address")
                to_address = execution_data.get("to_address")

                # swapExactTokensForTokens parametreleri
                amount_in = int(amount_wei)  # Input token amount
                expected_amount_out = execution_data.get("expected_amount_out", 0)
                to_decimals = execution_data.get("to_decimals", 18)

                # Expected amount'ı wei'ye çevir
                expected_amount_wei = int(expected_amount_out * (10 ** to_decimals))

                # Slippage tolerance uygula
                slippage_multiplier = (100 - slippage_tolerance) / 100
                amount_out_min = int(expected_amount_wei * slippage_multiplier)

                path = [from_address, to_address]  # Token → Token
                to = user_address  # Recipient
                deadline = int(time.time()) + 1200  # 20 dakika

                print(f"[UNISWAP] Token→Token swap: {amount_in} wei")
                print(f"[UNISWAP] Min output: {amount_out_min} wei")
                print(f"[UNISWAP] Path: {path}")

                # ABI encode
                function_sig = "0x38ed1739"  # swapExactTokensForTokens(uint256,uint256,address[],address,uint256)
                encoded_params = encode(
                    ['uint256', 'uint256', 'address[]', 'address', 'uint256'],
                    [amount_in, amount_out_min, path, to, deadline]
                ).hex()

                call_data = function_sig + encoded_params

                # Dinamik gas estimation
                gas_estimate = self._estimate_gas_for_swap_type(quote_data, execution_data)

                # Gas price'ı quote'dan al
                gas_price = quote_data.get("gas_price")
                if gas_price and isinstance(gas_price, int):
                    gas_price = hex(gas_price)

                return {
                    "to": router_address,
                    "data": call_data,
                    "value": "0x0",
                    "gas": gas_estimate,
                    "gasPrice": gas_price,
                }

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
