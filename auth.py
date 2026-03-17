from flask import session, redirect, url_for, flash
from functools import wraps
import sqlite3
import hashlib
import os
import threading

import sys

# Use persistent volume path in production (Docker), local file in dev
_db_dir = '/app/db' if os.path.isdir('/app/db') else '.'
DATABASE = os.path.join(_db_dir, 'users.db')
_db_lock = threading.Lock()

def get_db_connection():
    """Get database connection with timeout"""
    conn = sqlite3.connect(DATABASE, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrency
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def init_db():
    """Initialize the database with users table"""
    with _db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
        finally:
            conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password):
    """Create a new user"""
    with _db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            hashed_pw = hash_password(password)
            cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                          (username, email, hashed_pw))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

def verify_user(username, password):
    """Verify user credentials"""
    with _db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            hashed_pw = hash_password(password)
            cursor.execute('SELECT id, username FROM users WHERE username = ? AND password = ?',
                          (username, hashed_pw))
            user = cursor.fetchone()
            return user
        finally:
            conn.close()

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_user_folder(user_id):
    """Get user-specific folder path"""
    return os.path.join('user_uploads', str(user_id))

def get_user_reels_folder(user_id):
    """Get user-specific reels folder path"""
    return os.path.join('static', 'reels', str(user_id))

def get_user_metadata_folder(user_id):
    """Get user-specific metadata folder path"""
    return os.path.join('static', 'metadata', str(user_id))
