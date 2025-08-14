import sqlite3
import os
import requests
import base64
import sys
import time
import subprocess
from datetime import datetime

# Настройки
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
DB_FILE = "results.db"
GITHUB_DB_PATH = "results.db"

def download_db():
    """Загружает базу данных с GitHub"""
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
                print("✅ База данных загружена с GitHub")
                return True
        print("ℹ️ База данных не найдена на GitHub, создаём новую")
        return False
    except Exception as e:
        print(f"⚠️ Ошибка при загрузке базы данных: {str(e)}")
        return False

def upload_db():
    """Загружает базу данных на GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_DB_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # Проверяем существование файла
    sha = None
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            sha = response.json().get("sha")
    except:
        pass
    
    # Читаем содержимое БД
    try:
        with open(DB_FILE, "rb") as f:
            content = base64.b64encode(f.read()).decode()
    except Exception as e:
        print(f"⚠️ Ошибка чтения файла БД: {str(e)}")
        return False
    
    data = {
        "message": "Обновление базы данных через GitHub Action",
        "content": content,
        "sha": sha
    }
    
    try:
        response = requests.put(url, json=data, headers=headers)
        if response.status_code in (200, 201):
            print("✅ База данных загружена на GitHub")
            return True
        print(f"⚠️ Не удалось загрузить базу данных: {response.status_code} - {response.text}")
        return False
    except Exception as e:
        print(f"⚠️ Ошибка при загрузке базы данных: {str(e)}")
        return False

def run_and_measure():
    """Запускает программу и измеряет время выполнения с высокой точностью"""
    try:
        # Начало измерения времени
        start_time = time.perf_counter_ns()
        
        # Запуск программы
        result = subprocess.run(["./main"], capture_output=True, text=True)
        
        # Конец измерения времени
        end_time = time.perf_counter_ns()
        
        # Рассчет времени выполнения в микросекундах
        exec_time_ns = end_time - start_time
        exec_time = exec_time_ns / 1000.0  # наносекунды -> микросекунды
        
        # Сохраняем вывод программы
        with open("run_stdout.log", "w") as f:
            f.write(result.stdout)
        with open("run_stderr.log", "w") as f:
            f.write(result.stderr)
            
        print(f"ℹ️ Время выполнения: {exec_time:.3f} μs")
        return exec_time
    except Exception as e:
        print(f"⚠️ Ошибка при запуске программы: {str(e)}")
        return 0.0

def main():
    nickname = os.getenv("GITHUB_ACTOR", "unknown")
    
    # Запускаем программу и измеряем время
    exec_time = run_and_measure()

    # Скачиваем БД или создаем новую
    if not download_db():
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        # Создаем таблицы с правильными типами данных
        cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT NOT NULL,
            exec_time REAL NOT NULL,  -- REAL для микросекунд
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS user_prefs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE NOT NULL,
            color TEXT,
            telegram_id INTEGER
        )
        """)
        
        conn.commit()
        conn.close()
        print("ℹ️ Создана новая база данных")

    # Добавляем результат
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    
    # Проверяем наличие пользователя в user_prefs
    cur.execute("SELECT id FROM user_prefs WHERE nickname = ?", (nickname,))
    if not cur.fetchone():
        # Добавляем нового пользователя
        cur.execute("""
        INSERT INTO user_prefs (nickname)
        VALUES (?)
        """, (nickname,))
        print(f"ℹ️ Добавлен новый пользователь: {nickname}")
    
    # Добавляем результат выполнения
    timestamp = datetime.utcnow().isoformat()
    cur.execute("""
    INSERT INTO results (nickname, exec_time, timestamp)
    VALUES (?, ?, ?)
    """, (nickname, exec_time, timestamp))
    
    conn.commit()
    conn.close()
    print(f"✅ Результат сохранен: {nickname} - {exec_time:.3f} μs")

    # Загружаем обновлённую БД
    if not upload_db():
        print("⚠️ Не удалось загрузить обновленную базу данных")

if __name__ == "__main__":
    main()
