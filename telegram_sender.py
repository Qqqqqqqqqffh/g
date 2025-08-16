import sys
import os
import requests
import json

def send_telegram_message(telegram_id):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    server_url = os.getenv("YANDEX_SERVER_URL")
    
    if not bot_token or not server_url:
        print("⚠️ Missing environment variables")
        return False
    
    # Читаем описание
    with open("description.txt", "r") as f:
        description = f.read()
    
    # Отправляем запрос на сервер Яндекса
    url = f"{server_url}/send_logs"
    data = {
        "telegram_id": int(telegram_id),
        "caption": description
    }
    files = {
        "archive": open("logs.tar.gz", "rb")
    }
    
    try:
        response = requests.post(url, data=data, files=files)
        if response.status_code == 200:
            print(f"✅ Logs sent via Yandex server to user {telegram_id}")
            return True
        else:
            print(f"⚠️ Failed to send logs: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"⚠️ Error sending to Yandex server: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚠️ Usage: python telegram_sender.py <telegram_id>")
        sys.exit(1)
    
    telegram_id = sys.argv[1]
    send_telegram_message(telegram_id)
