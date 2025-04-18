import pytest
from src.telegram_bot import parse_signal, log_trade

def test_parse_signal():
    result = parse_signal("Buy SOL at 150")
    assert result == ('SOL', 'Buy', 150.0)
    result = parse_signal("Sell BTC at 60000")
    assert result == ('BTC', 'Sell', 60000.0)
    result = parse_signal("Invalid message")
    assert result is None

def test_log_trade():
    log_trade('SOL', 'Buy', 150.0, 0.01, 'market')
    import sqlite3
    conn = sqlite3.connect('data/trading_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trades WHERE asset='SOL' AND action='Buy' AND price=150.0")
    result = cursor.fetchone()
    conn.close()
    assert result is not None