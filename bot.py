from config import TOKEN, ADMIN_ID, WELCOME_TEXT, ENERGY_MEANINGS
import re
from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, ConversationHandler, filters
)


TOKEN = "8582895684:AAFX1JH2DrRNCuUbEMmJF5T-prWl3NZXIEg"
ADMIN_ID = 846008896
VIDEO_NOTE_ID = "AgADcZkAApdcEUs"

NAME, PHONE, COMMENT, BIRTHDATE = range(4)


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

ENERGY_MEANINGS = {
    1: "Энергия инициативы и начала.",
    2: "Энергия партнёрства и чувств.",
    3: "Энергия творчества.",
    4: "Энергия структуры и опоры.",
    5: "Энергия свободы.",
    6: "Энергия выбора и любви.",
    7: "Энергия поиска смысла.",
    8: "Энергия баланса.",
    9: "Энергия мудрости.",
    10: "Энергия перемен.",
    11: "Энергия внутренней силы.",
    12: "Энергия паузы.",
    13: "Энергия трансформации.",
    14: "Энергия умеренности.",
    15: "Энергия материального.",
    16: "Энергия резких изменений.",
    17: "Энергия вдохновения.",
    18: "Энергия интуиции.",
    19: "Энергия радости.",
    20: "Энергия пробуждения.",
    21: "Энергия завершения.",
    22: "Энергия свободы."
}


def calculate_energy(date_str: str) -> int:
    if not re.match(r"^\d{2}\.\d{2}\.\d{4}$", date_str):
        raise ValueError

    digits = [int(d) for d in date_str if d.isdigit()]
    total = sum(digits)

    while total > 22:
        total = sum(int(d) for d in str(total))

    return total


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # if not context.user_data.get("video_shown"):
#     await context.bot.send_video_note(
#         chat_id=chat_id,
#         video_note=VIDEO_NOTE_ID
#     )
#     context.user_data["video_shown"] = True

    keyboard = [
        ["🔮 Мини-разбор по дате рождения"],
        ["💼 Услуги"]
    ]

    await update.message.reply_text(
        "Привет 🤍\n\n"
        "Здесь ты можешь получить мини-разбор по дате рождения\n"
        "или выбрать персональные матрицы.\n\n"
        "Выбери, с чего начнём 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def mini_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Напиши дату рождения в формате:\nДД.ММ.ГГГГ",
        reply_markup=ReplyKeyboardMarkup([["❌ Отмена"]], resize_keyboard=True)
    )
    return BIRTHDATE

async def process_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    birthdate = update.message.text.strip()

    digits = [int(d) for d in birthdate if d.isdigit()]
    if len(digits) != 8:
        await update.message.reply_text("Введите дату в формате ДД.ММ.ГГГГ")
        return BIRTHDATE

    base_sum = sum(digits)

    if base_sum > 22:
        energy = sum(int(d) for d in str(base_sum))
    else:
        energy = base_sum

    meaning = ENERGY_MEANINGS.get(
        energy,
        "Эта энергия требует индивидуального разбора."
    )

    await update.message.reply_text(
        f"✨ Ваша энергия судьбы: *{energy}*\n\n{meaning}",
        parse_mode="Markdown"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 Отправить заявку", callback_data="order")]
    ])

    await update.message.reply_text(
        "Если хочешь полный разбор — оставь заявку 👇",
        reply_markup=keyboard
    )

    return ConversationHandler.END

    meaning = ENERGY_MEANINGS.get(energy)

    await update.message.reply_text(
        f"Твоя основная энергия — *{energy}*\n\n"
        f"{meaning}\n\n"
        "В полном разборе я подробно объясняю,\n"
        "как проживать эту энергию в плюсе.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
[InlineKeyboardButton("📖 Полный разбор", callback_data="service_1")],
            [InlineKeyboardButton("💼 Все услуги", callback_data="services")]
        ])
    )

    context.job_queue.run_once(follow_24, 86400, chat_id=update.effective_chat.id)
    context.job_queue.run_once(follow_48, 172800, chat_id=update.effective_chat.id)

    return ConversationHandler.END

async def follow_24(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        context.job.chat_id,
        "Напоминаю 🤍 Ты можешь вернуться к полному разбору.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 Полный разбор", callback_data="service_1")]
        ])
    )

async def follow_48(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        context.job.chat_id,
        "Если чувствуешь отклик — я рядом 🤍",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💼 Услуги", callback_data="services")]
        ])
    )


async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(v["title"], callback_data=k)] for k, v in SERVICES.items()]
    await update.message.reply_text("Выберите услугу:", reply_markup=InlineKeyboardMarkup(keyboard))

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
    text = (
        f"📩 Новая заявка\n\n"
        f"{context.user_data['title']}\n"
        f"{context.user_data['price']}\n\n"
        f"{context.user_data['name']}\n"
        f"{context.user_data['phone']}\n"
        f"{update.message.text}"
    )

    await context.bot.send_message(ADMIN_ID, text)
    await update.message.reply_text("✅ Заявка отправлена!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    mini_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔮"), mini_start)],
        states={
            BIRTHDATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_birthdate)
            ]
        },
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
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(mini_conv)
    app.add_handler(MessageHandler(filters.Regex("^💼 Услуги$"), show_services))
    app.add_handler(CallbackQueryHandler(show_service_card, pattern="^service_"))
    app.add_handler(order_conv)

    app.run_polling()

if __name__ == "__main__":

    main()
