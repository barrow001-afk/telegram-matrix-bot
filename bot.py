from fastapi import FastAPI
import asyncio
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from config import TOKEN  # твой токен из config.py

app = FastAPI()

# ---------------------
# Telegram bot setup
# ---------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["💼 Услуги"]]
    await update.message.reply_text(
        "Привет! Бот запущен и работает через FastAPI.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

application = ApplicationBuilder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))

# Запускаем polling в фоне
asyncio.create_task(application.run_polling())

# ---------------------
# FastAPI routes
# ---------------------
@app.get("/")
def root():
    return {"status": "Bot is running"}

# ---------------------
# Запуск сервера
# ---------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=10000)