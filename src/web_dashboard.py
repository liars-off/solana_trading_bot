from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_socketio import SocketIO
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import sqlite3
import pandas as pd
from datetime import datetime
from weasyprint import HTML
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
socketio = SocketIO(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    return User(username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == os.getenv('ADMIN_USERNAME'):
            from werkzeug.security import check_password_hash
            if check_password_hash(os.getenv('ADMIN_PASSWORD_HASH'), password):
                user = User(username)
                login_user(user)
                return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    conn = sqlite3.connect('data/trading_data.db')
    trades = pd.read_sql_query("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 10", conn)
    signals = pd.read_sql_query("SELECT * FROM signals ORDER BY timestamp DESC LIMIT 10", conn)
    conn.close()
    return render_template('index.html', trades=trades.to_dict('records'), signals=signals.to_dict('records'))

@app.route('/trades')
@login_required
def trades():
    period = request.args.get('period', '1d')
    asset = request.args.get('asset', 'solana')
    conn = sqlite3.connect('data/trading_data.db')
    trades = pd.read_sql_query(f"SELECT * FROM trades WHERE asset='{asset}' ORDER BY timestamp DESC", conn)
    market_data = pd.read_sql_query(f"SELECT * FROM market_data WHERE asset='{asset}' ORDER BY timestamp DESC", conn)
    conn.close()
    return render_template('trades.html', trades=trades.to_dict('records'), market_data=market_data.to_dict('records'), period=period, asset=asset)

@app.route('/model')
@login_required
def model():
    conn = sqlite3.connect('data/trading_data.db')
    signals = pd.read_sql_query("SELECT * FROM signals ORDER BY timestamp DESC LIMIT 10", conn)
    conn.close()
    return render_template('model.html', signals=signals.to_dict('records'))

@app.route('/debug')
@login_required
def debug():
    with open('bot_log.txt', 'r') as f:
        logs = f.readlines()[-50:]  # Ambil 50 baris terakhir
    return render_template('debug.html', logs=logs)

@app.route('/export/csv')
@login_required
def export_csv():
    conn = sqlite3.connect('data/trading_data.db')
    df = pd.read_sql_query("SELECT * FROM trades", conn)
    conn.close()
    csv_path = 'reports/trades_export.csv'
    df.to_csv(csv_path, index=False)
    return send_file(csv_path, as_attachment=True)

@app.route('/export/pdf')
@login_required
def export_pdf():
    conn = sqlite3.connect('data/trading_data.db')
    trades = pd.read_sql_query("SELECT * FROM trades ORDER BY timestamp DESC", conn)
    conn.close()
    html = render_template('report.html', trades=trades.to_dict('records'))
    pdf_path = 'reports/trades_report.pdf'
    HTML(string=html).write_pdf(pdf_path)
    return send_file(pdf_path, as_attachment=True)

@socketio.on('connect')
def handle_connect():
    socketio.emit('status', {'status': 'Bot connected'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)