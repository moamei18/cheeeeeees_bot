from flask import Flask, render_template_string
import os
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔴 حط توكن بوتك هنا
TOKEN = "8526200321:AAGBRYS738lVYJY94WaoglW8HNDc5HVz5Zk"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ================== موقع الشطرنج ==================
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chess</title>
<style>
body{margin:0;background:#dcecf8;font-family:Arial;text-align:center}
h2{margin:20px}
.board{display:grid;grid-template-columns:repeat(8,1fr);width:100vw;height:100vw}
.sq{display:flex;align-items:center;justify-content:center;font-size:38px}
.light{background:#f0d9b5}.dark{background:#b88762}
</style>
</head>
<body>
<h2>♟ Chess Now</h2>

<div class="board">
{% for sq in squares %}
<div class="sq {{sq.color}}">{{sq.piece}}</div>
{% endfor %}
</div>

</body>
</html>
"""

@app.route("/")
def home():
    board = [
        ["♖","♘","♗","♔","♕","♗","♘","♖"],
        ["♙","♙","♙","♙","♙","♙","♙","♙"],
        ["","","","","","","",""],
        ["","","","","","","",""],
        ["","","","","","","",""],
        ["","","","","","","",""],
        ["♟","♟","♟","♟","♟","♟","♟","♟"],
        ["♜","♞","♝","♚","♛","♝","♞","♜"]
    ]

    squares = []
    for r in range(8):
        for c in range(8):
            color = "light" if (r + c) % 2 == 0 else "dark"
            squares.append({"piece": board[r][c], "color": color})

    return render_template_string(HTML, squares=squares)

# ================== البوت ==================

@bot.message_handler(commands=["start"])
def start(message):
    link = "https://cheeeeeeesbot-production.up.railway.app"
    
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("♟ ابدأ لعبة الشطرنج", url=link))

    bot.send_message(
        message.chat.id,
        "🔥 اهلاً بك في لعبة الشطرنج\nاضغط الزر وابدأ اللعب",
        reply_markup=kb
    )

def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

# تشغيل البوت بخيط
threading.Thread(target=run_bot, daemon=True).start()

# ================== تشغيل السيرفر ==================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
