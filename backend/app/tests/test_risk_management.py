# test_risk_management.py

from app.strategies.risk import set_stop_loss, calculate_position_size

def test_set_stop_loss():
    entry_price = 500
    stop_loss_percentage = 2
    expected_stop_loss_price = 490.0  # 500 * (1 - 0.02)
    
    stop_loss_price = set_stop_loss(entry_price, stop_loss_percentage)
    
    assert stop_loss_price == expected_stop_loss_price, f"Expected {expected_stop_loss_price}, but got {stop_loss_price}"
    print(f"Test Passed: Stop-Loss Fiyatı doğru hesaplandı: {stop_loss_price}")


def test_calculate_position_size():
    account_balance = 10000
    stop_loss_percentage = 2
    entry_price = 500
    current_price = 510
    stop_loss_price = set_stop_loss(entry_price, stop_loss_percentage)
    
    position_size = calculate_position_size(account_balance, 1, stop_loss_price, current_price)
    
    # Calculate expected position size manually:
    risk_amount = account_balance * (1 / 100)  # 1% risk
    expected_position_size = risk_amount / abs(current_price - stop_loss_price)
    
    print(f"Risk Amount: {risk_amount}, Expected Position Size: {expected_position_size}")
    
    assert position_size == expected_position_size, f"Expected {expected_position_size}, but got {position_size}"
    print(f"Test Passed: Pozisyon boyutu doğru hesaplandı: {position_size}")


if __name__ == "__main__":
    test_set_stop_loss()
    test_calculate_position_size()
