import time
import argparse
import threading
from decimal import Decimal
from typing import List, Dict, Tuple, Optional, Any
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
from app.routing.dex_clients.uniswap import UniswapClient
from app.routing.dex_clients.base import DexClient
from app.routing.dex_clients.dexscreener import DexScreenerClient
from app.routing.dex_clients.zerox import ZeroXClient
from app.routing.dex_clients.oneinch import OneInchClient
from app.routing.dex_clients.openocean import OpenOceanClient
from app.strategies.arbitrage_and_twap import fetch_all_usd_prices
from app.config.tokens import TOKENS 

STATE: Dict[str, Dict] = {
    "plans": {},   
    "next_id": 1,  
}
RUNNING: Dict[str, bool] = {}           

LOCK = threading.RLock()

EXEC_LOG: list[dict[str, Any]] = []

def _append_exec_log(entry: dict[str, Any]) -> None:
    EXEC_LOG.append(entry)
    if len(EXEC_LOG) > 1000:
        del EXEC_LOG[: len(EXEC_LOG) - 1000]

PRICE_POLL_SEC = 5          
PRICE_TICKER_RUNNING = False

def _new_plan_id() -> int:
    with LOCK:
        pid = STATE["next_id"]
        STATE["next_id"] += 1
        return pid


class DCAStrategy:
    def __init__(self, dex_clients: List[DexClient], usd_prices: Dict[str, Decimal], plan_key: str, delay_seconds: int):
        self.dex_clients = dex_clients
        self.usd_prices = usd_prices
        self.plan_key = plan_key
        self.delay_seconds = delay_seconds

    def _fetch_best_quote(
        self,
        from_symbol: str,
        to_symbol: str,
        amount: Decimal
    ) -> Tuple[DexClient, Decimal]:
        from_price = self.usd_prices.get(from_symbol.lower()) or self.usd_prices.get(from_symbol.upper())
        to_price   = self.usd_prices.get(to_symbol.lower())   or self.usd_prices.get(to_symbol.upper())

        if to_price is None or Decimal(to_price) <= 0:
            raise RuntimeError(f"No spot price for {to_symbol}")

        if from_price is None or Decimal(from_price) <= 0:
            expected_qty = amount / Decimal(to_price)
        else:
            expected_qty = amount * (Decimal(str(from_price)) / Decimal(str(to_price)))

        best_pair: Optional[Tuple[DexClient, Decimal]] = None
        best_dev = Decimal('Infinity')
        threshold = Decimal('1.0')

        for dex in self.dex_clients:
            try:
                quote = dex.get_quote(from_symbol.upper(), to_symbol.upper(), amount)
            except Exception:
                continue
            if quote is None or quote <= 0:
                continue
            deviation = abs(quote - expected_qty) / expected_qty
            if deviation <= threshold:
                return dex, quote
            if deviation < best_dev:
                best_dev = deviation
                best_pair = (dex, quote)

        if best_pair:
            return best_pair

        if from_price is not None and to_price is not None:
            fallback_qty = amount * (Decimal(str(from_price)) / Decimal(str(to_price)))
            print(f"[FALLBACK] Using spot price for {from_symbol}->{to_symbol} = {fallback_qty}")
            return self.dex_clients[0], fallback_qty

        raise RuntimeError(f"No valid quotes and no fallback price for {from_symbol}->{to_symbol}")


    def _execute_trade(
        self,
        dex: DexClient,
        from_symbol: str,
        to_symbol: str,
        amount: Decimal
    ) -> str:
        return dex.swap(from_symbol.upper(), to_symbol.upper(), amount)

    def init_plan(
        self,
        token: str,
        total_usd: Decimal,
        total_intervals: int
    ) -> Dict:
        with LOCK:
            existing = STATE["plans"].get(self.plan_key)
            if existing:
                return existing

        try:
            now_price_raw = fetch_all_usd_prices()
            now_price_val = now_price_raw.get(token.lower(), now_price_raw.get("qlk", 0))
            now_price = Decimal(str(now_price_val))
        except Exception:
            now_price = Decimal("0")

        with LOCK:
            existing = STATE["plans"].get(self.plan_key)
            if existing:
                return existing

            plan_state = {
                "id": _new_plan_id(),
                "token": token.upper(),
                "plan": self.plan_key,              
                "status": "active",
                "total_investment": float(total_usd),
                "intervals_completed": 0,
                "total_intervals": total_intervals,
                "avg_buy_price": 0.0,               
                "current_price": float(now_price),
                "total_tokens": 0.0,
                "current_value": 0.0,
                "pnl": 0.0,
                "pnl_percentage": 0.0,
                "invested_so_far": 0.0,
                "next_buy_in": self.delay_seconds // 60,  
                "frequency": "interval",
                "logs": []
            }
            STATE["plans"][self.plan_key] = plan_state
            return plan_state

    def run(
        self,
        from_symbol: str,
        to_symbol: str,
        total_usd: Decimal,
        intervals: int
    ):
        amount_per_trade = (total_usd / intervals).quantize(Decimal('0.0001'))

        plan_state = self.init_plan(
            token=to_symbol,
            total_usd=total_usd,
            total_intervals=intervals
        )

        print(
            f"Starting DCA for {to_symbol.upper()} ({self.plan_key}): {intervals} trades of {amount_per_trade} {from_symbol} each.",
            flush=True
        )
        for i in range(1, intervals + 1):
            try:
                fresh_raw = fetch_all_usd_prices()
                self.usd_prices = {k.lower(): Decimal(str(v)) for k, v in fresh_raw.items()}

                dex, received = self._fetch_best_quote(from_symbol, to_symbol, amount_per_trade)
                tx = self._execute_trade(dex, from_symbol, to_symbol, amount_per_trade)

                with LOCK:
                    plan_state["intervals_completed"] += 1
                    plan_state["total_tokens"] = float(Decimal(str(plan_state["total_tokens"])) + received)

                    plan_state["invested_so_far"] = float(Decimal(str(plan_state["invested_so_far"])) + amount_per_trade)

                    SIX = Decimal("0.000001")
                    invested_so_far_dec = Decimal(str(plan_state["invested_so_far"]))
                    total_tokens_dec    = Decimal(str(plan_state["total_tokens"]))
                    avg_buy = (invested_so_far_dec / total_tokens_dec) if total_tokens_dec > 0 else Decimal("0")
                    plan_state["avg_buy_price"] = float(avg_buy.quantize(SIX))

                    plan_state["logs"].append({
                        "interval": i,
                        "dex": dex.name,
                        "amount_usd": float(amount_per_trade),
                        "tokens_received": float(received),
                        "tx": tx,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })

                unit_price = (amount_per_trade / received).quantize(Decimal("0.000001")) if received > 0 else Decimal(0)
                _append_exec_log({
                    "strategy": "DCA",
                    "plan": self.plan_key,
                    "token": to_symbol.upper(),
                    "action": "Buy Order",
                    "amount": float(amount_per_trade),
                    "price": float(unit_price),
                    "tokens": float(received),
                    "dex": dex.name,
                    "status": "success",
                    "time": datetime.now(timezone.utc).isoformat(),
                })

                print(f"  {to_symbol.upper()} DCA {i}/{intervals}: Bought {received} on {dex.name}", flush=True)

            except Exception as err:
                _append_exec_log({
                    "strategy": "DCA",
                    "plan": self.plan_key,
                    "token": to_symbol.upper(),
                    "action": "Buy Order",
                    "amount": float(amount_per_trade),
                    "price": None,
                    "tokens": 0.0,
                    "dex": "unknown",
                    "status": "failed",
                    "error": str(err),
                    "time": datetime.now(timezone.utc).isoformat(),
                })
                print(f"  {to_symbol.upper()} DCA {i}/{intervals} failed: {err}", flush=True)

            if i < intervals:
                time.sleep(self.delay_seconds)

        with LOCK:
            plan_state["status"] = "completed"
            plan_state["next_buy_in"] = 0
        print(f"Completed DCA for {to_symbol.upper()} ({self.plan_key}).\n", flush=True)


