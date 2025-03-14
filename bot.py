import os
import json
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

# Устанавливаем логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загружаем токен из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Ошибка: переменная TELEGRAM_BOT_TOKEN не установлена!")

# Файл базы данных
DATABASE_FILE = "database.json"

# Функция загрузки данных из базы
def load_data():
    try:
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except json.JSONDecodeError:
        return {}

# Функция сохранения данных в базу
def save_data(data):
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Функция команды /start
async def start(update: Update, context):
    user = update.effective_user
    await update.message.reply_text(
        f"Привет, {user.first_name}! Отправь фото товара 📸"
    )

# Обработчик фотографий
async def handle_photo(update: Update, context):
    try:
        # Получаем фото
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_path = file.file_path

        # Отправляем подтверждение пользователю
        keyboard = [
            [InlineKeyboardButton("🔎 Найти товар", callback_data="search")],
            [InlineKeyboardButton("💰 Дешевле", callback_data="cheaper"),
             InlineKeyboardButton("📈 Дороже", callback_data="expensive")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)

        # Логируем полученное фото
        logger.info(f"Получено фото: {file_path}")

    except Exception as e:
        logger.error(f"Ошибка обработки фото: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обработке фото.")

# Обработчик кнопок
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "search":
        await query.message.reply_text("🔍 Ищем товар...")
    elif query.data == "cheaper":
        await query.message.reply_text("💰 Ищем варианты дешевле...")
    elif query.data == "expensive":
        await query.message.reply_text("📈 Ищем варианты дороже...")

# Основная функция запуска бота
async def main():
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("✅ Бот запущен!")
    await application.run_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        logger.error(f"Ошибка запуска бота: {e}")

