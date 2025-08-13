import sqlite3
import os
import requests
import base64
from datetime import datetime

# Настройки
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
DB_FILE = "results.db"
GITHUB_DB_PATH = "results.db"

# Функция для работы с GitHub DB
def download_db():
    """Загружает БД с GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_DB_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            content = response.json().get("content", "")
            if content:
                # Декодируем base64
                db_content = base64.b64decode(content)
                with open(DB_FILE, "wb") as f:
                    f.write(db_content)
                print("Database downloaded from GitHub")
                return True
        print("Database not found on GitHub, creating new")
        return False
    except Exception as e:
        print(f"Error downloading DB: {str(e)}")
        return False

def upload_db():
    """Загружает БД на GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_DB_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Проверяем существование файла
    sha = None
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json().get("sha")
    
    # Читаем содержимое БД
    with open(DB_FILE, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    
    data = {
        "message": "Update database from GitHub Action",
        "content": content,
        "sha": sha
    }
    
    try:
        response = requests.put(url, json=data, headers=headers)
        if response.status_code in (200, 201):
            print("Database uploaded to GitHub")
            return True
        print(f"Failed to upload DB: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        print(f"Error uploading DB: {str(e)}")
        return False

# Основной код
def main():
    nickname = os.getenv("GITHUB_ACTOR", "unknown")
    exec_time = None

    # Читаем время выполнения из файла
    try:
        with open("program_output.txt", "r") as f:
            for line in f:
                if "Execution time:" in line:
                    parts = line.strip().split(": ")
                    if len(parts) > 1:
                        exec_time_str = parts[1].split()[0]
                        exec_time = float(exec_time_str)
                    break
    except Exception as e:
        print(f"Error reading output file: {str(e)}")
        exec_time = 0.0

    if exec_time is None:
        exec_time = 0.0

    # Скачиваем БД
    if not download_db():
        # Если не удалось скачать, создаем новую
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
        conn.commit()
        conn.close()
        print("Created new database")

    # Добавляем результат
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO results (nickname, exec_time, timestamp)
    VALUES (?, ?, ?)
    """, (nickname, exec_time, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    print(f"Saved result for {nickname} with time {exec_time}s")

    # Загружаем обновленную БД
    if not upload_db():
        print("Failed to upload updated database")

if __name__ == "__main__":
    main()