router = APIRouter()

def _sorted_plans_list() -> List[Dict]:
    def plan_steps(plan: Dict) -> int:
        try:
            return int(str(plan.get("plan","")).split("-")[1])
        except Exception:
            return 9999
    with LOCK:
        plans = list(STATE["plans"].values())
    plans.sort(key=plan_steps)
    return plans

def _precreate_plan(plan_key: str, token: str, total_usd: float, total_intervals: int, delay_seconds: int):
    with LOCK:
        if plan_key in STATE["plans"]:
            del STATE["plans"][plan_key]
        STATE["plans"][plan_key] = {
            "id": _new_plan_id(),
            "token": token.upper(),
            "plan": plan_key,
            "status": "active",
            "total_investment": float(total_usd),
            "intervals_completed": 0,
            "total_intervals": int(total_intervals),
            "avg_buy_price": 0.0,
            "current_price": 0.0,
            "total_tokens": 0.0,
            "current_value": 0.0,
            "pnl": 0.0,
            "pnl_percentage": 0.0,
            "invested_so_far": 0.0,
            "next_buy_in": delay_seconds // 60,
            "frequency": "interval",
            "logs": []
        }

def _apply_price_to_plans(spot_map: Dict[str, Decimal]) -> None:
    TWO = Decimal("0.01")
    SIX = Decimal("0.000001")

    with LOCK:
        plans = list(STATE["plans"].values())

    for plan in plans:
        token_l = plan["token"].lower()
        spot = spot_map.get(token_l) or (spot_map.get("qlk") if plan["token"].upper() == "QLK" else None)
        if spot is None:
            continue

        total_tokens     = Decimal(str(plan.get("total_tokens", 0.0)))
        invested_so_far  = Decimal(str(plan.get("invested_so_far", 0.0)))  

        current_value = total_tokens * spot
        pnl           = current_value - invested_so_far
        pnl_pct       = (pnl / invested_so_far * Decimal(100)) if invested_so_far > 0 else Decimal(0)

        with LOCK:
            plan["current_price"]   = float(spot.quantize(SIX))
            plan["current_value"]   = float(current_value.quantize(SIX))
            plan["pnl"]             = float(pnl.quantize(SIX))
            plan["pnl_percentage"]  = float(pnl_pct.quantize(SIX))
            plan["invested_so_far"] = float(invested_so_far.quantize(TWO))

