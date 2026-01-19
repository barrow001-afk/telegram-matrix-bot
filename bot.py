import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters
)
from config import TOKEN, ADMIN_ID, ENERGY_MEANINGS

BIRTHDATE = 1


def calculate_energy(date_str: str) -> int:
    digits = [int(d) for d in date_str if d.isdigit()]
    total = sum(digits)
    while total > 22:
        total = sum(map(int, str(total)))
    return total


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🔮 Мини-разбор"], ["💼 Услуги"]]
    await update.message.reply_text(
        "Привет 🤍\n\n"
        "Я помогу рассчитать твою энергию по дате рождения.\n\n"
        "Выбери действие 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def mini_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введи дату рождения в формате:\nДД.ММ.ГГГГ"
    )
    return BIRTHDATE


async def process_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    date = update.message.text.strip()

    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date):
        await update.message.reply_text("❌ Формат неверный. Пример: 12.03.1995")
        return BIRTHDATE

    energy = calculate_energy(date)
    meaning = ENERGY_MEANINGS.get(energy, "Требует индивидуального разбора.")

    await update.message.reply_text(
        f"✨ Твоя энергия: *{energy}*\n\n{meaning}",
        parse_mode="Markdown"
    )

    return ConversationHandler.END


async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💼 Услуги:\n\n"
        "— Личная матрица\n"
        "— Матрица совместимости\n"
        "— Детская матрица\n\n"
        "Напиши, что тебя интересует 👇"
    )


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    mini_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔮"), mini_start)],
        states={
            BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_birthdate)]
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(mini_conv)
    app.add_handler(MessageHandler(filters.Regex("^💼"), services))

    app.run_polling()


if __name__ == "__main__":
    main()