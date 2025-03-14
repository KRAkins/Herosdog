import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from user_data import get_user_requests, update_user_requests, user_paid
from payments import get_payment_message

# Получаем API-ключи из переменных окружения
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
USDT_TON_WALLET = os.getenv("USDT_TON_WALLET")

# Функция поиска по фото
async def search_google_by_image(image_url):
    try:
        url = f"https://www.googleapis.com/customsearch/v1?q=&searchType=image&imgUrl={image_url}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
        response = requests.get(url).json()
        return [item["link"] for item in response.get("items", [])]
    except Exception as e:
        print(f"Ошибка при поиске по изображению: {e}")
        return []

# Функция поиска цен
async def search_prices_on_google(product_name):
    try:
        url = f"https://serpapi.com/search.json?q={product_name}&tbm=shop&api_key={SERPAPI_KEY}"
        response = requests.get(url).json()
        return [(item["title"], item["link"], item.get("price", "Цена неизвестна")) for item in response.get("shopping_results", [])]
    except Exception as e:
        print(f"Ошибка при поиске цен: {e}")
        return []

# Обработка команды /start
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
    user_data = get_user_requests(user_id)

    if user_data["requests"] >= 3 and not user_data["paid"]:
        keyboard = [[InlineKeyboardButton("💰 Купить подписку", callback_data="buy")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("❌ Вы использовали 3 бесплатных запроса.\n💰 Подпишитесь за 5 USDT (TON).", reply_markup=reply_markup)
        return

    update_user_requests(user_id)

    photo = update.message.photo[-1].get_file()
    image_url = photo.file_path
    await update.message.reply_text("🔍 Ищу товары по фото...")

    results = await search_google_by_image(image_url)

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

# Обработка кнопок
async def button_click(update: Update, context):
    query = update.callback_query
    await query.answer()

    if query.data == "buy":
        await buy_subscription(update, context)
        return

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

