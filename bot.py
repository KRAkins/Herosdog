from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
from config import TELEGRAM_BOT_TOKEN, GOOGLE_API_KEY, SERPAPI_KEY, SEARCH_ENGINE_ID
from user_data import get_user_requests, update_user_requests, user_paid
from payments import get_payment_message

# Функция поиска по фото
def search_google_by_image(image_url):
    url = f"https://www.googleapis.com/customsearch/v1?q=&searchType=image&imgUrl={image_url}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
    response = requests.get(url).json()
    return [item["link"] for item in response.get("items", [])]

# Функция поиска цен
def search_prices_on_google(product_name):
    url = f"https://serpapi.com/search.json?q={product_name}&tbm=shop&api_key={SERPAPI_KEY}"
    response = requests.get(url).json()
    return [(item["title"], item["link"], item["price"]) for item in response.get("shopping_results", [])]

# Обработка команды /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Отправь фото товара 📸")

# Оплата подписки
def buy_subscription(update: Update, context: CallbackContext):
    update.message.reply_text(get_payment_message(), parse_mode="Markdown")

# Подтверждение оплаты
def confirm_payment(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    user_paid(user_id)
    update.message.reply_text("✅ Подписка активирована! Теперь у вас нет ограничений.")

# Обработка фото
def handle_photo(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    user_data = get_user_requests(user_id)

    if user_data["requests"] >= 3 and not user_data["paid"]:
        keyboard = [[InlineKeyboardButton("💰 Купить подписку", callback_data="buy")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("❌ Вы использовали 3 бесплатных запроса.\n💰 Подпишитесь за 5 USDT (TON).", reply_markup=reply_markup)
        return

    update_user_requests(user_id)

    photo = update.message.photo[-1].get_file()
    image_url = photo.file_path
    update.message.reply_text("🔍 Ищу товары по фото...")

    results = search_google_by_image(image_url)

    if results:
        keyboard = [
            [InlineKeyboardButton("💰 Дешевые", callback_data="low_price"),
             InlineKeyboardButton("💎 Дорогие", callback_data="high_price")],
            [InlineKeyboardButton("🔍 Просто найти", callback_data="search_all")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f"📌 Найдено товаров: {len(results)}\nВыбери фильтр:", reply_markup=reply_markup)
        context.user_data["product_links"] = results
    else:
        update.message.reply_text("❌ Товар не найден.")

# Обработка кнопок
def button_click(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "buy":
        buy_subscription(update, context)
        return

# Запуск бота
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("buy", buy_subscription))
    dp.add_handler(CommandHandler("confirm", confirm_payment))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))
    dp.add_handler(CallbackQueryHandler(button_click))
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
