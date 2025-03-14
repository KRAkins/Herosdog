from flask import Flask, request
import telegram
from config import TELEGRAM_BOT_TOKEN

app = Flask(__name__)
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

@app.route("/", methods=["GET"])
def home():
    return "Бот работает!"

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    handle_update(update)
    return "OK", 200

def handle_update(update):
    if update.message:
        chat_id = update.message.chat_id
        text = update.message.text
        bot.send_message(chat_id, f"Ты написал: {text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
