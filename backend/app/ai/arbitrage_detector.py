from app.aggregator.price_feed import calculate_slippage

DEX_CHAINS = {
    "uniswap_v2": "ethereum",
    "uniswap_v3": "ethereum",
    "sushiswap": "ethereum",
    "curve": "ethereum",
    "balancer": "ethereum",
    "pancakeswap_v3": "bsc",
    "quickswap": "polygon",
    "1inch": "ethereum",
}

BRIDGE_COSTS = {
    ("ethereum", "bsc"): {"fee_pct": 0.1, "time_minutes": 3},
    ("ethereum", "polygon"): {"fee_pct": 0.07, "time_minutes": 5},
    ("bsc", "polygon"): {"fee_pct": 0.06, "time_minutes": 4},
    ("polygon", "ethereum"): {"fee_pct": 0.08, "time_minutes": 6},
    ("bsc", "ethereum"): {"fee_pct": 0.1, "time_minutes": 3},
}

def detect_arbitrage(token_data: dict, gas_costs: dict):
    opportunities = []

    for symbol, entries in token_data.items():
        if len(entries) < 2:
            continue

        for i in range(len(entries)):
            for j in range(i + 1, len(entries)):
                buy = entries[i]
                sell = entries[j]

                if buy['price'] >= sell['price']:
                    buy, sell = sell, buy

                spread_pct = ((sell['price'] - buy['price']) / buy['price']) * 100
                if spread_pct < 0.01:
                    continue

                amount_usd = 1000

                buy_slippage = calculate_slippage(amount_usd, buy["liquidity"])
                sell_slippage = calculate_slippage(amount_usd, sell["liquidity"])
                total_slippage_cost = amount_usd * (buy_slippage + sell_slippage) / 100

                dex_fee = amount_usd * 0.006

                buy_chain = DEX_CHAINS.get(buy["dex"], "ethereum")
                sell_chain = DEX_CHAINS.get(sell["dex"], "ethereum")
                eth_price = 3000

                gas_buy = gas_costs.get(buy_chain, {}).get("fast", 25)
                gas_sell = gas_costs.get(sell_chain, {}).get("fast", 25)
                gas_cost_usd = (gas_buy + gas_sell) * 100_000 * 1e-9 * eth_price

                bridge_cost = 0
                execution_delay_sec = 30
                bridge_info = None

                if buy_chain != sell_chain:
                    bridge_key = (buy_chain, sell_chain)
                    bridge_info = BRIDGE_COSTS.get(bridge_key)

                if bridge_info:
                    fee_pct = bridge_info["fee_pct"]
                    time_minutes = bridge_info["time_minutes"]
                    bridge_cost = amount_usd * (fee_pct / 100)
                    execution_delay_sec += time_minutes * 60
                else:
                    bridge_cost = amount_usd * 0.15
                    execution_delay_sec += 10 * 60
                    
                total_cost = total_slippage_cost + dex_fee + gas_cost_usd + bridge_cost
                gross_profit = amount_usd * (spread_pct / 100)
                net_profit = gross_profit - total_cost

                if net_profit <= 0:
                    print(f"⛔ SKIPPED {symbol} | Gross: {gross_profit:.4f} | Cost: {total_cost:.4f} → Net: {net_profit:.4f}")
                    continue

                liquidity_score = min(min(buy["liquidity"], sell["liquidity"]) / 500000, 1.0)
                volume_score = min(min(buy["volume"], sell["volume"]) / 1000000, 1.0)
                confidence = round((liquidity_score + volume_score) / 2, 2)
                risk_score = round(1 - confidence, 2)

                opportunities.append({
                    "symbol": symbol,
                    "buy_from": buy['dex'],
                    "buy_price": round(buy['price'], 6),
                    "sell_to": sell['dex'],
                    "sell_price": round(sell['price'], 6),
                    "spread_pct": round(spread_pct, 2),
                    "net_profit_usd": round(net_profit, 2),
                    "gas_cost_usd": round(gas_cost_usd, 2),
                    "risk_score": risk_score,
                    "confidence": confidence,
                    "bridge_cost_usd": round(bridge_cost, 2),
                    "execution_time_sec": execution_delay_sec,
                })

    opportunities.sort(key=lambda x: x["net_profit_usd"], reverse=True)
    return opportunities[:5]