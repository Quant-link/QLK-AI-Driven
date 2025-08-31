import json, os
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

TOKENS_JSON_PATH = os.getenv("TOKENS_JSON_PATH", "app/config/tokens.json")

def load_tokens_file() -> Dict[str, Any]:
    if not os.path.exists(TOKENS_JSON_PATH):
        return {}
    with open(TOKENS_JSON_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception:
            data = []
    out: Dict[str, Any] = {}
    if isinstance(data, list):
        for t in data:
            sym = (t.get("symbol") or "").upper()
            if not sym:
                continue
            out[sym] = {
                "symbol": sym,
                "chain": t.get("chain", "ethereum"),
                "address": t.get("address"),
                "decimals": int(t.get("decimals", 18)),
                "cg_id": t.get("cg_id")  
            }
    elif isinstance(data, dict):
        for sym, t in data.items():
            out[sym.upper()] = {
                "symbol": sym.upper(),
                "chain": t.get("chain", "ethereum"),
                "address": t.get("address"),
                "decimals": int(t.get("decimals", 18)),
                "cg_id": t.get("cg_id")
            }
    return out

def save_tokens_file(tokens_list: List[Dict[str, Any]]) -> None:
    with open(TOKENS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(tokens_list, f, ensure_ascii=False, indent=2)

def refresh_tokens() -> Dict[str, Any]:
    return load_tokens_file()

TOKENS: Dict[str, Any] = load_tokens_file()

def get_token(symbol: str) -> Dict[str, Any]:
    return TOKENS.get(symbol.upper())
