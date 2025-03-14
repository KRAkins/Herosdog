from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import requests
import os
import logging
from config import TELEGRAM_BOT_TOKEN, GOOGLE_API_KEY, SERPAPI_KEY, SEARCH_ENGINE_ID
from user_data import get_user_requests, update_user_requests, user_paid
from payments import get_payment_message

# Настраиваем логирование
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Функция поиска товаров по фото через Google API
async def search_google_by_image(image_url):
    url = f"https://www.googleapis.com/customsearch/v1?q=&searchType=image&imgUrl={image_url}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
    response = requests.get(url).json()
    logger.info(f"Google Image Search Response: {response}")  # Логируем ответ

    if "items" in response:
        return [item["link"] for item in response["items"]]
    else:
        return []

# Функция поиска цен через SerpApi
async def search_prices_on_google(product_name):
    url = f"https://serpapi.com/search.json?q={product_name}&tbm=shop&api_key={SERPAPI_KEY}"
    response = requests.get(url).json()
    logger.info(f"SerpAPI Search Response: {response}")  # Логируем ответ

    if "shopping_results" in response:
        return [(item["title"], item["link"], item["price"]) for item in response["shopping_results"]]
    else:
        return []

# Команда /start
async def start(update: Update, context):
    await update.message.reply_text("Привет! Отправь фото товара 📸")

# Оплата подписки
async def buy_subscription(update: Update, context):
    await update.message.reply_text(get_payment_message(), parse_mode="Markdown")

# Подтверждение оплаты
async def confirm_payment(update: Update, context):
    user_id = update.message.chat_id
    user_paid(user_id)
    await update.message.reply_text("✅ Подписка активирована! Теперь у вас нет ограничений.")

# Обработка фото
async def handle_photo(update: Update, context):
    user_id = update.message.chat_id
    logger.info(f"User {user_id} sent a photo.")  # Логируем факт получения фото

    try:
        # Проверяем лимиты пользователя
        user_data = get_user_requests(user_id)
        if user_data["requests"] >= 3 and not user_data["paid"]:
            keyboard = [[InlineKeyboardButton("💰 Купить подписку", callback_data="buy")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text("❌ Вы использовали 3 бесплатных запроса.\n💰 Подпишитесь за 5 USDT (TON).", reply_markup=reply_markup)
            return

        # Обновляем количество запросов
        update_user_requests(user_id)

        # Получаем URL изображения
        photo = await update.message.photo[-1].get_file()
        image_url = photo.file_path
        logger.info(f"Image URL: {image_url}")  # Логируем URL фото

        await update.message.reply_text("🔍 Ищу товары по фото...")

        # Выполняем поиск товаров по фото
        results = await search_google_by_image(image_url)
        logger.info(f"Search Results: {results}")  # Логируем результаты поиска

        if results:
            keyboard = [
                [InlineKeyboardButton("💰 Дешевые", callback_data="low_price"),
                 InlineKeyboardButton("💎 Дорогие", callback_data="high_price")],
                [InlineKeyboardButton("🔍 Просто найти", callback_data="search_all")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(f"📌 Найдено товаров: {len(results)}\nВыбери фильтр:", reply_markup=reply_markup)
            context.user_data["product_links"] = results
        else:
            await update.message.reply_text("❌ Товар не найден.")
    except Exception as e:
        logger.error(f"Error in handle_photo: {e}")  # Логируем ошибку
        await update.message.reply_text("❌ Произошла ошибка при обработке фото.")

# Обработка кнопок
async def button_click(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "buy":
        await buy_subscription(update, context)

# Запуск бота
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("buy", buy_subscription))
    application.add_handler(CommandHandler("confirm", confirm_payment))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(button_click))

    application.run_polling()

if __name__ == "__main__":
    main()

