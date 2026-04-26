from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 38266855  # حط API_ID مالك
API_HASH = "6cc39a629921d107b9f04f6510185f0e"  # حط API_HASH مالك
BOT_TOKEN = "8526200321:AAGBRYS738lVYJY94WaoglW8HNDc5HVz5Zk"  # حط توكن البوت

app = Client("chess_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

WEB_URL = "https://cheeeeeeesbot-production.up.railway.app"

# رسالة ستارت
@app.on_message(filters.command("start"))
async def start(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎮 لعب شطرنج", switch_inline_query="")]
    ])
    
    await message.reply_text(
        "♟️ هلا بك في بوت الشطرنج\n\nاضغط الزر وابدأ التحدي 🔥",
        reply_markup=buttons
    )

# inline (اختيار الوقت)
@app.on_inline_query()
async def inline(client, query):
    results = [
        {
            "type": "article",
            "id": "1",
            "title": "⚡ سريع (1 دقيقة)",
            "input_message_content": {
                "message_text": "🎮 لعبة شطرنج\n⏱️ 1 دقيقة\nاضغط للعب 👇"
            },
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "▶️ دخول اللعبة", "url": WEB_URL}]
                ]
            }
        },
        {
            "type": "article",
            "id": "2",
            "title": "⚡ متوسط (3 دقائق)",
            "input_message_content": {
                "message_text": "🎮 لعبة شطرنج\n⏱️ 3 دقائق\nاضغط للعب 👇"
            },
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "▶️ دخول اللعبة", "url": WEB_URL}]
                ]
            }
        },
        {
            "type": "article",
            "id": "3",
            "title": "🔥 سريع (10 دقائق)",
            "input_message_content": {
                "message_text": "🎮 لعبة شطرنج\n⏱️ 10 دقائق\nاضغط للعب 👇"
            },
            "reply_markup": {
                "inline_keyboard": [
                    [{"text": "▶️ دخول اللعبة", "url": WEB_URL}]
                ]
            }
        }
    ]

    await query.answer(results, cache_time=1)

app.run()
