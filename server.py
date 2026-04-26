from flask import Flask, request, render_template_string, Response
import os
import threading
import urllib.parse
import urllib.request
import time
import telebot
from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent,
)

TOKEN = "8526200321:AAG8Im0iwJqIlfX82KwtFU-H9s34DWEQA2k"
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
.top{height:74px;display:flex;align-items:center;padding:0 28px;border-bottom:1px solid #c8d6e0}
.x{font-size:46px;margin-right:34px}.title{font-size:34px;font-weight:700}.icons{margin-left:auto;font-size:36px}
.wait{height:calc(100vh - 74px);display:flex;align-items:center;justify-content:center;flex-direction:column;color:#9aa5ad}
.avatar{width:78px;height:78px;border-radius:50%;object-fit:cover;background:#ccc}
.red{background:radial-gradient(circle at 35% 35%,#ff6973,#bd3038)}
.dot{width:18px;height:18px;background:#000;border:4px solid #dcecf8;border-radius:50%;margin-left:52px;margin-top:-20px}
.waittxt{font-size:22px;margin-top:20px}
.loader{margin-top:18px;width:28px;height:28px;border:4px solid #c6cfd6;border-top-color:#777;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.player{display:flex;align-items:center;padding:15px 16px 10px}
.info{margin-left:12px;font-size:22px;font-weight:700}.rate{font-size:18px;font-weight:400;margin-top:5px}
.timer{margin-left:auto;background:#cfe0ee;border-radius:14px;padding:14px 18px;font-size:26px;font-weight:700}
.board{width:100vw;height:100vw;display:grid;grid-template-columns:repeat(8,1fr);grid-template-rows:repeat(8,1fr)}
.sq{display:flex;align-items:center;justify-content:center;font-size:43px;font-weight:bold}
.light{background:#f0d9b5}.dark{background:#b88762}
.white{color:white;text-shadow:0 0 2px #000,0 0 2px #000}.black{color:#000}
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
  <img class="avatar" src="{{ avatar }}">
  <div class="dot"></div>
  <div class="waittxt">Waiting for anyone to join</div>
  <div class="loader"></div>
</div>
{% else %}
<div>
  <div class="player">
    <img class="avatar" src="{{ avatar }}">
    <div class="info">{{ name }}<div class="rate">1200</div></div>
    <div class="timer">◷ {{ game_time }}:00.0</div>
  </div>

  <div class="board">
    {% for sq in squares %}
      <div class="sq {{ sq.color }} {{ sq.piece_color }}">{{ sq.piece }}</div>
    {% endfor %}
  </div>

  <div class="player">
    <div>
      <div class="avatar red"></div>
      <div class="dot"></div>
    </div>
    <div class="info">.<div class="rate">1200</div></div>
    <div class="timer">◷ 09:55.5</div>
  </div>
  <div class="flag">⚐</div>
</div>
{% endif %}

</body>
</html>
"""

def make_squares():
    empty = ("", "")
    board = [
        [("♜","black"),("♞","black"),("♝","black"),("♛","black"),("♚","black"),("♝","black"),("♞","black"),("♜","black")],
        [("♟","black"),("♟","black"),("♟","black"),("♟","black"),("♟","black"),("♟","black"),("♟","black"),("♟","black")],
        [empty,empty,empty,empty,empty,empty,empty,empty],
        [empty,empty,empty,empty,empty,empty,empty,empty],
        [empty,empty,empty,empty,empty,empty,empty,empty],
        [empty,empty,empty,empty,empty,empty,empty,empty],
        [("♙","white"),("♙","white"),("♙","white"),("♙","white"),("♙","white"),("♙","white"),("♙","white"),("♙","white")],
        [("♖","white"),("♘","white"),("♗","white"),("♕","white"),("♔","white"),("♗","white"),("♘","white"),("♖","white")]
    ]

    squares = []
    for r in range(8):
        for c in range(8):
            cell = board[r][c]
            piece, piece_color = cell if len(cell) == 2 else ("", "")
            color = "light" if (r + c) % 2 == 0 else "dark"
            squares.append({"piece": piece, "piece_color": piece_color, "color": color})
    return squares

@app.route("/")
def home():
    mode = "game" if request.args.get("play") == "1" else "wait"
    name = request.args.get("name", "fadi")
    game_time = request.args.get("time", "10")
    avatar = request.args.get("avatar", "https://i.imgur.com/8Km9tLL.jpeg")

    return render_template_string(
        HTML,
        mode=mode,
        name=name,
        game_time=game_time,
        avatar=avatar,
        squares=make_squares()
    )

@app.route("/avatar")
def avatar_proxy():
    path = request.args.get("path", "")
    if not path:
        return "", 404

    url = f"https://api.telegram.org/file/bot{TOKEN}/{path}"

    try:
        data = urllib.request.urlopen(url, timeout=10).read()
        return Response(data, mimetype="image/jpeg")
    except:
        return "", 404

def get_avatar_url(user_id):
    try:
        photos = bot.get_user_profile_photos(user_id, limit=1)

        if photos.total_count > 0:
            file_id = photos.photos[0][-1].file_id
            file_info = bot.get_file(file_id)
            path = urllib.parse.quote(file_info.file_path)
            return f"{WEB_LINK}/avatar?path={path}"
    except:
        pass

    return "https://i.imgur.com/8Km9tLL.jpeg"

@bot.message_handler(commands=["start"])
def start(message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Play", switch_inline_query=""))

    text = (
        "Want to play chess with any contact from Telegram?\n"
        "It's very easy to do so, click the button below or go to the chat which you want to send the invitation to, "
        "type in @cheesfadi_bot, and add a space.\n"
        "You can also send the invitation to a group or channel. In that case, the first person to click the 'Join' button will be your opponent."
    )

    bot.send_message(message.chat.id, text, reply_markup=kb)

@bot.inline_handler(func=lambda query: True)
def inline_query(query):
    user = query.from_user
    name = user.first_name or "fadi"
    avatar = get_avatar_url(user.id)

    safe_name = urllib.parse.quote(name)
    safe_avatar = urllib.parse.quote(avatar, safe=":/?=&.%")

    modes = [
        ("bullet", "Bullet (1|0)", "Timer: 1 min + 0 sec. Random color.", "1"),
        ("blitz", "Blitz (3|2)", "Timer: 3 min + 2 sec. Random color.", "3"),
        ("rapid", "Rapid (10|5)", "Timer: 10 min + 5 sec. Random color.", "10"),
    ]

    results = []

    for mid, title, desc, minutes in modes:
        join_link = f"{WEB_LINK}/?play=1&time={minutes}&name={safe_name}&avatar={safe_avatar}"

        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Join", url=join_link))

        text = (
            f"User {name} wants to play chess.\n\n"
            f"Game Rules: {desc}\n\n"
            f"Click the button below to join the game."
        )

        results.append(
            InlineQueryResultArticle(
                id=f"{mid}_{int(time.time())}",
                title=title,
                description=desc,
                input_message_content=InputTextMessageContent(text),
                reply_markup=kb
            )
        )

    bot.answer_inline_query(query.id, results, cache_time=1, is_personal=True)

def run_bot():
    try:
        bot.remove_webhook()
    except:
        pass

    bot.infinity_polling(skip_pending=True)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
