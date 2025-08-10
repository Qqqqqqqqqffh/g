import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

CHOICE_FILE = "avatar_choice.json"

AVATARS = {
    "classic": "Классика",
    "dark": "Темная",
    "bright": "Яркая"
}

def load_choice():
    if os.path.exists(CHOICE_FILE):
        with open(CHOICE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_choice(data):
    with open(CHOICE_FILE, "w") as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Используй /choose_avatar для выбора стиля таблицы рекордов.")

async def choose_avatar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(v, callback_data=k)] for k, v in AVATARS.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите стиль аватарки:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data

    data = load_choice()
    user_id = str(query.from_user.id)
    data[user_id] = choice
    save_choice(data)

    await query.edit_message_text(text=f"Вы выбрали стиль: {AVATARS[choice]}")

async def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("choose_avatar", choose_avatar))
    app.add_handler(CallbackQueryHandler(button))

    print("Бот запущен")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
