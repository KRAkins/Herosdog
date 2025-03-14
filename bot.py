import os
import logging
import json
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

# Логирование для отладки
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Проверка токена перед запуском
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ Ошибка: переменная TELEGRAM_BOT_TOKEN не установлена!")

# Функция обработки команды /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Отправь фото товара 📸")

# Функция обработки полученного фото
async def handle_photo(update: Update, context):
    try:
        user_id = update.message.from_user.id
        photo = update.message.photo[-1]  # Берем самое большое фото
        file = await photo.get_file()
        image_url = file.file_path

        # Подтверждение получения фото
        await update.message.reply_text("Фото получено! Ищу информацию...")

        # Клавиатура с вариантами выбора
        keyboard = [
            [InlineKeyboardButton("🔽 Найти дешевле", callback_data="cheaper")],
            [InlineKeyboardButton("🔼 Найти дороже", callback_data="expensive")],
            [InlineKeyboardButton("🔍 Просто найти", callback_data="search")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

    except Exception as e:
        logger.error(f"Ошибка при обработке фото: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обработке фото.")

# Функция обработки кнопок
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    
    if query.data == "cheaper":
        await query.message.reply_text("🔽 Поиск товаров дешевле...")
        # Здесь можно добавить код поиска
    elif query.data == "expensive":
        await query.message.reply_text("🔼 Поиск товаров дороже...")
        # Здесь можно добавить код поиска
    elif query.data == "search":
        await query.message.reply_text("🔍 Поиск товара без фильтра...")
        # Здесь можно добавить код поиска

# Основная функция
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(button_handler))

    logging.info("✅ Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()

