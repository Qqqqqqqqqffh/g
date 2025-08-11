import sqlite3
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import os

DB_FILE = "results.db"
OUTPUT_IMAGE = "leaderboard.png"
AVATARS_DIR = "avatars"  # локальная папка с аватарками

TITLE = "Таблица лидеров"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE_TITLE = 36
FONT_SIZE_TEXT = 24
TABLE_LIMIT = 10
GOLD_COLOR = (255, 215, 0)

AVATAR_SIZE = 32  # размер мини-аватарки

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

def generate_image(leaderboard):
    width = 600
    row_height = 50
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

        # Путь к аватарке
        avatar_path = os.path.join(AVATARS_DIR, f"{nickname}.png")
        if os.path.exists(avatar_path):
            avatar_img = Image.open(avatar_path).convert("RGBA")
            avatar_img = avatar_img.resize((AVATAR_SIZE, AVATAR_SIZE))
            img.paste(avatar_img, (50, y - 5), avatar_img)  # вставка с прозрачностью
            text_x = 50 + AVATAR_SIZE + 10
        else:
            text_x = 50

        # Никнейм
        draw.text((text_x, y), f"{i}. {nickname}", font=font_text, fill=color)

        # Время
        draw.text((width - 50, y), f"{microseconds:.3f} μс", font=font_text, fill=color, anchor="rm")

        y += row_height

    img.save(OUTPUT_IMAGE)
    print(f"✅ Картинка сохранена: {OUTPUT_IMAGE}")

if __name__ == "__main__":
    leaderboard = get_leaderboard()
    generate_image(leaderboard)
