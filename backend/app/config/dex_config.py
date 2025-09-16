# DEX Configuration for different exchanges
from typing import Dict, List, Optional, Set

# DEX-specific ETH address formats
DEX_ETH_ADDRESSES = {
    "1inch": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
    "openocean": "0x0000000000000000000000000000000000000000", 
    "uniswap": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH for Uniswap
    "sushiswap": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH for SushiSwap
}

# DEX-specific endpoints for different swap types
DEX_ENDPOINTS = {
    "1inch": {
        "quote": "https://api.1inch.dev/swap/v6.0/1/quote",
        "swap": "https://api.1inch.dev/swap/v6.0/1/swap",
        "native_eth_support": True,
        "requires_approval": True
    },
    "openocean": {
        "quote": "https://open-api.openocean.finance/v3/eth/quote",
        "swap": "https://open-api.openocean.finance/v3/eth/swap_quote", 
        "native_eth_support": True,
        "requires_approval": True
    },
    "uniswap": {
        "quote": None,  # Custom implementation
        "swap": None,   # Custom implementation
        "native_eth_support": False,  # Uses WETH
        "requires_approval": True
    }
}

# Token pair availability per DEX (major pairs only)
DEX_SUPPORTED_PAIRS = {
    "1inch": {
        # ETH pairs
        ("ETH", "WETH"), ("ETH", "USDT"), ("ETH", "USDC"), ("ETH", "DAI"),
        ("ETH", "WBTC"), ("ETH", "UNI"), ("ETH", "LINK"), ("ETH", "AAVE"),
        ("ETH", "MATIC"), ("ETH", "CRV"), ("ETH", "COMP"), ("ETH", "MKR"),
        ("ETH", "SNX"), ("ETH", "YFI"), ("ETH", "SUSHI"), ("ETH", "BAL"),
        ("ETH", "LDO"), ("ETH", "APE"), ("ETH", "SHIB"), ("ETH", "FTM"),
        ("ETH", "GRT"), ("ETH", "ENS"), ("ETH", "MANA"), ("ETH", "SAND"), ("ETH", "IMX"),
        
        # Stablecoin pairs
        ("USDT", "USDC"), ("USDT", "DAI"), ("USDC", "DAI"),
        
        # Major token pairs
        ("WBTC", "USDT"), ("WBTC", "USDC"), ("WBTC", "DAI"),
        ("UNI", "USDT"), ("UNI", "USDC"), ("LINK", "USDT"), ("LINK", "USDC"),
        ("AAVE", "USDT"), ("AAVE", "USDC"), ("MATIC", "USDT"), ("MATIC", "USDC"),

        # Additional major pairs for Routes API
        ("BTC", "USDT"), ("BTC", "USDC"), ("DAI", "USDT"),
        ("QLK", "USDT"), ("QLK", "ETH"), ("QLK", "USDC"),
    },
    
    "openocean": {
        # ETH pairs
        ("ETH", "WETH"), ("ETH", "USDT"), ("ETH", "USDC"), ("ETH", "DAI"),
        ("ETH", "WBTC"), ("ETH", "UNI"), ("ETH", "LINK"), ("ETH", "AAVE"),
        ("ETH", "MATIC"), ("ETH", "CRV"), ("ETH", "COMP"), ("ETH", "MKR"),
        ("ETH", "SNX"), ("ETH", "YFI"), ("ETH", "SUSHI"), ("ETH", "BAL"),
        ("ETH", "LDO"), ("ETH", "APE"), ("ETH", "SHIB"), ("ETH", "FTM"),
        ("ETH", "GRT"), ("ETH", "ENS"), ("ETH", "MANA"), ("ETH", "SAND"), ("ETH", "IMX"),
        
        # Stablecoin pairs
        ("USDT", "USDC"), ("USDT", "DAI"), ("USDC", "DAI"),
        
        # Major token pairs
        ("WBTC", "USDT"), ("WBTC", "USDC"), ("UNI", "USDT"), ("UNI", "USDC"),
        ("LINK", "USDT"), ("LINK", "USDC"), ("AAVE", "USDT"), ("AAVE", "USDC"),

        # Additional major pairs for Routes API
        ("BTC", "USDT"), ("BTC", "USDC"), ("DAI", "USDT"),
        ("QLK", "USDT"), ("QLK", "ETH"), ("QLK", "USDC"),
    },
    
    "uniswap": {
        # WETH pairs (Uniswap uses WETH, not native ETH)
        ("WETH", "USDT"), ("WETH", "USDC"), ("WETH", "DAI"), ("WETH", "WBTC"),
        ("WETH", "UNI"), ("WETH", "LINK"), ("WETH", "AAVE"), ("WETH", "MATIC"),
        ("WETH", "CRV"), ("WETH", "COMP"), ("WETH", "MKR"), ("WETH", "SNX"),
        ("WETH", "YFI"), ("WETH", "SUSHI"), ("WETH", "BAL"), ("WETH", "LDO"),
        ("WETH", "APE"), ("WETH", "SHIB"), ("WETH", "FTM"), ("WETH", "GRT"),
        ("WETH", "ENS"), ("WETH", "MANA"), ("WETH", "SAND"), ("WETH", "IMX"),
        
        # ETH-WETH special case
        ("ETH", "WETH"),
        
        # Stablecoin pairs
        ("USDT", "USDC"), ("USDT", "DAI"), ("USDC", "DAI"),
        
        # Major token pairs
        ("WBTC", "USDT"), ("WBTC", "USDC"), ("UNI", "USDT"), ("UNI", "USDC"),
        ("LINK", "USDT"), ("LINK", "USDC"), ("AAVE", "USDT"), ("AAVE", "USDC"),

        # Additional major pairs for Routes API
        ("BTC", "USDT"), ("BTC", "USDC"), ("DAI", "USDT"),
        ("QLK", "USDT"), ("QLK", "ETH"), ("QLK", "USDC"),
    }
}

