import numpy as np
import pandas as pd
import tensorflow as tf
from src.model_processing.environment import TradingEnvironment
import sqlite3
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(filename='model_training_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def load_model(model_path='dqn_trading_model_solana.h5'):
    """Memuat model DQN yang telah dilatih."""
    try:
        model = tf.keras.models.load_model(model_path)
        logging.info(f"Model loaded successfully from {model_path}")
        return model
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        raise

def get_latest_data(asset='solana', db_path='data/trading_data.db'):
    """Mengambil data terbaru dari database untuk inferensi."""
    try:
        conn = sqlite3.connect(db_path)
        query = f"""
        SELECT price, volume, rsi, macd, bb_upper, bb_lower, vwap, stoch_k, stoch_d, atr 
        FROM market_data 
        WHERE asset = '{asset}' 
        ORDER BY timestamp DESC 
        LIMIT 50
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        if df.empty:
            logging.warning(f"No data found for {asset}")
            return None
        return df[['price', 'volume', 'rsi', 'macd', 'bb_upper', 'bb_lower', 'vwap', 'stoch_k', 'stoch_d', 'atr']].values
    except Exception as e:
        logging.error(f"Failed to fetch data: {e}")
        return None

def predict_action(model, state):
    """Memprediksi aksi menggunakan model DQN."""
    state = np.array(state).reshape(1, -1)
    q_values = model.predict(state, verbose=0)
    action = np.argmax(q_values[0])
    action_map = {0: 'Buy', 1: 'Hold', 2: 'Sell'}
    return action_map[action]

def run_inference(asset='solana', model_path='dqn_trading_model_solana.h5'):
    """Menjalankan inferensi untuk menghasilkan sinyal perdagangan."""
    model = load_model(model_path)
    env = TradingEnvironment(asset=asset)
    state = get_latest_data(asset)
    
    if state is None:
        logging.error("No state data available for inference")
        return None
    
    action = predict_action(model, state[-1])
    price = state[-1][0]
    
    try:
        conn = sqlite3.connect('data/trading_data.db')
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO signals (timestamp, asset, action, price)
        VALUES (?, ?, ?, ?)
        """, (datetime.now().isoformat(), asset, action, price))
        conn.commit()
        conn.close()
        logging.info(f"Inference completed: {action} {asset} at ${price}")
        return {'asset': asset, 'action': action, 'price': price}
    except Exception as e:
        logging.error(f"Failed to save signal: {e}")
        return None

if __name__ == '__main__':
    result = run_inference()
    if result:
        print(f"Sinyal: {result['action']} {result['asset']} pada ${result['price']}")