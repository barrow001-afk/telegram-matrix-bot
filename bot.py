from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = "8582895684:AAFX1JH2DrRNCuUbEMmJF5T-prWl3NZXIEg"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🔮 Мини-разбор"], ["💼 Услуги"]]
    await update.message.reply_text(
        "Привет 🤍\nВыбери действие 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает ✅")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_polling()

if __name__ == "__main__":
    main()