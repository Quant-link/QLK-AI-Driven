import sys, os
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_tokens_endpoint():
    r = client.get("/tokens")
    assert r.status_code == 200
    data = r.json()
    assert "tokens" in data
    assert isinstance(data["tokens"], list)

def test_quote_endpoint():
    r = client.post("/quote", params={"from_token": "ETH", "to_token": "USDT", "amount": 0.01})
    assert r.status_code == 200
    data = r.json()
    assert "success" in data
    if data["success"]:
        assert "expectedAmountOut" in data

def test_swap_endpoint():
    r = client.post(
        "/swap",
        params={
            "from_token": "ETH",
            "to_token": "USDT",
            "amount": 0.01,
            "user_address": "0x000000000000000000000000000000000000dead"
        }
    )
    assert r.status_code == 200
    data = r.json()
    assert "success" in data
    if data["success"]:
        assert "tx" in data
        assert "to" in data["tx"]

def test_status_endpoint_pending():
    fake_hash = "0x" + "0"*64
    r = client.get("/status", params={"tx_hash": fake_hash})
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
