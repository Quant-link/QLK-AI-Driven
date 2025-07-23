import time
import random

def get_price_exchange_A(symbol):
    return 60000 + random.uniform(-100, 100)

def get_price_exchange_B(symbol):
    return 60000 + random.uniform(-80, 80)

def place_order_exchange_A(symbol, order_type, quantity, price=None):
    print(f"[Exchange A] Order Placed: {order_type} {quantity} {symbol} @ {price if price else 'Market'}")
    return {
        "order_id": "A_" + str(random.randint(1000, 9999)),
        "status": "FILLED" if random.random() > 0.1 else "NEW"
    }

def place_order_exchange_B(symbol, order_type, quantity, price=None):
    print(f"[Exchange B] Order Placed: {order_type} {quantity} {symbol} @ {price if price else 'Market'}")
    return {
        "order_id": "B_" + str(random.randint(1000, 9999)),
        "status": "FILLED" if random.random() > 0.1 else "NEW"
    }

def find_and_execute_arbitrage(symbol="BTC/USDT", min_profit_percentage=0.001, trade_amount_usdt=100):
    print(f"\n--- Arbitrage Check ({symbol}) ---")
    price_A = get_price_exchange_A(symbol)
    price_B = get_price_exchange_B(symbol)

    if not price_A or not price_B:
        print("Prices could not be retrieved, skipping arbitrage check.")
        return False

    print(f"Exchange A Price: {price_A:.2f}")
    print(f"Exchange B Price: {price_B:.2f}")

    profit_ab = (price_B - price_A) / price_A
    profit_ba = (price_A - price_B) / price_B

    quantity_to_trade_ab = trade_amount_usdt / price_A if price_A else 0
    quantity_to_trade_ba = trade_amount_usdt / price_B if price_B else 0

    if profit_ab > min_profit_percentage:
        print(f"Arbitrage Opportunity (A->B): Profit %{profit_ab * 100:.4f}")
        print(f"Buying {quantity_to_trade_ab:.6f} {symbol.split('/')[0]} from Exchange A...")
        buy_order = place_order_exchange_A(symbol, "BUY", quantity_to_trade_ab, price_A)
        if buy_order and buy_order["status"] == "FILLED":
            print(f"Selling {quantity_to_trade_ab:.6f} {symbol.split('/')[0]} on Exchange B...")
            sell_order = place_order_exchange_B(symbol, "SELL", quantity_to_trade_ab, price_B)
            if sell_order and sell_order["status"] == "FILLED":
                print(f"Arbitrage Successful! Estimated Profit: {trade_amount_usdt * profit_ab:.2f} USDT")
                return True
            else:
                print("Sell order on Exchange B did not execute. Position may remain open!")
        else:
            print("Buy order on Exchange A did not execute.")
        return False

    elif profit_ba > min_profit_percentage:
        print(f"Arbitrage Opportunity (B->A): Profit %{profit_ba * 100:.4f}")
        print(f"Buying {quantity_to_trade_ba:.6f} {symbol.split('/')[0]} from Exchange B...")
        buy_order = place_order_exchange_B(symbol, "BUY", quantity_to_trade_ba, price_B)
        if buy_order and buy_order["status"] == "FILLED":
            print(f"Selling {quantity_to_trade_ba:.6f} {symbol.split('/')[0]} on Exchange A...")
            sell_order = place_order_exchange_A(symbol, "SELL", quantity_to_trade_ba, price_A)
            if sell_order and sell_order["status"] == "FILLED":
                print(f"Arbitrage Successful! Estimated Profit: {trade_amount_usdt * profit_ba:.2f} USDT")
                return True
            else:
                print("Sell order on Exchange A did not execute. Position may remain open!")
        else:
            print("Buy order on Exchange B did not execute.")
        return False

    else:
        print("No arbitrage opportunity found.")
        return False

def execute_twap_order(symbol, total_quantity, num_steps, interval_seconds, order_type="BUY", exchange="A"):
    print(f"\n--- TWAP Order Starting ({order_type} {total_quantity} {symbol} / {num_steps} Steps) ---")
    quantity_per_step = total_quantity / num_steps
    executed_quantity = 0

    for i in range(num_steps):
        print(f"Step {i+1}/{num_steps}:")
        current_price = get_price_exchange_A(symbol) if exchange == "A" else get_price_exchange_B(symbol)
        if not current_price:
            print("Price could not be retrieved, skipping TWAP step.")
            time.sleep(interval_seconds)
            continue

        print(f"Current Price: {current_price:.2f}")

        if exchange == "A":
            order_result = place_order_exchange_A(symbol, order_type, quantity_per_step, current_price)
        else:
            order_result = place_order_exchange_B(symbol, order_type, quantity_per_step, current_price)

        if order_result and order_result["status"] == "FILLED":
            executed_quantity += quantity_per_step
            print(f"Step {i+1} successful. Executed Quantity: {quantity_per_step:.6f} {symbol.split('/')[0]}")
        else:
            print(f"Step {i+1} failed or order did not execute. It can be retried or logged.")

        if i < num_steps - 1:
            print(f"Waiting {interval_seconds} seconds before next step...")
            time.sleep(interval_seconds)

    print(f"\n--- TWAP Order Completed ---")
    print(f"Total of {executed_quantity:.6f} {symbol.split('/')[0]} {order_type} executed.")

if __name__ == "__main__":
    arbitrage_symbol = "BTC/USDT"
    min_arbitrage_profit = 0.0005
    arbitrage_trade_amount_usdt = 500

    twap_symbol = "ETH/USDT"
    twap_total_quantity = 0.1
    twap_num_steps = 10
    twap_interval_seconds = 10

    print("Trade Bot Starting...")

    execute_twap_order(
        twap_symbol,
        twap_total_quantity,
        twap_num_steps,
        twap_interval_seconds,
        order_type="BUY",
        exchange="A"
    )

    print("\n--- Starting Arbitrage Loop ---")
    try:
        while True:
            arbitrage_found = find_and_execute_arbitrage(
                arbitrage_symbol,
                min_arbitrage_profit,
                arbitrage_trade_amount_usdt
            )

            if not arbitrage_found:
                print("No arbitrage opportunity found. Retrying in 5 seconds...")
                time.sleep(5)
            else:
                print("Arbitrage opportunity found and executed. Waiting briefly...")
                time.sleep(10)

    except KeyboardInterrupt:
        print("\nBot manually stopped.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")