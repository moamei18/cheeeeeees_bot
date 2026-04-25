import telebot
from telebot.types import InlineQueryResultArticle, InputTextMessageContent

TOKEN = "8526200321:AAGBRYS738lVYJY94WaoglW8HNDc5HVz5Zk"

bot = telebot.TeleBot(TOKEN)

@bot.inline_handler(lambda query: True)
def inline(query):
    results = []

    modes = [
        ("⚡ 1 دقيقة", "1"),
        ("⚡ 3 دقائق", "3"),
        ("🧠 10 دقائق", "10"),
    ]

    for title, time in modes:
        results.append(
            InlineQueryResultArticle(
                id=time,
                title=title,
                input_message_content=InputTextMessageContent(
                    f"♟️ تم إنشاء تحدي شطرنج\n⏱ الوقت: {time} دقائق\n\nاضغط Join للعب"
                ),
                reply_markup=telebot.types.InlineKeyboardMarkup().add(
                    telebot.types.InlineKeyboardButton(
                        "♟️ Join",
                        url="https://lichess.org"
                    )
                )
            )
        )

    bot.answer_inline_query(query.id, results)

print("Chess bot running...")
bot.infinity_polling()
