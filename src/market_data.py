import sqlite3
import pandas as pd
from datetime import datetime
import logging
import time
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD
from ta.volatility import BollingerBands, AverageTrueRange
import numpy as np
from dotenv import load_dotenv
import os
from pycoingecko import CoinGeckoAPI
import requests

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(filename='bot_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize CoinGecko API client
cg = CoinGeckoAPI()

def fetch_crypto_data(asset='solana'):
    """Mengambil data pasar dari CoinGecko."""
    try:
        # Map asset ke ID CoinGecko
        asset_map = {
            'solana': 'solana',
            'bitcoin': 'bitcoin',
            'ethereum': 'ethereum'
        }
        asset_id = asset_map.get(asset.lower(), 'solana')
        
        # Ambil data pasar
        data = cg.get_price(ids=asset_id, vs_currencies='usd', include_24hr_vol=True)
        if not data or asset_id not in data:
            raise ValueError(f"No data returned for {asset}")
        
        price = data[asset_id]['usd']
        volume = data[asset_id].get('usd_24h_vol', 0.0)
        
        logging.info(f"Fetched {asset} data: Price=${price}, Volume=${volume}")
        return price, volume
    except Exception as e:
        logging.error(f"Error fetching data for {asset}: {e}")
        return None, None

def fetch_gmgn_data():
    """Mengambil data wallet dari GMGN.ai (simulasi)."""
    try:
        url = "https://gmgn.ai/defi/leaderboard"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.text
        wallets = []
        if "win_rate" in data.lower():
            wallets.append({
                "wallet_address": "0x1234567890abcdef",
                "profit": 5000.0,
                "loss": 1000.0,
                "sharpe_ratio": 2.5,
                "win_rate": 80.0
            })
        filtered_wallets = [w for w in wallets if w['win_rate'] > 75.0]
        logging.info(f"Fetched {len(filtered_wallets)} high-performing wallets from GMGN.ai")
        return filtered_wallets
    except Exception as e:
        logging.error(f"Error fetching GMGN.ai data: {e}")
        return []

def calculate_indicators(df):
    """Menghitung indikator teknikal."""
    try:
        # RSI
        df['rsi'] = RSIIndicator(close=df['price'], window=14).rsi()
        # MACD
        df['macd'] = MACD(close=df['price']).macd()
        # Bollinger Bands
        bb = BollingerBands(close=df['price'], window=20)
        df['bb_upper'] = bb.bollinger_hband()
        df['bb_lower'] = bb.bollinger_lband()
        # VWAP
        df['vwap'] = (df['price'] * df['volume']).cumsum() / df['volume'].cumsum()
        # Stochastic Oscillator
        stoch = StochasticOscillator(high=df['price'], low=df['price'], close=df['price'], window=14, smooth_window=3)
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()
        # Average True Range (ATR)
        # Untuk ATR, kita perlu high, low, dan close, tapi karena data hanya memiliki 'price',
        # kita asumsikan high=low=close untuk simulasi sederhana
        atr = AverageTrueRange(high=df['price'], low=df['price'], close=df['price'], window=14)
        df['atr'] = atr.average_true_range()
        return df
    except Exception as e:
        logging.error(f"Error calculating indicators: {e}")
        return df

def save_market_data(asset, price, volume, rsi, macd, bb_upper, bb_lower, vwap, stoch_k, stoch_d, atr):
    """Menyimpan data pasar ke database."""
    try:
        conn = sqlite3.connect('data/trading_data.db')
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO market_data (timestamp, asset, price, volume, rsi, macd, bb_upper, bb_lower, vwap, stoch_k, stoch_d, atr)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), asset, price, volume, rsi, macd, bb_upper, bb_lower, vwap, stoch_k, stoch_d, atr))
        conn.commit()
        conn.close()
        logging.info(f"Saved market data for {asset}")
    except Exception as e:
        logging.error(f"Error saving market data: {e}")

def save_wallet_data(wallet):
    """Menyimpan data wallet ke database."""
    try:
        conn = sqlite3.connect('data/trading_data.db')
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO wallet_data (timestamp, wallet_address, asset, profit, loss, sharpe_ratio, win_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), wallet['wallet_address'], 'solana', 
              wallet['profit'], wallet['loss'], wallet['sharpe_ratio'], wallet['win_rate']))
        conn.commit()
        conn.close()
        logging.info(f"Saved wallet data for {wallet['wallet_address']}")
    except Exception as e:
        logging.error(f"Error saving wallet data: {e}")

def main():
    assets = ['solana', 'bitcoin', 'ethereum']
    price_history = {asset: [] for asset in assets}
    volume_history = {asset: [] for asset in assets}
    
    while True:
        for asset in assets:
            price, volume = fetch_crypto_data(asset)
            if price is None or volume is None:
                continue
            
            price_history[asset].append(price)
            volume_history[asset].append(volume)
            if len(price_history[asset]) > 50:
                price_history[asset].pop(0)
                volume_history[asset].pop(0)
            
            df = pd.DataFrame({
                'price': price_history[asset],
                'volume': volume_history[asset]
            })
            df = calculate_indicators(df)
            latest = df.iloc[-1]
            save_market_data(
                asset, 
                price, 
                volume, 
                latest['rsi'], 
                latest['macd'], 
                latest['bb_upper'], 
                latest['bb_lower'], 
                latest['vwap'], 
                latest['stoch_k'], 
                latest['stoch_d'], 
                latest['atr']
            )
        
        if int(time.time()) % 600 == 0:  # Setiap 10 menit
            wallets = fetch_gmgn_data()
            for wallet in wallets:
                save_wallet_data(wallet)
        
        time.sleep(60)  # Tunggu 1 menit sebelum pengambilan data berikutnya

if __name__ == "__main__":
    main()