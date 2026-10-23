# ==============================================================================
# HỆ THỐNG CƠ SỞ DỮ LIỆU NGƯỜI DÙNG (SQLITE AUTHENTICATION DATABASE)
# Module: database.py
# ==============================================================================

import os
import sqlite3
from flask_login import UserMixin

DB_PATH = os.path.join(os.path.dirname(__file__), 'users.db')

def get_db_connection():
    """Tạo kết nối đến SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Tự động khởi tạo bảng users và prediction_history nếu chưa tồn tại."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prediction_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            crop_name TEXT NOT NULL,
            crop_id TEXT NOT NULL,
            emoji TEXT NOT NULL,
            confidence REAL NOT NULL,
            n REAL NOT NULL,
            p REAL NOT NULL,
            k REAL NOT NULL,
            temp REAL NOT NULL,
            humidity REAL NOT NULL,
            ph REAL NOT NULL,
            rainfall REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

class User(UserMixin):
    """Lớp đối tượng Người dùng tích hợp Flask-Login UserMixin."""
    def __init__(self, id, email, password_hash):
        self.id = str(id)
        self.email = email
        self.password_hash = password_hash

def get_user_by_id(user_id):
    """Tìm người dùng theo ID (phục vụ user_loader của Flask-Login)."""
    conn = get_db_connection()
    user_row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user_row:
        return User(id=user_row['id'], email=user_row['email'], password_hash=user_row['password_hash'])
    return None

def get_user_by_email(email):
    """Tìm người dùng theo email (phục vụ đăng nhập & kiểm tra trùng lặp)."""
    conn = get_db_connection()
    user_row = conn.execute('SELECT * FROM users WHERE lower(email) = lower(?)', (email.strip(),)).fetchone()
    conn.close()
    if user_row:
        return User(id=user_row['id'], email=user_row['email'], password_hash=user_row['password_hash'])
    return None

def create_user(email, password_hash):
    """Tạo mới một tài khoản người dùng vào SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO users (email, password_hash) VALUES (?, ?)',
        (email.strip().lower(), password_hash)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def save_prediction_history(user_id, crop_name, crop_id, emoji, confidence, n, p, k, temp, humidity, ph, rainfall):
    """Lưu trữ lịch sử dự đoán của người dùng."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO prediction_history 
        (user_id, crop_name, crop_id, emoji, confidence, n, p, k, temp, humidity, ph, rainfall)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, crop_name, crop_id, emoji, confidence, n, p, k, temp, humidity, ph, rainfall))
    conn.commit()
    history_id = cursor.lastrowid
    conn.close()
    return history_id

def get_user_history(user_id, limit=30):
    """Lấy danh sách các lần dự đoán gần nhất của người dùng."""
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT id, crop_name, crop_id, emoji, confidence, n, p, k, temp, humidity, ph, rainfall,
               strftime('%d/%m/%Y %H:%M', created_at) as created_time
        FROM prediction_history 
        WHERE user_id = ? 
        ORDER BY id DESC 
        LIMIT ?
    ''', (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_user_history(history_id, user_id):
    """Xóa một mục lịch sử của người dùng."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM prediction_history WHERE id = ? AND user_id = ?', (history_id, user_id))
    conn.commit()
    conn.close()
    return True

def clear_user_history(user_id):
    """Xóa toàn bộ lịch sử của người dùng."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM prediction_history WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()
    return True

