from flask import Flask, request, render_template_string
import os
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8526200321:AAGBRYS738lVYJY94WaoglW8HNDc5HVz5Zk"
WEB_LINK = "https://cheeeeeeesbot-production.up.railway.app"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="ar">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chess Now</title>
<style>
body{margin:0;background:#dcecf8;font-family:Arial,sans-serif;color:#000}
.top{height:74px;display:flex;align-items:center;padding:0 28px;border-bottom:1px solid #c8d6e0;background:#dcecf8}
.x{font-size:46px;margin-right:34px}.title{font-size:34px;font-weight:700}.icons{margin-left:auto;font-size:36px}
.wait{height:calc(100vh - 74px);display:flex;align-items:center;justify-content:center;flex-direction:column;color:#9aa5ad}
.vs{display:flex;align-items:center;gap:28px}
.avatar{width:76px;height:76px;border-radius:50%;object-fit:cover}
.red{background:radial-gradient(circle at 35% 35%,#ff6973,#bd3038)}
.line{height:64px;width:1px;background:#bac7d1}
.dot{width:18px;height:18px;background:#000;border:4px solid #dcecf8;border-radius:50%;margin-left:52px;margin-top:-20px}
.waittxt{font-size:22px;margin-top:20px}
.loader{margin-top:18px;width:28px;height:28px;border:4px solid #c6cfd6;border-top-color:#777;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.btn{margin-top:25px;border:0;border-radius:14px;background:#111;color:#fff;padding:13px 34px;font-size:21px}
.player{display:flex;align-items:center;padding:15px 16px 10px}
.info{margin-left:12px;font-size:22px;font-weight:700}.rate{font-size:18px;font-weight:400;margin-top:5px}
.timer{margin-left:auto;background:#cfe0ee;border-radius:14px;padding:14px 18px;font-size:26px;font-weight:700}
.board{width:100vw;height:100vw;display:grid;grid-template-columns:repeat(8,1fr);grid-template-rows:repeat(8,1fr)}
.sq{display:flex;align-items:center;justify-content:center;font-size:43px;font-weight:bold}
.light{background:#f0d9b5}.dark{background:#b88762}
.white{color:white;text-shadow:0 0 2px #000,0 0 2px #000,0 0 2px #000}.black{color:#000}
.flag{font-size:34px;color:#999;margin-left:28px;margin-top:12px}
</style>
</head>
<body>

<div class="top">
  <div class="x">×</div>
  <div class="title">Chess Now</div>
  <div class="icons">⌄ ⋮</div>
</div>

{% if mode == "wait" %}
<div class="wait">
  <div class="vs">
    <div><div class="avatar red"></div><div class="dot"></div></div>
    <div class="line"></div>
    <img class="avatar" src="{{ avatar }}">
  </div>
  <div class="waittxt">Waiting for {{ name }} to connect</div>
  <div class="loader"></div>
  <button class="btn" onclick="location.href='/?play=1&time={{ time }}&name={{ name }}'">Play</button>
</div>
{% else %}
<div class="game">
  <div class="player">
    <div><div class="avatar red"></div><div class="dot"></div></div>
    <div class="info">لاعب الخصم ♟<div class="rate">1200</div></div>
    <div class="timer">◷ 09:54.9</div>
  </div>

  <div class="board">
    {% for sq in squares %}
      <div class="sq {{ sq.color }} {{ sq.piece_color }}">{{ sq.piece }}</div>
    {% endfor %}
  </div>

  <div class="player">
    <img class="avatar" src="{{ avatar }}">
    <div class="info">{{ name }} ♟<div class="rate">1200</div></div>
    <div class="timer">◷ {{ time }}:00.0</div>
  </div>
  <div class="flag">⚐</div>
</div>
{% endif %}

</body>
</html>
"""

def make_squares():
    board = [
        [("♖","white"),("♘","white"),("♗","white"),("♔","white"),("♕","white"),("♗","white"),("♘","white"),("♖","white")],
        [("♙","white"),("♙","white"),("♙","white"),("♙","white"),("♙","white"),("♙","white"),("♙","white"),("♙","white")],
        [("",""),("",""),("",""),("",""),("",""),("",""),("",""),("")],
        [("",""),("",""),("",""),("",""),("",""),("",""),("",""),("")],
        [("",""),("",""),("",""),("",""),("",""),("",""),("",""),("")],
        [("",""),("",""),("",""),("",""),("",""),("",""),("",""),("")],
        [("♟","black"),("♟","black"),("♟","black"),("♟","black"),("♟","black"),("♟","black"),("♟","black"),("♟","black")],
        [("♜","black"),("♞","black"),("♝","black"),("♚","black"),("♛","black"),("♝","black"),("♞","black"),("♜","black")]
    ]

    squares = []
    for r in range(8):
        for c in range(8):
            piece, piece_color = board[r][c]
            color = "light" if (r + c) % 2 == 0 else "dark"
            squares.append({"piece": piece, "piece_color": piece_color, "color": color})
    return squares

@app.route("/")
def home():
    mode = "game" if request.args.get("play") == "1" else "wait"
    time = request.args.get("time", "10")
    name = request.args.get("name", "fadi")
    avatar = "https://i.imgur.com/8Km9tLL.jpeg"
    return render_template_string(HTML, mode=mode, time=time, name=name, avatar=avatar, squares=make_squares())

@bot.message_handler(commands=["start"])
def start(message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("♟ ابدأ لعبة الشطرنج", url=WEB_LINK + "/?time=10&name=fadi"))
    bot.send_message(message.chat.id, "🔥 اهلاً بك في بوت الشطرنج\nاضغط الزر وابدأ اللعب", reply_markup=kb)

def run_bot():
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