def _price_ticker_loop():
    while True:
        try:
            raw = fetch_all_usd_prices()
            spot_map = {k: Decimal(str(v)) for k, v in raw.items()}
            _apply_price_to_plans(spot_map)
        except Exception as e:
            print("[ticker] price fetch/apply error:", e, flush=True)
        time.sleep(PRICE_POLL_SEC)

def _start_ticker_if_needed():
    global PRICE_TICKER_RUNNING
    with LOCK:
        if PRICE_TICKER_RUNNING:
            return
        PRICE_TICKER_RUNNING = True
    t = threading.Thread(target=_price_ticker_loop, daemon=True)
    t.start()

@router.get("/api/dca_data")
def get_dca_data():
    _start_ticker_if_needed()

    try:
        with LOCK:
            have_any_price = any(p.get("current_price") for p in STATE["plans"].values())
        if not have_any_price:
            raw = fetch_all_usd_prices()
            spot_map = {k: Decimal(str(v)) for k, v in raw.items()}
            _apply_price_to_plans(spot_map)
    except Exception as e:
        print("[/api/dca_data bootstrap price error]", e, flush=True)

    return {"strategies": _sorted_plans_list()}

def _run_plan_in_background(
    plan_key: str,
    from_symbol: str,
    to_symbol: str,
    total_usd: Decimal,
    intervals: int,
    delay_seconds: int
):
    with LOCK:
        if RUNNING.get(plan_key):
            return
        RUNNING[plan_key] = True

    try:
        usd_prices_raw = fetch_all_usd_prices()
        usd_prices = {k.lower(): Decimal(str(v)) for k, v in usd_prices_raw.items()}
        dex_clients: List[DexClient] = [DexScreenerClient()]
        strategy = DCAStrategy(
            dex_clients=dex_clients,
            usd_prices=usd_prices,
            plan_key=plan_key,
            delay_seconds=delay_seconds
        )
        strategy.init_plan(token=to_symbol, total_usd=total_usd, total_intervals=intervals)
        strategy.run(
            from_symbol=from_symbol,
            to_symbol=to_symbol,
            total_usd=total_usd,
            intervals=intervals
        )
    finally:
        with LOCK:
            RUNNING[plan_key] = False

