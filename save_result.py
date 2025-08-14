import sqlite3
import os
import sys
from datetime import datetime

DB_FILE = "results.db"

def save_result(exec_time=None):
    nickname = os.getenv("GITHUB_ACTOR", "unknown")

    try:
        exec_time = float(exec_time) if exec_time else 0.0
    except ValueError:
        print("using 0.0")
        exec_time = 0.0
    
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nickname TEXT NOT NULL,
        exec_time REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS account_bindings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
        github_username TEXT NOT NULL UNIQUE
    )
    ''')

    timestamp = datetime.utcnow().isoformat()
    cur.execute("""
    INSERT INTO results (nickname, exec_time, timestamp)
    VALUES (?, ?, ?)
    """, (nickname, exec_time, timestamp))
    
    conn.commit()
    conn.close()
    print(f"✅ Результат сохранен: {nickname} - {exec_time:.3f} μs")

if __name__ == "__main__":
    exec_time_arg = sys.argv[1] if len(sys.argv) > 1 else None
    save_result(exec_time_arg)
