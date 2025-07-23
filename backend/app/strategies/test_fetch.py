from app.aggregator.price_feed import fetch_token_data

tokens = ["ETH", "PEPE", "SHIB", "UNI", "MATIC", "AAVE", "ARB"]

for symbol in tokens:
    data = fetch_token_data(symbol)
    if data:
        print(f"\n🔹 {symbol}:")
        for item in data:
            print(f"  DEX: {item['dex']}, Price: ${item['price']}, Liq: ${item['liquidity']}, Vol: ${item['volume']}")
