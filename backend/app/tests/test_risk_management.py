from decimal import Decimal
from fastapi.testclient import TestClient
from app.strategies.risk import set_stop_loss, calculate_position_size
from main import app


def test_set_stop_loss():
    entry_price = Decimal("500")
    stop_loss_percentage = Decimal("2")
    expected_stop_loss_price = Decimal("490.0")

    stop_loss_price = set_stop_loss(entry_price, stop_loss_percentage)

    assert stop_loss_price == expected_stop_loss_price, \
        f"Expected {expected_stop_loss_price}, but got {stop_loss_price}"
    print(f"✅ Test Passed: Stop-Loss Price was calculated correctly: {stop_loss_price}")


def test_calculate_position_size():
    account_balance = Decimal("10000")
    stop_loss_percentage = Decimal("2")
    entry_price = Decimal("500")
    current_price = Decimal("510")
    stop_loss_price = set_stop_loss(entry_price, stop_loss_percentage)

    position_size = calculate_position_size(account_balance, 1, stop_loss_price, current_price)

    risk_amount = account_balance * (Decimal("1") / Decimal("100"))  
    expected_position_size = risk_amount / abs(current_price - stop_loss_price)

    assert abs(position_size - expected_position_size) < Decimal("1e-6"), \
        f"Expected {expected_position_size}, but got {position_size}"
    print(f"✅ Test Passed: Position size calculated correctly: {position_size}")


def test_risk_management_endpoint():
    client = TestClient(app)
    response = client.get("/api/risk_management")
    assert response.status_code == 200
    data = response.json()
    assert "risk_data" in data
    assert isinstance(data["risk_data"], list)
    assert len(data["risk_data"]) >= 10, \
        f"Risk data too short: {len(data['risk_data'])}"
    print(f"✅ Test Passed: /api/risk_management {len(data['risk_data'])} token returned..")
