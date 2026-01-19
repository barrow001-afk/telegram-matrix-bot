import re
from telegram import (
    Update, KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    CallbackQueryHandler, ConversationHandler, Filters
)

TOKEN = "8582895684:AAFX1JH2DrRNCuUbEMmJF5T-prWl3NZXIEg"
ADMIN_ID = 846008896

NAME, PHONE, COMMENT, BIRTHDATE = range(4)

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
    22: "Энергия свободы."
}

def calculate_energy(date_str):
    digits = [int(d) for d in date_str if d.isdigit()]
    total = sum(digits)
    while total > 22:
        total = sum(map(int, str(total)))
    return total

def start(update: Update, context):
    keyboard = [
        ["🔮 Мини-разбор по дате рождения"],
        ["💼 Услуги"]
    ]
    update.message.reply_text(
        "Привет 🤍\nВыбери, с чего начнём 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

def mini_start(update: Update, context):
    update.message.reply_text(
        "Введи дату рождения в формате ДД.ММ.ГГГГ",
        reply_markup=ReplyKeyboardRemove()
    )
    return BIRTHDATE

def process_birthdate(update: Update, context):
    text = update.message.text
    if not re.match(r"\d{2}\.\d{2}\.\d{4}", text):
        update.message.reply_text("Неверный формат. Попробуй снова.")
        return BIRTHDATE

    energy = calculate_energy(text)
    meaning = ENERGY_MEANINGS.get(energy, "Индивидуальная энергия.")

    update.message.reply_text(
        f"✨ Твоя энергия: {energy}\n\n{meaning}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 Оставить заявку", callback_data="order")]
        ])
    )
    return ConversationHandler.END

def order_start(update: Update, context):
    update.callback_query.answer()
    update.callback_query.message.reply_text("Как тебя зовут?")
    return NAME

def get_name(update: Update, context):
    context.user_data["name"] = update.message.text
    update.message.reply_text("Введите номер телефона:")
    return PHONE

def get_phone(update: Update, context):
    context.user_data["phone"] = update.message.text
    update.message.reply_text("Комментарий:")
    return COMMENT

def get_comment(update: Update, context):
    text = (
        f"📩 Заявка\n\n"
        f"Имя: {context.user_data['name']}\n"
        f"Телефон: {context.user_data['phone']}\n"
        f"Комментарий: {update.message.text}"
    )
    context.bot.send_message(ADMIN_ID, text)
    update.message.reply_text("✅ Заявка отправлена!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    mini_conv = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("^🔮"), mini_start)],
        states={BIRTHDATE: [MessageHandler(Filters.text & ~Filters.command, process_birthdate)]},
        fallbacks=[]
    )

    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(order_start, pattern="^order$")],
        states={
            NAME: [MessageHandler(Filters.text & ~Filters.command, get_name)],
            PHONE: [MessageHandler(Filters.text & ~Filters.command, get_phone)],
            COMMENT: [MessageHandler(Filters.text & ~Filters.command, get_comment)],
        },
        fallbacks=[]
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(mini_conv)
    dp.add_handler(order_conv)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()