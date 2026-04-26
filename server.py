from flask import Flask, request, jsonify, render_template_string, Response
import os, threading, time, urllib.parse, urllib.request
import telebot
import chess
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent

TOKEN = "8526200321:AAG8Im0iwJqIlfX82KwtFU-H9s34DWEQA2k"
WEB_LINK = "https://cheeeeeeesbot-production.up.railway.app"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
games = {}

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chess Now</title>
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
.msg{text-align:center;font-size:20px;margin:8px}
</style>
</head>
<body>
<div class="top"><div class="x">×</div><div class="title">Chess Now</div><div class="icons">⌄ ⋮</div></div>

<div class="player">
  <img class="avatar" src="{{ black_avatar }}">
  <div class="info" id="blackName">{{ black_name }}<div class="rate">1200</div></div>
  <div class="timer" id="blackTimer">◷ 00:00</div>
</div>

<div class="board" id="board"></div>

<div class="player">
  <img class="avatar" src="{{ white_avatar }}">
  <div class="info" id="whiteName">{{ white_name }}<div class="rate">1200</div></div>
  <div class="timer" id="whiteTimer">◷ 00:00</div>
</div>

<div class="msg" id="msg">Loading...</div>

<script>
const GAME_ID="{{ game_id }}";
const ROLE="{{ role }}";
let selected=null;
let legal=[];

const pieces={
  p:{w:"♙",b:"♟"}, r:{w:"♖",b:"♜"}, n:{w:"♘",b:"♞"},
  b:{w:"♗",b:"♝"}, q:{w:"♕",b:"♛"}, k:{w:"♔",b:"♚"}
};

function fmt(s){
  s=Math.max(0,Math.floor(s));
  let m=Math.floor(s/60), r=s%60;
  return String(m).padStart(2,"0")+":"+String(r).padStart(2,"0");
}

function sqName(r,c){
  const files=["a","b","c","d","e","f","g","h"];
  return files[c]+(8-r);
}

async function loadState(){
  const res=await fetch(`/state?game=${GAME_ID}`);
  const data=await res.json();

  document.getElementById("whiteTimer").innerText="◷ "+fmt(data.white_time);
  document.getElementById("blackTimer").innerText="◷ "+fmt(data.black_time);
  document.getElementById("msg").innerText=data.message;

  draw(data.board, data.turn, data.over);
}

function draw(b, turn, over){
  const board=document.getElementById("board");
  board.innerHTML="";

  for(let r=0;r<8;r++){
    for(let c=0;c<8;c++){
      const sq=sqName(r,c);
      const div=document.createElement("div");
      div.className="sq "+(((r+c)%2==0)?"light":"dark");

      if(selected===sq) div.classList.add("sel");
      if(legal.includes(sq)) div.classList.add("move");

      const p=b[r][c];
      if(p){
        div.innerText=pieces[p.type][p.color];
        div.classList.add(p.color==="w"?"white":"black");
      }

      div.onclick=()=>tap(sq, turn, over);
      board.appendChild(div);
    }
  }
}

async function tap(sq, turn, over){
  if(over) return;
  if((ROLE==="w" && turn!=="w") || (ROLE==="b" && turn!=="b")) return;

  if(selected){
    const res=await fetch("/move",{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({game:GAME_ID, from:selected, to:sq, role:ROLE})
    });
    selected=null; legal=[];
    await loadState();
    return;
  }

  const res=await fetch(`/legal?game=${GAME_ID}&square=${sq}&role=${ROLE}`);
  const data=await res.json();
  if(data.ok){
    selected=sq;
    legal=data.moves;
  }else{
    selected=null; legal=[];
  }
  await loadState();
}

