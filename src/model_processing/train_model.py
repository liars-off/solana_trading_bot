import numpy as np
import tensorflow as tf
from tensorflow.keras import layers
from src.model_processing.environment import TradingEnvironment
import logging

# Setup logging
logging.basicConfig(filename='model_training_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def build_model(state_size, action_size):
    """Membangun model DQN."""
    model = tf.keras.Sequential([
        layers.Dense(64, activation='relu', input_shape=(state_size,)),
        layers.Dense(64, activation='relu'),
        layers.Dense(action_size, activation='linear')
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss='mse')
    return model

def train_dqn(env, episodes=100):
    """Melatih model DQN."""
    state_size = env.observation_space.shape[0]  # 10, sesuai dengan state baru
    action_size = env.action_space.n  # 3 (Buy, Hold, Sell)
    model = build_model(state_size, action_size)
    gamma = 0.95  # Discount factor
    epsilon = 1.0  # Exploration rate
    epsilon_min = 0.01
    epsilon_decay = 0.995
    batch_size = 32
    memory = []  # Replay memory

    for episode in range(episodes):
        state = env.reset()
        state = np.reshape(state, [1, state_size])
        total_reward = 0

        for time in range(100):
            # Pilih aksi (exploration atau exploitation)
            if np.random.rand() <= epsilon:
                action = env.action_space.sample()
            else:
                action = np.argmax(model.predict(state, verbose=0)[0])

            # Ambil langkah
            next_state, reward, done, _ = env.step(action)
            next_state = np.reshape(next_state, [1, state_size])
            memory.append((state, action, reward, next_state, done))
            state = next_state
            total_reward += reward

            # Replay training jika memori cukup
            if len(memory) > batch_size:
                batch = np.random.choice(len(memory), batch_size, replace=False)
                states = np.vstack([memory[i][0] for i in batch])
                actions = np.array([memory[i][1] for i in batch])
                rewards = np.array([memory[i][2] for i in batch])
                next_states = np.vstack([memory[i][3] for i in batch])
                dones = np.array([memory[i][4] for i in batch])

                # Hitung target Q-values
                targets = rewards + gamma * np.max(model.predict(next_states, verbose=0), axis=1) * (1 - dones)
                target_f = model.predict(states, verbose=0)
                for i in range(batch_size):
                    target_f[i][actions[i]] = targets[i]
                model.fit(states, target_f, epochs=1, verbose=0)

            if done:
                break

        # Kurangi epsilon untuk mengurangi eksplorasi
        if epsilon > epsilon_min:
            epsilon *= epsilon_decay

        logging.info(f"Episode {episode+1}/{episodes}, Total Reward: {total_reward}, Epsilon: {epsilon}")
        print(f"Episode {episode+1}/{episodes}, Total Reward: {total_reward}")

    model.save(f'dqn_trading_model_{env.asset}.h5')
    logging.info(f"Model saved as dqn_trading_model_{env.asset}.h5")
    return model

if __name__ == "__main__":
    env = TradingEnvironment(asset='solana')
    train_dqn(env, episodes=10)  # Kurangi episodes untuk testing