from flask import Flask, request, render_template_string, Response
import os, threading, urllib.parse, urllib.request, time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent

TOKEN = "8526200321:AAG8Im0iwJqIlfX82KwtFU-H9s34DWEQA2k"
WEB_LINK = "https://cheeeeeeesbot-production.up.railway.app"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chess Now</title>
<script src="https://cdn.jsdelivr.net/npm/chess.js@1.0.0-beta.8/dist/chess.min.js"></script>
<style>
body{margin:0;background:#dcecf8;font-family:Arial;color:#000}
.top{height:74px;display:flex;align-items:center;padding:0 28px;border-bottom:1px solid #c8d6e0}
.x{font-size:46px;margin-right:34px}.title{font-size:34px;font-weight:700}.icons{margin-left:auto;font-size:36px}
.player{display:flex;align-items:center;padding:15px 16px 10px}
.avatar{width:78px;height:78px;border-radius:50%;object-fit:cover;background:#ccc}
.red{background:radial-gradient(circle at 35% 35%,#ff6973,#bd3038)}
.dot{width:18px;height:18px;background:#000;border:4px solid #dcecf8;border-radius:50%;margin-left:52px;margin-top:-20px}
.info{margin-left:12px;font-size:22px;font-weight:700}.rate{font-size:18px;font-weight:400;margin-top:5px}
.timer{margin-left:auto;background:#cfe0ee;border-radius:14px;padding:14px 18px;font-size:26px;font-weight:700}
.board{width:100vw;height:100vw;display:grid;grid-template-columns:repeat(8,1fr);grid-template-rows:repeat(8,1fr)}
.sq{display:flex;align-items:center;justify-content:center;font-size:43px;font-weight:bold;user-select:none}
.light{background:#f0d9b5}.dark{background:#b88762}
.sel{outline:4px solid #ffe066;outline-offset:-4px}
.move{box-shadow:inset 0 0 0 6px rgba(30,150,70,.45)}
.white{color:white;text-shadow:0 0 2px #000,0 0 2px #000}.black{color:#000}
.flag{font-size:34px;color:#999;margin-left:28px;margin-top:12px}
.msg{text-align:center;font-size:20px;margin:8px}
</style>
</head>
<body>
<div class="top"><div class="x">×</div><div class="title">Chess Now</div><div class="icons">⌄ ⋮</div></div>

<div class="player">
  <img class="avatar" src="{{ avatar }}">
  <div class="info">{{ name }}<div class="rate">1200</div></div>
  <div class="timer" id="blackTimer">◷ {{ time }}:00</div>
</div>

<div class="board" id="board"></div>

<div class="player">
  <div><div class="avatar red"></div><div class="dot"></div></div>
  <div class="info">.<div class="rate">1200</div></div>
  <div class="timer" id="whiteTimer">◷ {{ time }}:00</div>
</div>
<div class="flag">⚐</div>
<div class="msg" id="msg">دور الأبيض</div>

<script>
const game = new Chess();
const boardEl = document.getElementById("board");
const msg = document.getElementById("msg");
let selected = null;
let legal = [];
let baseTime = {{ seconds }};
let whiteTime = baseTime;
let blackTime = baseTime;

const pieces = {
  p:{w:"♙",b:"♟"}, r:{w:"♖",b:"♜"}, n:{w:"♘",b:"♞"},
  b:{w:"♗",b:"♝"}, q:{w:"♕",b:"♛"}, k:{w:"♔",b:"♚"}
};

function fmt(s){
  s=Math.max(0,s);
  let m=Math.floor(s/60);
  let r=s%60;
  return String(m).padStart(2,"0")+":"+String(r).padStart(2,"0");
}

function updateTimers(){
  document.getElementById("whiteTimer").innerText="◷ "+fmt(whiteTime);
  document.getElementById("blackTimer").innerText="◷ "+fmt(blackTime);
}

setInterval(()=>{
  if(game.isGameOver()) return;
  if(game.turn()==="w") whiteTime--; else blackTime--;
  updateTimers();
  if(whiteTime<=0) msg.innerText="انتهى وقت الأبيض";
  if(blackTime<=0) msg.innerText="انتهى وقت الأسود";
},1000);

function squareName(r,c){
  const files=["a","b","c","d","e","f","g","h"];
  return files[c]+(8-r);
}

function draw(){
  boardEl.innerHTML="";
  const b = game.board();

  for(let r=0;r<8;r++){
    for(let c=0;c<8;c++){
      const sqName = squareName(r,c);
      const div=document.createElement("div");
      div.className="sq "+(((r+c)%2==0)?"light":"dark");
      div.dataset.square=sqName;

      if(selected===sqName) div.classList.add("sel");
      if(legal.includes(sqName)) div.classList.add("move");

      const p=b[r][c];
      if(p){
        div.innerText=pieces[p.type][p.color];
        div.classList.add(p.color==="w"?"white":"black");
      }

      div.onclick=()=>tap(sqName);
      boardEl.appendChild(div);
    }
  }

  if(game.isCheckmate()) msg.innerText="كش مات";
  else if(game.isDraw()) msg.innerText="تعادل";
  else msg.innerText=game.turn()==="w" ? "دور الأبيض" : "دور الأسود";
}

function tap(sq){
  if(game.isGameOver()) return;

  if(selected){
    const move = game.move({from:selected,to:sq,promotion:"q"});
    selected=null;
    legal=[];
    if(move){ draw(); return; }
  }

  const piece = game.get(sq);
  if(piece && piece.color===game.turn()){
    selected=sq;
    legal=game.moves({square:sq, verbose:true}).map(m=>m.to);
  } else {
    selected=null;
    legal=[];
  }
  draw();
}

updateTimers();
draw();
</script>
</body>
</html>
"""

@app.route("/")
def home():
    name = request.args.get("name", "fadi")
    game_time = request.args.get("time", "10")
    avatar = request.args.get("avatar", "https://i.imgur.com/8Km9tLL.jpeg")
    try:
        minutes = int(game_time)
    except:
        minutes = 10

    return render_template_string(
        HTML,
        name=name,
        time=minutes,
        seconds=minutes*60,
        avatar=avatar
    )

@app.route("/avatar")
def avatar_proxy():
    path = request.args.get("path", "")
    if not path:
        return "", 404
    try:
        url = f"https://api.telegram.org/file/bot{TOKEN}/{path}"
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
    bot.send_message(
        message.chat.id,
        "Want to play chess with any contact from Telegram?\\n"
        "Click Play, choose a chat, then select the game mode.",
        reply_markup=kb
    )

@bot.inline_handler(func=lambda q: True)
def inline_query(query):
    user = query.from_user
    name = user.first_name or "fadi"
    avatar = get_avatar_url(user.id)

    safe_name = urllib.parse.quote(name)
    safe_avatar = urllib.parse.quote(avatar, safe=":/?=&.%")

    modes = [
        ("bullet","Bullet (1|0)","Timer: 1 min + 0 sec. Random color.","1"),
        ("blitz","Blitz (3|2)","Timer: 3 min + 2 sec. Random color.","3"),
        ("rapid","Rapid (10|5)","Timer: 10 min + 5 sec. Random color.","10"),
    ]

    results=[]
    for mid,title,desc,minutes in modes:
        link=f"{WEB_LINK}/?time={minutes}&name={safe_name}&avatar={safe_avatar}"
        kb=InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Join", url=link))

        text=f"User {name} wants to play chess.\\n\\nGame Rules: {desc}\\n\\nClick the button below to join the game."

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
    port=int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0",port=port)
