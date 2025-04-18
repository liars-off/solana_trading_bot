import numpy as np
import gym
from gym import spaces
import sqlite3
import pandas as pd
import logging

# Setup logging
logging.basicConfig(filename='model_training_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class TradingEnvironment(gym.Env):
    def __init__(self, asset='solana'):
        super(TradingEnvironment, self).__init__()
        self.asset = asset
        self.action_space = spaces.Discrete(3)  # Buy, Hold, Sell
        # State sekarang mencakup price, volume, rsi, macd, bb_upper, bb_lower, vwap, stoch_k, stoch_d, atr
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(10,), dtype=np.float32)
        self.reset()

    def fetch_state(self):
        """Mengambil state terbaru dari database."""
        try:
            conn = sqlite3.connect('data/trading_data.db')
            query = f"""
            SELECT price, volume, rsi, macd, bb_upper, bb_lower, vwap, stoch_k, stoch_d, atr 
            FROM market_data 
            WHERE asset = '{self.asset}' 
            ORDER BY timestamp DESC 
            LIMIT 1
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            if df.empty:
                logging.warning(f"No data found for {self.asset} in market_data")
                return np.zeros(10)
            return df.iloc[0][['price', 'volume', 'rsi', 'macd', 'bb_upper', 'bb_lower', 'vwap', 'stoch_k', 'stoch_d', 'atr']].values
        except Exception as e:
            logging.error(f"Error fetching state: {e}")
            return np.zeros(10)

    def reset(self):
        """Mengatur ulang lingkungan."""
        self.balance = 10000.0  # Saldo awal
        self.position = 0.0  # Posisi awal (jumlah aset yang dimiliki)
        self.step_count = 0
        self.state = self.fetch_state()
        return self.state

    def step(self, action):
        """Melakukan langkah dalam lingkungan."""
        self.step_count += 1
        price = self.state[0]  # Harga saat ini dari state
        reward = 0.0
        
        if action == 0:  # Buy
            if self.balance >= price:
                self.position += 0.01  # Beli 0.01 unit
                self.balance -= price * 0.01
                reward = 0.1  # Reward kecil untuk tindakan
        elif action == 2:  # Sell
            if self.position >= 0.01:
                self.position -= 0.01  # Jual 0.01 unit
                self.balance += price * 0.01
                reward = 0.1  # Reward kecil untuk tindakan
        
        self.state = self.fetch_state()
        done = self.balance <= 0 or self.step_count >= 100
        info = {'balance': self.balance, 'position': self.position}
        return self.state, reward, done, info

    def render(self, mode='human'):
        """Menampilkan status lingkungan."""
        print(f"Balance: ${self.balance:.2f}, Position: {self.position:.4f} {self.asset}")