import sqlite3
import os
from datetime import datetime

DB_FILE = "results.db"

nickname = os.getenv("GITHUB_ACTOR", "unknown")
exec_time = None

with open("program_output.txt", "r") as f:
    for line in f:
        if "Execution time:" in line:
            parts = line.strip().split(": ")
            if len(parts) > 1:
                exec_time_str = parts[1].split()[0]
                exec_time = float(exec_time_str)
            break

if exec_time is None:
    exec_time = 0.0

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT,
    exec_time REAL,
    timestamp TEXT
)
""")
cur.execute("""
INSERT INTO results (nickname, exec_time, timestamp)
VALUES (?, ?, ?)
""", (nickname, exec_time, datetime.utcnow().isoformat()))
conn.commit()
conn.close()

print(f"Saved result for {nickname} with time {exec_time}s")
