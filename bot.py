import telebot
from telebot.types import InlineQueryResultArticle, InputTextMessageContent
import uuid

TOKEN = "8526200321:AAGBRYS738lVYJY94WaoglW8HNDc5HVz5Zk"  # حط توكنك هنا

bot = telebot.TeleBot(TOKEN)

# ---------------------------
# /start
# ---------------------------
@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "هلا بك في بوت الشطرنج ♟️\n\n"
        "حتى تلعب:\n"
        "اكتب اسم البوت بأي محادثة 👇\n\n"
        "@cheesfadi_bot\n\n"
        "اختار الوقت وابدأ التحدي 🔥"
    )

# ---------------------------
# INLINE (اختيار الوقت)
# ---------------------------
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
                id=str(uuid.uuid4()),
                title=title,
                description=f"ابدأ تحدي {time} دقائق",
                input_message_content=InputTextMessageContent(
                    f"♟️ تم إنشاء تحدي شطرنج\n\n⏱ الوقت: {time} دقائق\n\nاضغط الزر وابدأ اللعب 👇"
                ),
                reply_markup=telebot.types.InlineKeyboardMarkup().add(
                    telebot.types.InlineKeyboardButton(
                        "♟️ ابدأ اللعب",
                        url="https://www.chess.com/play/online"
                    )
                )
            )
        )

    bot.answer_inline_query(query.id, results)

# ---------------------------
# تشغيل البوت
# ---------------------------
print("Chess bot running...")
bot.infinity_polling()
