import requests

KYBER_API_URL = "https://aggregator-api.kyberswap.com/v1/ethereum/route"

TOKEN_ADDRESSES = {
    "WETH": "0xC02aaA39b223FE8D0A0E5C4F27eAD9083C756Cc2",
    "USDC": "0xA0b86991C6218b36c1d19D4a2e9Eb0cE3606eB48",
    "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
}

def get_kyber_route(from_token: str, to_token: str, amount: float):
    if from_token not in TOKEN_ADDRESSES or to_token not in TOKEN_ADDRESSES:
        raise ValueError("Unsupported token symbol.")

    token_in = TOKEN_ADDRESSES[from_token]
    token_out = TOKEN_ADDRESSES[to_token]
    amount_in = int(amount * 1e18)

    url = f"{KYBER_API_URL}?tokenIn={token_in}&tokenOut={token_out}&amountIn={amount_in}&gasInclude=true"
    print(f"➡️ Kyber URL: {url}")

    response = requests.get(url)

    print(f"📡 Status: {response.status_code}")
    if response.status_code != 200:
        raise Exception(f"Kyber Error {response.status_code}: {response.text}")

    data = response.json()
    if "routeSummary" not in data:
        return None

    return {
        "expectedAmountOut": int(data["routeSummary"]["amountOut"]) / 1e18,
        "path": [from_token, to_token]
    }
