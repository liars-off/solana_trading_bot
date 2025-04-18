import sqlite3
from datetime import datetime
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Setup logging
logging.basicConfig(filename='bot_log.txt', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_trade(asset, action, price, amount, order_type='market'):
    """Menyimpan perdagangan ke database."""
    try:
        conn = sqlite3.connect('data/trading_data.db')
        cursor = conn.cursor()
        profit = 0.0  # Placeholder, hitung profit di aplikasi nyata
        cursor.execute("""
        INSERT INTO trades (timestamp, action, asset, price, amount, profit, order_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), action, asset, price, amount, profit, order_type))
        conn.commit()
        conn.close()
        logging.info(f"Logged trade: {action} {amount} {asset} at ${price} ({order_type})")
    except Exception as e:
        logging.error(f"Error logging trade: {e}")

def parse_signal(message):
    """Mengurai pesan untuk sinyal perdagangan."""
    try:
        parts = message.split()
        if len(parts) < 4 or parts[0].lower() not in ['buy', 'sell']:
            return None
        action = parts[0].capitalize()
        asset = parts[1].upper()
        price = float(parts[3])
        return asset, action, price
    except Exception as e:
        logging.error(f"Error parsing signal: {e}")
        return None

async def start(update, context):
    """Menangani perintah /start."""
    keyboard = [
        [
            InlineKeyboardButton("Buy SOL 📈", callback_data='buy_sol'),
            InlineKeyboardButton("Sell SOL 📉", callback_data='sell_sol'),
        ],
        [InlineKeyboardButton("Check Market 🕒", callback_data='check_market')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Welcome to Solana Trading Bot! 🤖\nChoose an action:', reply_markup=reply_markup)

async def button_callback(update, context):
    """Menangani tombol interaktif."""
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == 'buy_sol':
        await query.message.reply_text('Enter buy price (e.g., Buy SOL at 150) 💰')
    elif data == 'sell_sol':
        await query.message.reply_text('Enter sell price (e.g., Sell SOL at 160) 💸')
    elif data == 'check_market':
        # Placeholder untuk data pasar
        conn = sqlite3.connect('data/trading_data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT price FROM market_data WHERE asset='solana' ORDER BY timestamp DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        price = result[0] if result else "N/A"
        await query.message.reply_text(f'Current SOL Price: ${price} 📊')

async def handle_message(update, context):
    """Menangani pesan sinyal."""
    message = update.message.text
    result = parse_signal(message)
    if not result:
        await update.message.reply_text('Format salah. Gunakan: "Buy SOL at 150" atau "Sell SOL at 160" ⚠️')
        return
    
    asset, action, price = result
    amount = 0.01  # Placeholder, sesuaikan dengan logika nyata
    log_trade(asset, action, price, amount)
    await update.message.reply_text(f'{action} {amount} {asset} at ${price} ✅')

async def limit_order(update, context):
    """Menangani perintah /limit untuk limit order."""
    message = ' '.join(context.args)
    result = parse_signal(message)
    if not result:
        await update.message.reply_text('Format salah. Gunakan: /limit Buy SOL at 150 ⚠️')
        return
    
    asset, action, price = result
    amount = 0.01  # Placeholder
    log_trade(asset, action, price, amount, order_type='limit')
    await update.message.reply_text(f'Limit order placed: {action} {amount} {asset} at ${price} ⏳')

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("limit", limit_order))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    logging.info("Telegram bot started")
    application.run_polling()

if __name__ == "__main__":
    main()