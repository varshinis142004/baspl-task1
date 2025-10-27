from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import hashlib
import re
import os

# Serve frontend static files from ../frontend
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'front')

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Simple email validator
def is_valid_email(email: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

@app.route('/')
def index():
    # Serve your form page (SignUp_LogIn_Form.html)
    return send_from_directory(FRONTEND_DIR, 'SignUp_LogIn_Form.html')

@app.route('/dashboard.html')
def dashboard():
    # Serve dashboard placeholder
    return send_from_directory(FRONTEND_DIR, 'dashboard.html')

@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''

    # Server-side validation
    if not username or not email or not password:
        return jsonify({'success': False, 'error': 'All fields are required.'}), 400
    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters.'}), 400
    if not is_valid_email(email):
        return jsonify({'success': False, 'error': 'Invalid email format.'}), 400

    hashed = hash_password(password)
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'error': 'Username already taken.'}), 400

    conn.close()
    return jsonify({'success': True}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    password = data.get('password') or ''

    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password are required.'}), 400

    hashed = hash_password(password)
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users WHERE username=? AND password=?", (username, hashed))
    row = cur.fetchone()
    conn.close()

    if row:
        # For Task 1 we just return success; later you can add sessions/tokens if needed
        return jsonify({'success': True, 'username': row['username']})
    else:
        return jsonify({'success': False, 'error': 'Invalid username or password.'}), 401

if __name__ == '__main__':
    init_db()
    # debug=True helpful while developing; set to False in production
    app.run(host='127.0.0.1', port=5000, debug=True)
