import sqlite3

DB_PATH = "game.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT NOT NULL,
            score INTEGER NOT NULL
        )""")
    return conn