setInterval(loadState,1000);
loadState();
</script>
</body>
</html>
"""

def get_game(game_id, minutes=10):
    if game_id not in games:
        games[game_id] = {
            "board": chess.Board(),
            "white_time": minutes * 60,
            "black_time": minutes * 60,
            "last": time.time(),
            "minutes": minutes
        }
    return games[game_id]

def update_clock(g):
    now = time.time()
    diff = now - g["last"]
    if not g["board"].is_game_over():
        if g["board"].turn == chess.WHITE:
            g["white_time"] -= diff
        else:
            g["black_time"] -= diff
    g["last"] = now

def board_json(board):
    out=[]
    for r in range(8):
        row=[]
        for c in range(8):
            sq=chess.square(c, 7-r)
            p=board.piece_at(sq)
            if p:
                row.append({"type": p.symbol().lower(), "color": "w" if p.color == chess.WHITE else "b"})
            else:
                row.append(None)
        out.append(row)
    return out

@app.route("/")
def home():
    game_id=request.args.get("game","solo")
    role=request.args.get("role","w")
    minutes=int(request.args.get("time","10"))

    white_name=request.args.get("white_name","White")
    black_name=request.args.get("black_name","Black")
    white_avatar=request.args.get("white_avatar","https://i.imgur.com/8Km9tLL.jpeg")
    black_avatar=request.args.get("black_avatar","https://i.imgur.com/8Km9tLL.jpeg")

    get_game(game_id, minutes)

    return render_template_string(
        HTML,
        game_id=game_id,
        role=role,
        white_name=white_name,
        black_name=black_name,
        white_avatar=white_avatar,
        black_avatar=black_avatar
    )

@app.route("/state")
def state():
    game_id=request.args.get("game","solo")
    g=get_game(game_id)
    update_clock(g)
    board=g["board"]

    if g["white_time"] <= 0:
        msg="انتهى وقت الأبيض"
        over=True
    elif g["black_time"] <= 0:
        msg="انتهى وقت الأسود"
        over=True
    elif board.is_checkmate():
        msg="كش مات"
        over=True
    elif board.is_stalemate():
        msg="تعادل"
        over=True
    else:
        msg="دور الأبيض" if board.turn == chess.WHITE else "دور الأسود"
        over=False

    return jsonify({
        "board": board_json(board),
        "turn": "w" if board.turn == chess.WHITE else "b",
        "white_time": int(g["white_time"]),
        "black_time": int(g["black_time"]),
        "message": msg,
        "over": over
    })

@app.route("/legal")
def legal():
    game_id=request.args.get("game","solo")
    square=request.args.get("square","")
    role=request.args.get("role","w")
    g=get_game(game_id)
    board=g["board"]

    if (role=="w" and board.turn != chess.WHITE) or (role=="b" and board.turn != chess.BLACK):
        return jsonify({"ok":False,"moves":[]})

    try:
        sq=chess.parse_square(square)
    except:
        return jsonify({"ok":False,"moves":[]})

    piece=board.piece_at(sq)
    if not piece:
        return jsonify({"ok":False,"moves":[]})

    if (role=="w" and piece.color != chess.WHITE) or (role=="b" and piece.color != chess.BLACK):
        return jsonify({"ok":False,"moves":[]})

    moves=[chess.square_name(m.to_square) for m in board.legal_moves if m.from_square == sq]
    return jsonify({"ok":True,"moves":moves})

@app.route("/move", methods=["POST"])
def move():
    data=request.get_json()
    game_id=data.get("game","solo")
    frm=data.get("from")
    to=data.get("to")
    role=data.get("role","w")

    g=get_game(game_id)
    update_clock(g)
    board=g["board"]

    if (role=="w" and board.turn != chess.WHITE) or (role=="b" and board.turn != chess.BLACK):
        return jsonify({"ok":False})

    try:
        move=chess.Move.from_uci(frm+to)
        if move not in board.legal_moves:
            move=chess.Move.from_uci(frm+to+"q")
        if move in board.legal_moves:
            board.push(move)
            g["last"]=time.time()
            return jsonify({"ok":True})
    except:
        pass

    return jsonify({"ok":False})

@app.route("/avatar")
def avatar_proxy():
    path=request.args.get("path","")
    if not path:
        return "",404
    try:
        url=f"https://api.telegram.org/file/bot{TOKEN}/{path}"
        data=urllib.request.urlopen(url,timeout=10).read()
        return Response(data,mimetype="image/jpeg")
    except:
        return "",404

def get_avatar_url(user_id):
    try:
        photos=bot.get_user_profile_photos(user_id,limit=1)
        if photos.total_count > 0:
            file_id=photos.photos[0][-1].file_id
            file_info=bot.get_file(file_id)
            path=urllib.parse.quote(file_info.file_path)
            return f"{WEB_LINK}/avatar?path={path}"
    except:
        pass
    return "https://i.imgur.com/8Km9tLL.jpeg"

@bot.message_handler(commands=["start"])
def start(message):
    kb=InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Play", switch_inline_query=""))
    bot.send_message(
        message.chat.id,
        "Want to play chess with any contact from Telegram?\nClick Play and choose a chat.",
        reply_markup=kb
    )

@bot.inline_handler(func=lambda q: True)
def inline_query(query):
    user=query.from_user
    name=user.first_name or "Player"
    avatar=get_avatar_url(user.id)

    safe_name=urllib.parse.quote(name)
    safe_avatar=urllib.parse.quote(avatar, safe=":/?=&.%")

    modes=[
        ("bullet","Bullet (1|0)","Timer: 1 min + 0 sec. Random color.","1"),
        ("blitz","Blitz (3|2)","Timer: 3 min + 2 sec. Random color.","3"),
        ("rapid","Rapid (10|5)","Timer: 10 min + 5 sec. Random color.","10"),
    ]

    results=[]
    for mid,title,desc,minutes in modes:
        game_id=f"{user.id}_{int(time.time())}_{mid}"

        start_link=f"{WEB_LINK}/?game={game_id}&role=w&time={minutes}&white_name={safe_name}&white_avatar={safe_avatar}&black_name=Opponent"
        join_link=f"{WEB_LINK}/?game={game_id}&role=b&time={minutes}&white_name={safe_name}&white_avatar={safe_avatar}&black_name=Opponent"

        kb=InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Start", url=start_link))
        kb.add(InlineKeyboardButton("Join", url=join_link))

        text=f"User {name} wants to play chess.\n\nGame Rules: {desc}\n\nPress Start if you created it, or Join if you are the opponent."

        results.append(
            InlineQueryResultArticle(
                id=f"{game_id}",
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