@router.post("/api/dca_start")
def start_dca(
    from_symbol: str = Query(default="USDT"),
    to_symbol: str = Query(default="qlk"),
    total_usd: float = Query(default=500.0),
    intervals: int = Query(default=5, description="Allowed: 5, 10, 15"),
    delay_seconds: int = Query(default=60)
):
    to_symbol = to_symbol.lower()
    if to_symbol != "qlk":
        raise HTTPException(status_code=400, detail="Only QLK is supported in this mode.")
    if intervals not in (5, 10, 15):
        raise HTTPException(status_code=400, detail="intervals must be one of 5, 10, 15.")

    plan_key = f"{to_symbol.upper()}-{intervals}"

    _precreate_plan(plan_key, to_symbol, total_usd, intervals, delay_seconds)

    _start_ticker_if_needed()

    t = threading.Thread(
        target=_run_plan_in_background,
        kwargs=dict(
            plan_key=plan_key,
            from_symbol=from_symbol,
            to_symbol=to_symbol,
            total_usd=Decimal(str(total_usd)),
            intervals=intervals,
            delay_seconds=delay_seconds
        ),
        daemon=True
    )
    t.start()

    return {"status": "DCA started", "token": to_symbol.upper(), "plan": plan_key}

@router.post("/api/dca_start_all")
def start_dca_all(
    from_symbol: str = Query(default="USDT"),
    to_symbol: str = Query(default="qlk"),
    total_usd_5: float = Query(default=500.0),
    total_usd_10: float = Query(default=500.0),
    total_usd_15: float = Query(default=500.0),
    delay_seconds: int = Query(default=60)
):
    to_symbol = to_symbol.lower()
    if to_symbol != "qlk":
        raise HTTPException(status_code=400, detail="Only QLK is supported in this mode.")

    _start_ticker_if_needed()

    results = []
    for intervals, amt in [(5, total_usd_5), (10, total_usd_10), (15, total_usd_15)]:
        plan_key = f"{to_symbol.upper()}-{intervals}"

        _precreate_plan(plan_key, to_symbol, amt, intervals, delay_seconds)

        t = threading.Thread(
            target=_run_plan_in_background,
            kwargs=dict(
                plan_key=plan_key,
                from_symbol=from_symbol,
                to_symbol=to_symbol,
                total_usd=Decimal(str(amt)),
                intervals=intervals,
                delay_seconds=delay_seconds
            ),
            daemon=True
        )
        t.start()

        results.append({"plan": plan_key, "status": "DCA started", "token": to_symbol.upper(), "total_usd": amt})

    return {"started": results}

@router.get("/api/execution_log")
def get_execution_log(limit: int = Query(default=100, ge=1, le=1000)):
    with LOCK:
        data = EXEC_LOG[-limit:]
    return {"items": data[::-1]}

def main():
    parser = argparse.ArgumentParser(
        description="Run DCA for USDT-based pairs across tokens."
    )
    parser.add_argument(
        "--total-usd", dest="total_usd", required=True,
        type=Decimal,
        help="Total USD amount to spend per token"
    )
    parser.add_argument(
        "--intervals", dest="intervals", default=5,
        type=int,
        help="Number of DCA intervals per token (suggested: 5, 10, 15)"
    )
    parser.add_argument(
        "--delay", dest="delay_seconds", default=60,
        type=int,
        help="Delay between intervals in seconds"
    )
    parser.add_argument(
        "--tokens", dest="tokens", nargs="*", default=["qlk"],
        help="List of target symbols (here: only 'qlk')"
    )
    args = parser.parse_args()

    usd_prices_raw = fetch_all_usd_prices()
    usd_prices = {k.lower(): Decimal(str(v)) for k, v in usd_prices_raw.items()}

    dex_clients: List[DexClient] = [
        ZeroXClient(), OneInchClient(), OpenOceanClient()
    ]
    from_symbol = "USDT"

    targets = args.tokens
    for to_symbol in targets:
        plan_key = f"{to_symbol.upper()}-{args.intervals}"
        strategy = DCAStrategy(
            dex_clients=dex_clients,
            usd_prices=usd_prices,
            plan_key=plan_key,
            delay_seconds=args.delay_seconds
        )
        strategy.run(
            from_symbol=from_symbol,
            to_symbol=to_symbol,
            total_usd=args.total_usd,
            intervals=args.intervals
        )


if __name__ == "__main__":
    main()
