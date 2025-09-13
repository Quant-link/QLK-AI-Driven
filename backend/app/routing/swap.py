from fastapi import APIRouter
from app.routing.optimizer import get_best_quote
from app.routing.route_finder import build_swap_tx, get_tx_status

router = APIRouter()

@router.get("/tokens")
def get_tokens():
    return {"tokens": []}

@router.post("/quote")
def get_quote(from_token: str, to_token: str, amount: float):
    result = get_best_quote(from_token, to_token, amount)
    return result

@router.post("/swap")
def get_swap_tx(from_token: str, to_token: str, amount: float, user_address: str):
    tx = build_swap_tx(from_token, to_token, amount, user_address)
    if not tx:
        return {"success": False, "message": "Swap transaction could not be built."}
    return {"success": True, "tx": tx}

@router.get("/status")
def get_status(tx_hash: str):
    return get_tx_status(tx_hash)
