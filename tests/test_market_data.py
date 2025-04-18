import pytest
import pandas as pd
from src.market_data import fetch_crypto_data, calculate_indicators, save_market_data

def test_fetch_crypto_data():
    price, volume = fetch_crypto_data('solana')
    assert price is not None
    assert volume is not None
    assert isinstance(price, float)
    assert isinstance(volume, float)

def test_calculate_indicators():
    df = pd.DataFrame({
        'price': [150.0, 155.0, 160.0, 158.0, 162.0] * 10,  # 50 data points
        'volume': [1000.0, 1200.0, 1100.0, 1300.0, 1250.0] * 10
    })
    df = calculate_indicators(df)
    assert 'rsi' in df.columns
    assert 'macd' in df.columns
    assert 'bb_upper' in df.columns
    assert 'bb_lower' in df.columns
    assert 'vwap' in df.columns
    assert 'stoch_k' in df.columns
    assert 'stoch_d' in df.columns
    assert 'atr' in df.columns
    assert not df['rsi'].isna().any()
    assert not df['stoch_k'].isna().any()
    assert not df['atr'].isna().any()

def test_save_market_data():
    save_market_data('solana', 150.0, 1000.0, 70.0, 0.5, 155.0, 145.0, 150.0, 80.0, 75.0, 2.5)
    import sqlite3
    conn = sqlite3.connect('data/trading_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM market_data WHERE asset='solana' AND price=150.0")
    result = cursor.fetchone()
    conn.close()
    assert result is not None
    assert result[9] == 80.0  # stoch_k
    assert result[10] == 75.0  # stoch_d
    assert result[11] == 2.5  # atr