import sys
import os
import requests
import json
from datetime import datetime

def save_result(exec_time=None):
    nickname = os.getenv("GITHUB_ACTOR", "unknown")
    server_url = os.getenv("YANDEX_SERVER_URL")
    
    if not server_url:
        print("⚠️ YANDEX_SERVER_URL not set")
        return
    
    # Обработка времени выполнения
    try:
        exec_time = float(exec_time) if exec_time else 0.0
    except ValueError:
        print("⚠️ Invalid exec_time, using 0.0")
        exec_time = 0.0
    
    # Формируем данные
    data = {
        "github_username": nickname,
        "exec_time": exec_time,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Отправляем на сервер Яндекса
    url = f"{server_url}/save_result"
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"✅ Result saved: {nickname} - {exec_time:.3f} μs")
        else:
            print(f"⚠️ Failed to save result: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ Error saving result: {str(e)}")

if __name__ == "__main__":
    exec_time_arg = sys.argv[1] if len(sys.argv) > 1 else None
    save_result(exec_time_arg)
