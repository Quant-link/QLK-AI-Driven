from app.routing.route_finder import get_best_route
import argparse

def get_best_quote(from_token: str, to_token: str, amount: float) -> dict:
    route = get_best_route(from_token.upper(), to_token.upper(), amount)

    if not route:
        return {"success": False, "message": "No optimal route found."}

    return {
        "success": True,
        "source": route.get("source"),
        "bestDex": route.get("bestDex"),
        "expectedAmountOut": route.get("expectedAmountOut"),
        "path": route.get("path")
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--from', dest='from_token', required=True)
    parser.add_argument('--to', dest='to_token', required=True)
    parser.add_argument('--amount', type=float, required=True)
    args = parser.parse_args()

    print(f"🔍 Finding best route from {args.from_token} to {args.to_token} for {args.amount}...")

    route = get_best_route(args.from_token.upper(), args.to_token.upper(), args.amount)

    if route:
        print(f"\n✅ Best Route Found via {route.get('source')}")
        if 'bestDex' in route:
            print(f"  Best DEX: {route['bestDex']}")
        print(f"  Expected Output: {route.get('expectedAmountOut')} {args.to_token.upper()}")
        if 'path' in route:
            print(f"  Path: {route['path']}")
    else:
        print("❌ No optimal route found.")

if __name__ == "__main__":
    main()
