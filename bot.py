import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8526200321:AAGBRYS738lVYJY94WaoglW8HNDc5HVz5Zk"
WEB_LINK = "https://cheeeeeeesbot-production.up.railway.app/?time=10&name=fadi"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("♟ ابدأ تحدي شطرنج", url=WEB_LINK))

    bot.send_message(
        message.chat.id,
        "اختر الوقت وابدأ التحدي 🔥",
        reply_markup=kb
    )

bot.infinity_polling()
