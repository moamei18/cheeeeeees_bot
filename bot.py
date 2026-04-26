import threading
import telebot
from telebot.types import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request, render_template_string
import uuid

TOKEN = "8526200321:AAGBRYS738lVYJY94WaoglW8HNDc5HVz5Zk"
BOT_USERNAME = "@cheesfadi_bot"
WEB_URL = "https://cheeeeeeesbot-production.up.railway.app"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Chess</title>
<style>
body{margin:0;background:#dbeeff;font-family:Arial;text-align:center}
#board{width:360px;height:360px;margin:20px auto;display:grid;grid-template-columns:repeat(8,1fr);border:2px solid #333}
.cell{width:45px;height:45px;font-size:28px;display:flex;align-items:center;justify-content:center}
.white{background:#f0d9b5}.black{background:#b58863}
</style>
</head>
<body>
<h2>لعبة الشطرنج ♟️</h2>
<p>الوقت: {{ time }} دقائق</p>
<div id="board"></div>
<script>
const pieces=["♜","♞","♝","♛","♚","♝","♞","♜","♟","♟","♟","♟","♟","♟","♟","♟","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","","♙","♙","♙","♙","♙","♙","♙","♙","♖","♘","♗","♕","♔","♗","♘","♖"];
const board=document.getElementById("board");
for(let i=0;i<64;i++){let c=document.createElement("div");let r=Math.floor(i/8),col=i%8;c.className="cell "+((r+col)%2===0?"white":"black");c.textContent=pieces[i];board.appendChild(c);}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    t = request.args.get("time", "10")
    return render_template_string(HTML, time=t)

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        f"هلا بك في بوت الشطرنج ♟️\n\nاكتب اسم البوت بأي محادثة:\n{BOT_USERNAME}\n\nواختار وقت التحدي 🔥"
    )

@bot.inline_handler(lambda query: True)
def inline(query):
    results = []
    modes = [
        ("⚡ 1 دقيقة", "1"),
        ("⚡ 3 دقائق", "3"),
        ("🧠 10 دقائق", "10"),
    ]

    for title, t in modes:
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("♟️ Join", url=f"{WEB_URL}/?time={t}"))

        results.append(
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=title,
                description=f"تحدي شطرنج {t} دقائق",
                input_message_content=InputTextMessageContent(
                    f"♟️ تحدي شطرنج\n\n⏱ الوقت: {t} دقائق\n\nاضغط Join للعب 👇"
                ),
                reply_markup=kb
            )
        )

    bot.answer_inline_query(query.id, results, cache_time=1)

def run_bot():
    print("Chess bot polling...")
    bot.infinity_polling(skip_pending=True)

if __name__ == "__main__":
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=8080)
