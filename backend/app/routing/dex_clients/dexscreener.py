import requests
import time
import logging

# Zincir eşlemesi: internal → dexscreener
chain_mapping = {
    "ethereum": "ethereum",
    "bsc": "bsc",
    "polygon": "polygon",
    "arbitrum": "arbitrum",
    "base": "base",
    "avalanche": "avalanche",
    "solana": "solana",
    "aptos": "aptos"
    # unsupported chains like osmosis, pulsechain, thala should be skipped
}


def get_token_info(query: str):
    try:
        base_url = "https://api.dexscreener.com/latest/dex/search"
        response = requests.get(base_url, params={"q": query})
        response.raise_for_status()
        data = response.json()

        if data.get("pairs"):
            best_pair = data["pairs"][0]
            return {
                "chain": best_pair["chainId"],
                "address": best_pair["pairAddress"]
            }

        symbol_query = query.upper()
        response = requests.get(base_url, params={"q": symbol_query})
        response.raise_for_status()
        data = response.json()

        if data.get("pairs"):
            best_pair = data["pairs"][0]
            return {
                "chain": best_pair["chainId"],
                "address": best_pair["pairAddress"]
            }

        return None
    except Exception as e:
        print(f"❌ Dexscreener error for {query}: {e}")
        time.sleep(0.5)
        return None


def get_token_pairs_by_symbol(symbol: str):
    try:
        url = f"https://api.dexscreener.com/latest/dex/search"
        response = requests.get(url, params={"q": symbol})
        response.raise_for_status()
        data = response.json()

        pairs = data.get("pairs", [])
        if not isinstance(pairs, list):
            logging.warning(f"[WARN] No valid pairs list for {symbol}: {pairs}")
            return []

        return pairs

    except Exception as e:
        logging.warning(f"[ERROR] Dexscreener fetch failed for {symbol}: {e}")
        time.sleep(0.5)
        return []