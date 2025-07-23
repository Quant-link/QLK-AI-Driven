from app.routing.route_finder import get_best_route
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--from', dest='from_token', required=True)
    parser.add_argument('--to', dest='to_token', required=True)
    parser.add_argument('--amount', type=float, required=True)
    args = parser.parse_args()

    print(f"🔍 Finding best route from {args.from_token} to {args.to_token} for {args.amount}...")

    route = get_best_route(args.from_token.upper(), args.to_token.upper(), args.amount)

    if route:
        print(f"\n✅ Best Route Found via {route['source']}")
        print(f"  Expected Output: {route['expectedAmountOut']} {args.to_token}")
        print(f"  Path: {route['path']}")
    else:
        print("❌ No optimal route found.")

if __name__ == "__main__":
    main()
