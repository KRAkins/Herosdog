import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Настройка логирования
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена бота из переменных окружения
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    print("❌ Ошибка: переменная TELEGRAM_BOT_TOKEN не установлена! Проверь настройки Railway.")
    exit(1)

# Функция старта бота
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Привет! Отправь фото товара 📸")

# Функция обработки фото
async def handle_photo(update: Update, context: CallbackContext) -> None:
    try:
        photo = update.message.photo[-1]  # Берем лучшее качество
        file = await photo.get_file()
        file_path = file.file_path  # Получаем URL фото
        
        # Подтверждение загрузки
        await update.message.reply_text("Фото получено! Ищу информацию...")

        # Имитация обработки фото
        await asyncio.sleep(2)

        # Ответ с кнопками
        keyboard = [
            [InlineKeyboardButton("Найти дешевле", callback_data="cheaper")],
            [InlineKeyboardButton("Найти дороже", callback_data="expensive")],
            [InlineKeyboardButton("Просто найти", callback_data="find")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "Выберите действие:", reply_markup=reply_markup
        )

    except Exception as e:
        logger.error(f"Ошибка обработки фото: {e}")
        await update.message.reply_text("❌ Произошла ошибка при обработке фото.")

# Функция обработки нажатий на кнопки
async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "cheaper":
        await query.message.reply_text("🔍 Ищу более дешевые варианты...")
    elif query.data == "expensive":
        await query.message.reply_text("🔍 Ищу более дорогие варианты...")
    elif query.data == "find":
        await query.message.reply_text("🔍 Ищу товар...")

# Главная функция
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    
    # Обработчик кнопок
    application.add_handler(MessageHandler(filters.ALL, button_handler))

    # Запуск бота
    logger.info("✅ Бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
