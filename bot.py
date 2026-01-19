import re
import logging
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# ================= НАСТРОЙКИ =================

TOKEN = "8582895684:AAFX1JH2DrRNCuUbEMmJF5T-prWl3NZXIEg"
ADMIN_ID = 846008896

logging.basicConfig(level=logging.INFO)

NAME, PHONE, COMMENT, BIRTHDATE = range(4)

# ================= ДАННЫЕ =================

ENERGY_MEANINGS = {
    1: "Энергия инициативы и начала.",
    2: "Энергия партнёрства и чувств.",
    3: "Энергия творчества.",
    4: "Энергия структуры и опоры.",
    5: "Энергия свободы.",
    6: "Энергия любви и выбора.",
    7: "Энергия поиска смысла.",
    8: "Энергия баланса.",
    9: "Энергия мудрости.",
    10: "Энергия перемен.",
    11: "Энергия силы.",
    12: "Энергия паузы.",
    13: "Энергия трансформации.",
    14: "Энергия умеренности.",
    15: "Энергия материального.",
    16: "Энергия кризиса.",
    17: "Энергия вдохновения.",
    18: "Энергия интуиции.",
    19: "Энергия радости.",
    20: "Энергия пробуждения.",
    21: "Энергия завершения.",
    22: "Энергия свободы.",
}

# ================= ВСПОМОГАТЕЛЬНОЕ =================

def calculate_energy(date: str) -> int:
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date):
        raise ValueError
    digits = [int(d) for d in date if d.isdigit()]
    total = sum(digits)
    while total > 22:
        total = sum(map(int, str(total)))
    return total

# ================= ХЭНДЛЕРЫ =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔮 Мини-разбор"],
        ["💼 Услуги"],
    ]
    await update.message.reply_text(
        "Привет 🤍\n\nВыбери действие 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )

# ---------- Мини-разбор ----------

async def mini_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите дату рождения в формате ДД.ММ.ГГГГ",
        reply_markup=ReplyKeyboardMarkup([["❌ Отмена"]], resize_keyboard=True),
    )
    return BIRTHDATE

async def process_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        energy = calculate_energy(update.message.text.strip())
    except ValueError:
        await update.message.reply_text("Неверный формат. Пример: 01.01.1990")
        return BIRTHDATE

    meaning = ENERGY_MEANINGS.get(energy, "Энергия требует индивидуального разбора.")

    await update.message.reply_text(
        f"✨ Ваша энергия: *{energy}*\n\n{meaning}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📩 Оставить заявку", callback_data="order")]]
        ),
    )
    return ConversationHandler.END

# ---------- Заявка ----------

async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Как вас зовут?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        "Введите номер телефона",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📞 Отправить номер", request_contact=True)]],
            resize_keyboard=True,
        ),
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = (
        update.message.contact.phone_number
        if update.message.contact
        else update.message.text
    )
    await update.message.reply_text("Комментарий:")
    return COMMENT

async def get_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📩 Новая заявка\n\n"
        f"Имя: {context.user_data['name']}\n"
        f"Телефон: {context.user_data['phone']}\n"
        f"Комментарий: {update.message.text}"
    )
    await context.bot.send_message(ADMIN_ID, text)
    await update.message.reply_text(
        "✅ Заявка отправлена!",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

# ================= MAIN =================

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    mini_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔮"), mini_start)],
        states={BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_birthdate)]},
        fallbacks=[],
    )

    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(order_start, pattern="^order$")],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ],
            COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_comment)],
        },
        fallbacks=[],
    )

    app.add_handler(mini_conv)
    app.add_handler(order_conv)

    app.run_polling()

if __name__ == "__main__":
    main()