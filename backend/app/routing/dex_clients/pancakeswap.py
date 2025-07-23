import requests

def get_pancakeswap_quote(from_token: str, to_token: str, amount: float):
    url = f"https://api.pancakeswap.info/api/v2/quote?fromToken={from_token}&toToken={to_token}&amount={amount}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching PancakeSwap quote: {e}")
