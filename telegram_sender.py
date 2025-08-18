import requests
import sys
import os

def send_telegram_message(telegram_id, text, token):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": telegram_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=data)
    return response.json()

def send_telegram_document(telegram_id, document_path, caption, token):
    url = f"https://api.telegram.org/bot{token}/sendDocument"
    with open(document_path, 'rb') as f:
        files = {'document': f}
        data = {'chat_id': telegram_id, 'caption': caption}
        response = requests.post(url, files=files, data=data)
    return response.json()

if __name__ == "__main__":
    telegram_id = sys.argv[1]
    token = os.environ['TELEGRAM_BOT_TOKEN']
    yandex_server_url = os.environ['YANDEX_SERVER_URL']

    with open("description.txt", "r") as f:
        caption = f.read()

    response = send_telegram_document(telegram_id, "logs.tar.gz", caption, token)
    if response.get('ok'):
        print("Logs sent to Telegram")
    else:
        print(f"Failed to send logs: {response}")
