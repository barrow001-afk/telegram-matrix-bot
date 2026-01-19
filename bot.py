import os
import re
from fastapi import FastAPI
from threading import Thread
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, ConversationHandler, filters

TOKEN = os.environ.get("TOKEN", "ВАШ_ТОКЕН_ЗДЕСЬ")
ADMIN_ID = int(os.environ.get("ADMIN_ID", 123456789))

VIDEO_NOTE_ID = "AgADcZkAApdcEUs"

NAME, PHONE, COMMENT, BIRTHDATE = range(4)

SERVICES = {
    "service_1": {"title": "Личная матрица", "price": "6 000₽ / 8 000₽", "description": "✔️ Текст\n✔️ Текст + аудио", "photo": "service1.jpg"},
    "service_2": {"title": "Матрица совместимости", "price": "4 000₽ / 5 000₽", "description": "✔️ Текст\n✔️ Текст + аудио", "photo": "service2.jpg"},
    "service_3": {"title": "Детская матрица", "price": "4 000₽ / 5 000₽", "description": "✔️ Текст\n✔️ Текст + аудио", "photo": "service3.jpg"},
    "service_4": {"title": "Прогноз на 2026", "price": "4 990₽", "description": "✔️ Текст + аудио", "photo": "service4.jpg"}
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
    digits = [int(d) for d in date_str if d.isdigit()]
    total = sum(digits)
    while total > 22:
        total = sum(int(d) for d in str(total))
    return total

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🔮 Мини-разбор"], ["💼 Услуги"]]
    await update.message.reply_text(
        "Привет 🤍\nВыбери, с чего начнём 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def mini_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напиши дату рождения ДД.ММ.ГГГГ", reply_markup=ReplyKeyboardMarkup([["❌ Отмена"]], resize_keyboard=True))
    return BIRTHDATE

async def process_birthdate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    birthdate = update.message.text.strip()
    digits = [int(d) for d in birthdate if d.isdigit()]
    if len(digits) != 8:
        await update.message.reply_text("Введите корректно ДД.ММ.ГГГГ")
        return BIRTHDATE
    energy = calculate_energy(birthdate)
    meaning = ENERGY_MEANINGS.get(energy, "Индивидуальный разбор")
    await update.message.reply_text(f"✨ Энергия судьбы: *{energy}*\n{meaning}", parse_mode="Markdown")
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📩 Оставить заявку", callback_data="order")]])
    await update.message.reply_text("Для полного разбора оставь заявку 👇", reply_markup=keyboard)
    return ConversationHandler.END

async def show_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(v["title"], callback_data=k)] for k,v in SERVICES.items()]
    await update.message.reply_text("Выберите услугу:", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_service_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    service = SERVICES[query.data]
    context.user_data.update(service)
    with open(service["photo"], "rb") as photo:
        await query.message.reply_photo(photo=photo, caption=f"*{service['title']}*\n\n{service['description']}\n💰 {service['price']}", parse_mode="Markdown",
                                       reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📩 Оставить заявку", callback_data="order")]]))

async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text("Как вас зовут?")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Введите телефон:", reply_markup=ReplyKeyboardMarkup([[KeyboardButton("📞 Отправить номер", request_contact=True)]], resize_keyboard=True))
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.contact.phone_number if update.message.contact else update.message.text
    await update.message.reply_text("Комментарий:")
    return COMMENT

async def get_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = f"📩 Новая заявка\n\n{context.user_data['title']}\n{context.user_data['price']}\n\n{context.user_data['name']}\n{context.user_data['phone']}\n{update.message.text}"
    await context.bot.send_message(ADMIN_ID, text)
    await update.message.reply_text("✅ Заявка отправлена!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Bot is running"}

def run_bot():
    bot_app = ApplicationBuilder().token(TOKEN).build()

    mini_conv = ConversationHandler(entry_points=[MessageHandler(filters.Regex("^🔮"), mini_start)],
                                    states={BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_birthdate)]},
                                    fallbacks=[])
    order_conv = ConversationHandler(entry_points=[CallbackQueryHandler(order_start, pattern="^order$")],
                                     states={NAME:[MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
                                             PHONE:[MessageHandler(filters.CONTACT, get_phone),
                                                    MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
                                             COMMENT:[MessageHandler(filters.TEXT & ~filters.COMMAND, get_comment)]},
                                     fallbacks=[])

    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(mini_conv)
    bot_app.add_handler(MessageHandler(filters.Regex("^💼"), show_services))
    bot_app.add_handler(CallbackQueryHandler(show_service_card, pattern="^service_"))
    bot_app.add_handler(order_conv)
    bot_app.run_polling()

Thread(target=run_bot).start()