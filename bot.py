import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Загружаем токен из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен!")

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Привет! Отправь фото товара 📸")

# Обработчик фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file = await update.message.photo[-1].get_file()
    file_path = file.file_path
    logger.info(f"Фото получено: {file_path}")

    keyboard = [[
        InlineKeyboardButton("🔽 Найти дешевле", callback_data="cheaper"),
        InlineKeyboardButton("🔼 Найти дороже", callback_data="expensive"),
    ], [
        InlineKeyboardButton("🔍 Просто найти", callback_data="search")
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Фото получено! Ищу информацию...", reply_markup=reply_markup)

# Обработчик кнопок
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    action = query.data
    if action == "cheaper":
        await query.edit_message_text("🔍 Поиск товаров дешевле...")
    elif action == "expensive":
        await query.edit_message_text("🔍 Поиск товаров дороже...")
    elif action == "search":
        await query.edit_message_text("🔍 Поиск товара без фильтра...")

# Создаём приложение бота
application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(CallbackQueryHandler(button_callback))

# Запускаем бота
if __name__ == "__main__":
    logger.info("✅ Бот запущен!")
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        webhook_url=f"https://{os.getenv('RAILWAY_URL')}/{TELEGRAM_BOT_TOKEN}"
    )

 