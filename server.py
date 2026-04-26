import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="ar">
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chess Now</title>
<style>
body{margin:0;background:#dcecf8;font-family:Arial;color:#000}
.top{height:75px;display:flex;align-items:center;gap:35px;padding:0 28px;font-size:32px;font-weight:bold;border-bottom:1px solid #c8d6e0}
.close{font-size:46px}.menu{margin-left:auto}
.wait{height:calc(100vh - 75px);display:flex;flex-direction:column;align-items:center;justify-content:center;color:#aaa;font-size:23px}
.vs{display:flex;align-items:center;gap:28px}.line{height:65px;width:1px;background:#b8c4cc}
.avatar{width:90px;height:90px;border-radius:50%;object-fit:cover}
.red{background:radial-gradient(circle at 35% 35%,#ff6d75,#bd3038)}
.dot{width:20px;height:20px;background:#000;border:4px solid #dcecf8;border-radius:50%;margin-left:62px;margin-top:-22px;position:relative}
.spinner{margin-top:25px;width:28px;height:28px;border:4px solid #ccc;border-top-color:#777;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.game{padding-top:15px}
.player{display:flex;align-items:center;padding:0 16px;margin-bottom:10px}
.info{margin-left:12px;font-size:24px;font-weight:bold}.rate{font-size:19px;font-weight:normal;margin-top:6px}
.timer{margin-left:auto;background:#cfe0ee;border-radius:14px;padding:15px 18px;font-size:27px;font-weight:bold}
.board{width:100vw;height:100vw;display:grid;grid-template-columns:repeat(8,1fr)}
.sq{display:flex;align-items:center;justify-content:center;font-size:44px}
.light{background:#f0d9b5}.dark{background:#b88762}
.white{color:#fff;text-shadow:0 0 2px #000,0 0 2px #000}.black{color:#000}
.bottom{margin-top:18px}.flag{font-size:36px;color:#999;margin-left:30px}
.playbtn{margin-top:25px;background:#111;color:white;border:0;border-radius:14px;padding:14px 35px;font-size:22px}
</style>
</head>
<body>
<div class="top"><span class="close">×</span><span>Chess Now</span><span class="menu">⌄ ⋮</span></div>

{% if mode == "wait" %}
<div class="wait">
  <div class="vs">
    <div><div class="avatar red"></div><div class="dot"></div></div>
    <div class="line"></div>
    <img class="avatar" src="{{ avatar }}">
  </div>
  <div style="margin-top:20px">Waiting for {{ name }} to connect</div>
  <div class="spinner"></div>
  <button class="playbtn" onclick="location.href='/?play=1&time={{time}}&name={{name}}'">Play</button>
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

  <div class="player bottom">
    <img class="avatar" src="{{ avatar }}">
    <div class="info">{{ name }} ♟<div class="rate">1200</div></div>
    <div class="timer">◷ {{time}}:00.0</div>
  </div>
  <div class="flag">⚐</div>
</div>
{% endif %}
</body>
</html>
"""

@app.route("/")
def home():
    mode = "game" if request.args.get("play") == "1" else "wait"
    time = request.args.get("time", "10")
    name = request.args.get("name", "fadi")
    avatar = "https://i.imgur.com/8Km9tLL.jpeg"

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

    return render_template_string(HTML, mode=mode, time=time, name=name, avatar=avatar, squares=squares)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
