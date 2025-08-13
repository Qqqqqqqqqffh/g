import sqlite3
import requests
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

DB_FILE = "results.db"
OUTPUT_IMAGE = "leaderboard.png"

TITLE = "Таблица лидеров"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE_TITLE = 36
FONT_SIZE_TEXT = 24
TABLE_LIMIT = 10
GOLD_COLOR = (255, 215, 0)
AVATAR_SIZE = 40
DEFAULT_COLOR = (0, 0, 0)  # Черный цвет по умолчанию

# Ссылка на RAW файлы в GitHub
GITHUB_AVATAR_URL = "https://raw.githubusercontent.com/Qqqqqqqqqffh/g/main/avatars/"

def get_user_color(nickname):
    """Получает цвет пользователя из базы данных"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT color FROM user_prefs WHERE nickname = ?", (nickname,))
        result = cur.fetchone()
        conn.close()
        
        if result and result[0]:
            # Преобразуем HEX в RGB
            hex_color = result[0].lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return DEFAULT_COLOR
    except sqlite3.Error as e:
        print(f"⚠ Ошибка при получении цвета: {e}")
        return DEFAULT_COLOR

def get_leaderboard():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        SELECT nickname, MIN(exec_time) as best_time
        FROM results
        GROUP BY nickname
        ORDER BY best_time ASC
        LIMIT ?
    """, (TABLE_LIMIT,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_avatar(nickname):
    """Пытается скачать аватарку PNG или JPG. Возвращает Image или None."""
    for ext in ["png", "jpg", "jpeg"]:
        url = f"{GITHUB_AVATAR_URL}{nickname}.{ext}"
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content)).convert("RGBA")
                img = img.resize((AVATAR_SIZE, AVATAR_SIZE), Image.LANCZOS)
                return img
        except Exception:
            pass
    return None

def generate_image(leaderboard):
    width = 600
    row_height = AVATAR_SIZE + 10
    height = 150 + len(leaderboard) * row_height

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    font_title = ImageFont.truetype(FONT_PATH, FONT_SIZE_TITLE)
    font_text = ImageFont.truetype(FONT_PATH, FONT_SIZE_TEXT)

    # Заголовок
    draw.text((width // 2, 20), TITLE, font=font_title, fill="black", anchor="mm")

    # Время обновления
    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    draw.text((width // 2, 70), f"Обновлено: {now_str}", font=font_text, fill="gray", anchor="mm")

    y = 120
    for i, (nickname, best_time) in enumerate(leaderboard, start=1):
        microseconds = best_time * 1_000_000
        
        # Получаем цвет из базы данных
        color = get_user_color(nickname)

        # Загружаем аватарку
        avatar = get_avatar(nickname)
        x_offset = 50

        if avatar:
            img.paste(avatar, (x_offset, y), avatar)
            x_offset += AVATAR_SIZE + 10  # смещение для текста

        draw.text((x_offset, y + AVATAR_SIZE // 2), f"{i}. {nickname}", font=font_text, fill=color, anchor="lm")
        draw.text((width - 50, y + AVATAR_SIZE // 2), f"{microseconds:.3f} μс", font=font_text, fill="black", anchor="rm")

        y += row_height

    img.save(OUTPUT_IMAGE)
    print(f"✅ Картинка сохранена: {OUTPUT_IMAGE}")

if __name__ == "__main__":
    leaderboard = get_leaderboard()
    generate_image(leaderboard)
