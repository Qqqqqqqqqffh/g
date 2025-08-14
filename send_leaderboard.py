import os
import requests

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
IMAGE_PATH = "leaderboard.png"

if not BOT_TOKEN or not CHAT_ID:
    print("Error: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID env vars not set.")
    exit(1)

def send_photo(bot_token, chat_id, photo_path):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    with open(photo_path, "rb") as photo:
        files = {"photo": photo}
        data = {"chat_id": chat_id}
        resp = requests.post(url, data=data, files=files)
    if resp.status_code == 200:
        print("Фото отправлено в Telegram")
    else:
        print(f"Ошибка отправки: {resp.status_code} {resp.text}")

if __name__ == "__main__":
    send_photo(BOT_TOKEN, CHAT_ID, IMAGE_PATH)
