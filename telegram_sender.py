import sys
import os
import requests

def send_telegram_message(telegram_id):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print(" TELEGRAM_BOT_TOKEN not set")
        return False

    with open("description.txt", "r") as f:
        description = f.read()

    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    files = {
        "document": ("logs.tar.gz", open("logs.tar.gz", "rb"))
    }
    data = {
        "chat_id": telegram_id,
        "caption": description,
        "disable_notification": False
    }
    
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print(f"Logs sent to Telegram user {telegram_id}")
            return True
        else:
            print(f"Failed to send logs: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error sending to Telegram: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python telegram_sender.py <telegram_id>")
        sys.exit(1)
    
    telegram_id = sys.argv[1]
    send_telegram_message(telegram_id)
