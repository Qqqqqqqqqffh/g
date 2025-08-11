import os
import sqlite3
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

DB_FILE = "results.db"
OUTPUT_IMAGE = "leaderboard.png"
AVATAR_FOLDER = "avatars"
DEFAULT_AVATAR = "default.png"

TITLE = "Таблица лидеров"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE_TITLE = 36
FONT_SIZE_TEXT = 24
TABLE_LIMIT = 10
GOLD_COLOR = (255, 215, 0)

AVATAR_SIZE = 32  # размер аватарки в пикселях

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

def load_avatar(nickname):
    """Загружает аватарку по нику или заглушку."""
    avatar_path = os.path.join(AVATAR_FOLDER, f"{nickname}.png")
    if not os.path.exists(avatar_path):
        avatar_path = os.path.join(AVATAR_FOLDER, DEFAULT_AVATAR)
    try:
        avatar = Image.open(avatar_path).convert("RGBA")
        avatar = avatar.resize((AVATAR_SIZE, AVATAR_SIZE))
    except Exception:
        avatar = Image.new("RGBA", (AVATAR_SIZE, AVATAR_SIZE), (200, 200, 200, 255))
    return avatar

def generate_image(leaderboard):
    width = 600
    row_height = 50  # увеличили, чтобы вместить аватарку
    height = 150 + len(leaderboard) * row_height

    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    font_title = ImageFont.truetype(FONT_PATH, FONT_SIZE_TITLE)
    font_text = ImageFont.truetype(FONT_PATH, FONT_SIZE_TEXT)

    draw.text((width // 2, 20), TITLE, font=font_title, fill="black", anchor="mm")

    now_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    draw.text((width // 2, 70), f"Обновлено: {now_str}", font=font_text, fill="gray", anchor="mm")

    y = 120
    for i, (nickname, best_time) in enumerate(leaderboard, start=1):
        microseconds = best_time * 1_000_000
        color = GOLD_COLOR if i == 1 else "black"

        avatar = load_avatar(nickname)
        img.paste(avatar, (10, y - 8), avatar)  
        draw.text((50 + AVATAR_SIZE + 10, y), f"{i}. {nickname}", font=font_text, fill=color)
        draw.text((width - 50, y), f"{microseconds:.3f} μс", font=font_text, fill=color, anchor="rm")

        y += row_height

    img.save(OUTPUT_IMAGE)
    print(f"✅ Картинка сохранена: {OUTPUT_IMAGE}")

if __name__ == "__main__":
    leaderboard = get_leaderboard()
    generate_image(leaderboard)