# Convert sets to include reverse pairs
for dex in DEX_SUPPORTED_PAIRS:
    original_pairs = list(DEX_SUPPORTED_PAIRS[dex])
    DEX_SUPPORTED_PAIRS[dex] = set(original_pairs)
    # Add reverse pairs
    for pair in original_pairs:
        DEX_SUPPORTED_PAIRS[dex].add((pair[1], pair[0]))

def get_dex_eth_address(dex_name: str) -> str:
    """Get DEX-specific ETH address format"""
    return DEX_ETH_ADDRESSES.get(dex_name.lower(), DEX_ETH_ADDRESSES["1inch"])

def is_pair_supported(dex_name: str, from_token: str, to_token: str) -> bool:
    """Check if a token pair is supported by a specific DEX"""
    dex_pairs = DEX_SUPPORTED_PAIRS.get(dex_name.lower(), set())
    # Convert to uppercase for comparison
    from_token_upper = from_token.upper()
    to_token_upper = to_token.upper()
    return (from_token_upper, to_token_upper) in dex_pairs or (to_token_upper, from_token_upper) in dex_pairs

def get_supported_dexes_for_pair(from_token: str, to_token: str) -> List[str]:
    """Get list of DEXes that support a specific token pair"""
    supported_dexes = []
    # Convert to uppercase for comparison
    from_token_upper = from_token.upper()
    to_token_upper = to_token.upper()
    for dex_name, pairs in DEX_SUPPORTED_PAIRS.items():
        if (from_token_upper, to_token_upper) in pairs or (to_token_upper, from_token_upper) in pairs:
            supported_dexes.append(dex_name)
    return supported_dexes

def get_dex_endpoint_info(dex_name: str) -> Dict:
    """Get DEX endpoint configuration"""
    return DEX_ENDPOINTS.get(dex_name.lower(), {})
