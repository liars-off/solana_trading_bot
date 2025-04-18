# Solana Trading Bot

A trading bot for Solana and other cryptocurrencies, featuring AI-based trading signals, a web dashboard, and Telegram integration.

## Features
- **Market Data Fetching**: Collects price, volume, and technical indicators (RSI, MACD, Bollinger Bands, VWAP, Stochastic Oscillator, ATR) for Solana, Bitcoin, and Ethereum using CoinGecko.
- **AI Trading Model**: Uses DQN (Deep Q-Network) to generate trading signals.
- **Web Dashboard**: Visualizes trades, signals, and market data with real-time charts.
- **Telegram Bot**: Sends and receives trading signals via Telegram with interactive buttons.
- **Copy Trading**: Integrates with GMGN.ai to copy trades from high-performing wallets (win rate > 75%).
- **Export Reports**: Export trade history as CSV or PDF.

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/liars-off/solana_trading_bot.git
   cd solana_trading_bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   nano .env
   ```

4. **Initialize the database**:
   ```bash
   sqlite3 data/trading_data.db < schema.sql
   ```

   **schema.sql**:
   ```sql
   CREATE TABLE market_data (
       timestamp TEXT,
       asset TEXT,
       price REAL,
       volume REAL,
       rsi REAL,
       macd REAL,
       bb_upper REAL,
       bb_lower REAL,
       vwap REAL,
       stoch_k REAL,
       stoch_d REAL,
       atr REAL
   );

   CREATE TABLE signals (
       timestamp TEXT,
       asset TEXT,
       action TEXT,
       price REAL
   );

   CREATE TABLE trades (
       timestamp TEXT,
       action TEXT,
       asset TEXT,
       price REAL,
       amount REAL,
       profit REAL,
       order_type TEXT
   );

   CREATE TABLE wallet_data (
       timestamp TEXT,
       wallet_address TEXT,
       asset TEXT,
       profit REAL,
       loss REAL,
       sharpe_ratio REAL,
       win_rate REAL
   );
   ```

5. **Run the application**:
   - Fetch market data:
     ```bash
     python src/market_data.py
     ```
   - Run Telegram bot:
     ```bash
     python src/telegram_bot.py
     ```
   - Run web dashboard:
     ```bash
     python src/web_dashboard.py
     ```
   - Train the model:
     ```bash
     python src/model_processing/train_model.py
     ```
   - Run inference:
     ```bash
     python src/model_processing/inference.py
     ```

## Usage
- **Web Dashboard**: Access at `http://localhost:5000`. Log in with the credentials set in `.env`.
- **Telegram Bot**: Add the bot using the Telegram token and send commands like `/start`, `/limit Buy SOL at 150`, or manual signals like `Buy SOL at 150`.
- **Model Signals**: Check AI-generated signals on the `/model` page of the dashboard.

## Development
- Run tests:
  ```bash
  pytest tests/
  ```
- Lint code:
  ```bash
  flake8 src/ tests/ --max-line-length=120 --exclude=src/static
  ```

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.