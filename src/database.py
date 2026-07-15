import os
import sqlite3
from pathlib import Path
import sys


def get_app_dir():
    if getattr(sys, "frozen", False):
        # Запущено из EXE
        return os.path.dirname(sys.executable)

    # Запущено из Python
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = Path(__file__).resolve().parent.parent
DB_NAME = os.path.join(get_app_dir(), "relay.db")

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS buttons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ip TEXT NOT NULL,
            relay INTEGER NOT NULL,
            password TEXT DEFAULT '0',
            pulse_sec INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY CHECK(id=1),
            theme TEXT DEFAULT 'light',
            refresh_interval INTEGER DEFAULT 5,
            timeout INTEGER DEFAULT 2,
            notifications INTEGER DEFAULT 1
        )
    """)
    conn.execute("INSERT OR IGNORE INTO settings (id) VALUES(1)")
    conn.commit()
    conn.close()
    print("Database:", DB_NAME)