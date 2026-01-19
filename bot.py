import re
from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, ConversationHandler, filters
)

from config import TOKEN, ADMIN_ID, ENERGY_MEANINGS

NAME, PHONE, COMMENT, BIRTHDATE = range(4)


# ================== УСЛУГИ ==================
SERVICES = {
    "service_1": {
        "title": "Личная матрица",
        "price": "6 000₽ / 8 000₽",
        "description": "✔️ Текстовый формат\n✔️ Текст + аудио",
        "photo": "service1.jpg"
    },
    "service_2": {
        "title": "Матрица совместимости",
        "price": "4 000₽ / 5 000₽",
        "description": "✔️ Текстовый формат\n✔️ Текст + аудио",
        "photo": "service2.jpg"
    },
    "service_3": {
        "title": "Детская матрица",
        "price": "4 000₽ / 5 000₽",
        "description": "✔️ Текстовый формат\n✔️ Текст + аудио",
        "photo": "service3.jpg"
    },
    "service_4": {
        "title": "Прогноз на 2026",
        "price": "4 990₽",
        "description": "✔️ Текст + аудио",
        "photo": "service4.jpg"
    }
}


# ================== ЛОГИКА ==================
def calculate_energy(date_str: str) -> int:
    digits = [int(d) for d in date_str if d.isdigit()]
    total = sum(digits)
    while total > 22:
        total = sum(int(d) for d in str(total))
    return total


# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🔮 Мини-разбор по дате рождения"],
        ["💼 Услуги"]
    ]
    await update.message.reply_text(
        "Привет 🤍\n\nВыбери, с чего начнём 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


# ================== МИНИ-РАЗБОР ==================
async def mini_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Введите дату рождения:\nДД.ММ.ГГГГ",
        reply_markup=ReplyKeyboardMarkup([["❌ Отмена"]], resize_keyboard=True)
    )
    return BIRTHDATE


async def process_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not re.match(r"\d{2}\.\d{2}\.\d{4}", text):
        await update.message.reply_text("Формат: ДД.ММ.ГГГГ")
        return BIRTHDATE

    energy = calculate_energy(text)
    meaning = ENERGY_MEANINGS.get(energy, "Требует индивидуального разбора")

    context.user_data["energy"] = energy

    await update.message.reply_text(
        f"✨ *Ваша энергия:* {energy}\n\n{meaning}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Оставить заявку", callback_data="order")],
            [InlineKeyboardButton("💼 Все услуги", callback_data="services")]
        ])
    )

    return ConversationHandler.END


# ================== УСЛУГИ ==================
async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(v["title"], callback_data=k)] for k, v in SERVICES.items()]
    await update.message.reply_text(
        "Выберите услугу:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_service_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    service = SERVICES[query.data]
    context.user_data.update(service)

    with open(service["photo"], "rb") as photo:
        await query.message.reply_photo(
            photo=photo,
            caption=f"*{service['title']}*\n\n{service['description']}\n\n💰 {service['price']}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📩 Оставить заявку", callback_data="order")],
                [InlineKeyboardButton("⬅️ Назад", callback_data="services")]
            ])
        )


# ================== ЗАЯВКА ==================
async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Как вас зовут?")
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text(
        "Введите номер телефона:",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📞 Отправить номер", request_contact=True)]],
            resize_keyboard=True
        )
    )
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = (
        update.message.contact.phone_number if update.message.contact else update.message.text
    )
    await update.message.reply_text("Комментарий:")
    return COMMENT


async def get_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"📩 *Новая заявка*\n\n"
        f"{context.user_data.get('title', '')}\n"
        f"{context.user_data.get('price', '')}\n\n"
        f"{context.user_data['name']}\n"
        f"{context.user_data['phone']}\n"
        f"{update.message.text}"
    )

    await context.bot.send_message(ADMIN_ID, msg, parse_mode="Markdown")
    await update.message.reply_text("✅ Заявка отправлена!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# ================== MAIN ==================
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^🔮"), mini_start)],
            states={BIRTHDATE: [MessageHandler(filters.TEXT, process_birthdate)]},
            fallbacks=[]
        )
    )

    app.add_handler(MessageHandler(filters.Regex("^💼 Услуги$"), show_services))
    app.add_handler(CallbackQueryHandler(show_service_card, pattern="^service_"))
    app.add_handler(CallbackQueryHandler(show_services, pattern="^services$"))

    app.add_handler(
        ConversationHandler(
            entry_points=[CallbackQueryHandler(order_start, pattern="^order$")],
            states={
                NAME: [MessageHandler(filters.TEXT, get_name)],
                PHONE: [MessageHandler(filters.ALL, get_phone)],
                COMMENT: [MessageHandler(filters.TEXT, get_comment)],
            },
            fallbacks=[]
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()