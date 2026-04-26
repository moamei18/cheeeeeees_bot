from flask import Flask, request, render_template_string, Response
from flask_socketio import SocketIO, join_room, emit
import os, time, threading, urllib.parse, urllib.request
import chess
import telebot
from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQueryResultArticle, InputTextMessageContent
)

TOKEN = "8526200321:AAH2PXUUL5Zzue-Hkf8Q1HecJo6YMwW-Kco"
BOT_USERNAME = "cheesfadi_bot"
WEB_LINK = "https://cheeeeeeesbot-production.up.railway.app"

app = Flask(__name__)
app.config["SECRET_KEY"] = "chess_secret"
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

bot = telebot.TeleBot(TOKEN)
games = {}

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Chess Now</title>
<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<style>
body{margin:0;background:#dcecf8;font-family:Arial;color:#000;overflow-x:hidden}
.top{height:72px;display:flex;align-items:center;padding:0 28px;border-bottom:1px solid #c8d6e0}
.x{font-size:44px;margin-right:34px}.title{font-size:32px;font-weight:800}.icons{margin-left:auto;font-size:34px}
.player{display:flex;align-items:center;padding:12px 16px;min-height:88px}
.avatar{width:72px;height:72px;border-radius:50%;object-fit:cover;background:#ccc}
.info{margin-left:12px;font-size:22px;font-weight:800}.rate{font-size:18px;font-weight:400;margin-top:4px}
.timer{margin-left:auto;background:#cfe0ee;border-radius:16px;padding:14px 22px;font-size:28px;font-weight:900}
.board{width:100vw;height:100vw;position:relative;touch-action:none}
.square{position:absolute;width:12.5%;height:12.5%}
.light{background:#f0d9b5}.dark{background:#b88762}
.piece{position:absolute;width:12.5%;height:12.5%;display:flex;align-items:center;justify-content:center;user-select:none;touch-action:none;transition:transform .12s linear}
.piece img{width:88%;height:88%;pointer-events:none}
.sel{box-shadow:inset 0 0 0 5px #d8c52c}
.move::after{content:"";width:26px;height:26px;background:rgba(90,90,90,.35);border-radius:50%;position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)}
.last{background:#d7c52d!important}
.check{background:#e35b5b!important}
.msg{text-align:center;font-size:22px;margin:10px}
.wait{height:calc(100vh - 72px);display:flex;align-items:center;justify-content:center;flex-direction:column;color:#999;font-size:22px}
.loader{margin-top:18px;width:28px;height:28px;border:4px solid #c6cfd6;border-top-color:#777;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="top"><div class="x">×</div><div class="title">Chess Now</div><div class="icons">⌄ ⋮</div></div>

<div id="waitBox" class="wait" style="display:none">
  <img class="avatar" id="waitAvatar">
  <div style="margin-top:15px">Waiting for opponent to join</div>
  <div class="loader"></div>
</div>

<div id="gameBox">
  <div class="player">
    <img class="avatar" id="topAvatar">
    <div class="info" id="topName">Opponent<div class="rate">1200</div></div>
    <div class="timer" id="topTimer">◷ 00:00</div>
  </div>

  <div class="board" id="board"></div>

  <div class="player">
    <img class="avatar" id="bottomAvatar">
    <div class="info" id="bottomName">Me<div class="rate">1200</div></div>
    <div class="timer" id="bottomTimer">◷ 00:00</div>
  </div>

  <div class="msg" id="msg">Loading...</div>
</div>

<script>
const socket = io();
const GAME_ID="{{ game_id }}";
const ROLE="{{ role }}";

let whiteName="{{ white_name }}";
let blackName="{{ black_name }}";
let whiteAvatar="{{ white_avatar }}";
let blackAvatar="{{ black_avatar }}";

let boardData=null;
let turn="w";
let over=false;
let selected=null;
let legal=[];
let dragging=null;
let lastMove=[];
let checkSquare=null;

const boardEl=document.getElementById("board");
const pieceBase="https://cdn.jsdelivr.net/gh/lichess-org/lila@master/public/piece/cburnett/";

function setupNames(){
  if(ROLE==="w"){
    topAvatar.src=blackAvatar; topName.innerHTML=blackName+'<div class="rate">1200</div>';
    bottomAvatar.src=whiteAvatar; bottomName.innerHTML=whiteName+'<div class="rate">1200</div>';
    waitAvatar.src=whiteAvatar;
  }else{
    topAvatar.src=whiteAvatar; topName.innerHTML=whiteName+'<div class="rate">1200</div>';
    bottomAvatar.src=blackAvatar; bottomName.innerHTML=blackName+'<div class="rate">1200</div>';
    waitAvatar.src=blackAvatar;
  }
}

function fmt(s){
  s=Math.max(0,Math.floor(s));
  let m=Math.floor(s/60),r=s%60;
  return String(m).padStart(2,"0")+":"+String(r).padStart(2,"0")
}

function visualToSq(r,c){
  const f=["a","b","c","d","e","f","g","h"];
  return ROLE==="w"?f[c]+(8-r):f[7-c]+(r+1)
}

function pos(r,c){return `translate(${c*100}%,${r*100}%)`}
function getPiece(r,c){return ROLE==="w"?boardData[r][c]:boardData[7-r][7-c]}

function drawSquares(){
  boardEl.innerHTML="";
  for(let r=0;r<8;r++)for(let c=0;c<8;c++){
    let d=document.createElement("div");
    let sq=visualToSq(r,c);
    d.className="square "+(((r+c)%2==0)?"light":"dark");
    if(selected===sq)d.classList.add("sel");
    if(legal.includes(sq))d.classList.add("move");
    if(lastMove.includes(sq))d.classList.add("last");
    if(checkSquare===sq)d.classList.add("check");
    d.style.transform=pos(r,c);
    d.onclick=()=>tapSquare(sq);
    boardEl.appendChild(d);
  }
}

function drawPieces(){
  for(let r=0;r<8;r++)for(let c=0;c<8;c++){
    let p=getPiece(r,c);
    if(!p)continue;
    let sq=visualToSq(r,c);
    let el=document.createElement("div");
    el.className="piece";
    el.style.transform=pos(r,c);
    el.onclick=(e)=>{e.stopPropagation();tapSquare(sq);};
    el.onpointerdown=(e)=>startDrag(e,el,sq);

    let img=document.createElement("img");
    img.src=pieceBase+(p.color==="w"?"w":"b")+p.type.toUpperCase()+".svg";
    el.appendChild(img);

    boardEl.appendChild(el);
  }
}

function render(){drawSquares();if(boardData)drawPieces();}

function tapSquare(sq){
  if(over)return;
  if((ROLE==="w"&&turn!=="w")||(ROLE==="b"&&turn!=="b"))return;
  if(selected){
    socket.emit("move",{game:GAME_ID,from:selected,to:sq,role:ROLE});
    selected=null;legal=[];
    return;
  }
  socket.emit("legal",{game:GAME_ID,square:sq,role:ROLE});
}

function startDrag(e,el,sq){
  if(selected && selected !== sq){
    socket.emit("move",{game:GAME_ID,from:selected,to:sq,role:ROLE});
    selected=null;legal=[];
    return;
  }
  if(over)return;
  if((ROLE==="w"&&turn!=="w")||(ROLE==="b"&&turn!=="b"))return;
  selected=sq;
  socket.emit("legal",{game:GAME_ID,square:sq,role:ROLE});
  dragging={el,sq};
  el.style.transition="none";
  el.setPointerCapture(e.pointerId);
  moveDrag(e);
  el.onpointermove=moveDrag;
  el.onpointerup=endDrag;
}

function moveDrag(e){
  if(!dragging)return;
  const rect=boardEl.getBoundingClientRect();
  const size=rect.width/8;
  const x=e.clientX-rect.left-size/2;
  const y=e.clientY-rect.top-size/2;
  dragging.el.style.transform=`translate(${x}px,${y}px)`;
}

function endDrag(e){
  if(!dragging)return;
  const rect=boardEl.getBoundingClientRect();
  const size=rect.width/8;
  let c=Math.floor((e.clientX-rect.left)/size);
  let r=Math.floor((e.clientY-rect.top)/size);
  c=Math.max(0,Math.min(7,c)); r=Math.max(0,Math.min(7,r));
  const to=visualToSq(r,c);
  socket.emit("move",{game:GAME_ID,from:dragging.sq,to:to,role:ROLE});
  dragging.el.style.transition="transform .12s linear";
  dragging=null; selected=null; legal=[];
}

socket.on("connect",()=>socket.emit("join_game",{game:GAME_ID,role:ROLE}));

socket.on("state",(d)=>{
  boardData=d.board; turn=d.turn; over=d.over;
  whiteName=d.white_name; blackName=d.black_name;
  whiteAvatar=d.white_avatar; blackAvatar=d.black_avatar;
  lastMove=d.last_move || [];
  checkSquare=d.check_square || null;

  setupNames();

  if(d.status==="waiting"){
    waitBox.style.display="flex";
    gameBox.style.display="none";
    return;
  }

  waitBox.style.display="none";
  gameBox.style.display="block";

  if(ROLE==="w"){
    topTimer.innerText="◷ "+fmt(d.black_time);
    bottomTimer.innerText="◷ "+fmt(d.white_time);
  }else{
    topTimer.innerText="◷ "+fmt(d.white_time);
    bottomTimer.innerText="◷ "+fmt(d.black_time);
  }

  msg.innerText=d.message;
  render();

  if(checkSquare){
    setTimeout(()=>{checkSquare=null;render();},650);
  }
});

socket.on("legal_moves",(d)=>{selected=d.square;legal=d.moves;render()});

setupNames();
setInterval(()=>socket.emit("get_state",{game:GAME_ID}),700);
</script>
</body>
</html>
"""

def get_game(game_id, minutes=10):
    if game_id not in games:
        games[game_id]={
            "board":chess.Board(),
            "white_time":minutes*60,
            "black_time":minutes*60,
            "last":time.time(),
            "minutes":minutes,
            "status":"waiting",
            "white_name":"fadi",
            "black_name":"Opponent",
            "white_avatar":"https://i.imgur.com/8Km9tLL.jpeg",
            "black_avatar":"https://i.imgur.com/8Km9tLL.jpeg",
            "last_move":[],
        }
    return games[game_id]

def update_clock(g):
    if g["status"]!="playing":
        g["last"]=time.time()
        return
    now=time.time()
    diff=now-g["last"]
    if not g["board"].is_game_over():
        if g["board"].turn==chess.WHITE:g["white_time"]-=diff
        else:g["black_time"]-=diff
    g["last"]=now

def board_json(board):
    out=[]
    for r in range(8):
        row=[]
        for c in range(8):
            sq=chess.square(c,7-r)
            p=board.piece_at(sq)
            row.append({"type":p.symbol().lower(),"color":"w" if p.color==chess.WHITE else "b"} if p else None)
        out.append(row)
    return out

def check_square(board):
    if not board.is_check():
        return None
    king_sq=board.king(board.turn)
    return chess.square_name(king_sq) if king_sq is not None else None

def emit_state(game_id):
    g=get_game(game_id)
    update_clock(g)
    b=g["board"]

    if g["status"]=="waiting":
        msg="Waiting for opponent to join"; over=False
    elif g["white_time"]<=0:
        msg="انتهى وقت الأبيض"; over=True
    elif g["black_time"]<=0:
        msg="انتهى وقت الأسود"; over=True
    elif b.is_checkmate():
        msg="كش مات"; over=True
    elif b.is_stalemate():
        msg="تعادل"; over=True
    else:
        msg="دور الأبيض" if b.turn==chess.WHITE else "دور الأسود"; over=False

    socketio.emit("state",{
        "board":board_json(b),
        "turn":"w" if b.turn==chess.WHITE else "b",
        "white_time":int(g["white_time"]),
        "black_time":int(g["black_time"]),
        "message":msg,
        "over":over,
        "status":g["status"],
        "white_name":g["white_name"],
        "black_name":g["black_name"],
        "white_avatar":g["white_avatar"],
        "black_avatar":g["black_avatar"],
        "last_move":g.get("last_move",[]),
        "check_square":check_square(b),
    }, room=game_id)

@app.route("/")
def home():
    game_id=request.args.get("game","solo")
    role=request.args.get("role","w")
    minutes=int(request.args.get("time","10"))

    g=get_game(game_id,minutes)

    white_name=request.args.get("white_name")
    white_avatar=request.args.get("white_avatar")

    if white_name:
        g["white_name"]=white_name
    if white_avatar:
        g["white_avatar"]=white_avatar

    return render_template_string(
        HTML,
        game_id=game_id,
        role=role,
        white_name=g["white_name"],
        black_name=g["black_name"],
        white_avatar=g["white_avatar"],
        black_avatar=g["black_avatar"]
    )

@socketio.on("join_game")
def ws_join(data):
    game=data.get("game","solo")
    join_room(game)
    emit_state(game)

@socketio.on("get_state")
def ws_state(data):
    emit_state(data.get("game","solo"))

@socketio.on("legal")
def ws_legal(data):
    game=data.get("game","solo")
    sq_name=data.get("square","")
    role=data.get("role","w")
    g=get_game(game)
    b=g["board"]
    if g["status"]!="playing":
        return emit("legal_moves",{"square":sq_name,"moves":[]})
    try:
        sq=chess.parse_square(sq_name)
    except:
        return emit("legal_moves",{"square":sq_name,"moves":[]})
    p=b.piece_at(sq)
    if not p:
        return emit("legal_moves",{"square":sq_name,"moves":[]})
    if (role=="w" and (b.turn!=chess.WHITE or p.color!=chess.WHITE)) or (role=="b" and (b.turn!=chess.BLACK or p.color!=chess.BLACK)):
        return emit("legal_moves",{"square":sq_name,"moves":[]})
    moves=[chess.square_name(m.to_square) for m in b.legal_moves if m.from_square==sq]
    emit("legal_moves",{"square":sq_name,"moves":moves})

@socketio.on("move")
def ws_move(data):
    game=data.get("game","solo")
    frm=data.get("from")
    to=data.get("to")
    role=data.get("role","w")
    g=get_game(game)
    update_clock(g)
    b=g["board"]
    if g["status"]!="playing":
        return
    if (role=="w" and b.turn!=chess.WHITE) or (role=="b" and b.turn!=chess.BLACK):
        return
    try:
        mv=chess.Move.from_uci(frm+to)
        if mv not in b.legal_moves:
            mv=chess.Move.from_uci(frm+to+"q")
        if mv in b.legal_moves:
            b.push(mv)
            g["last_move"]=[frm,to]
            g["last"]=time.time()
            emit_state(game)
    except:
        pass

@app.route("/avatar")
def avatar_proxy():
    path=request.args.get("path","")
    if not path:return "",404
    try:
        data=urllib.request.urlopen(f"https://api.telegram.org/file/bot{TOKEN}/{path}",timeout=10).read()
        return Response(data,mimetype="image/jpeg")
    except:
        return "",404

def get_avatar_url(user_id):
    try:
        photos=bot.get_user_profile_photos(user_id,limit=1)
        if photos.total_count>0:
            file_id=photos.photos[0][-1].file_id
            file_info=bot.get_file(file_id)
            path=urllib.parse.quote(file_info.file_path)
            return f"{WEB_LINK}/avatar?path={path}"
    except:
        pass
    return "https://i.imgur.com/8Km9tLL.jpeg"

@bot.message_handler(commands=["start"])
def start(message):
    parts=message.text.split(maxsplit=1)

    if len(parts)>1 and parts[1].startswith("join_"):
        game_id=parts[1].replace("join_","")
        g=get_game(game_id)

        user=message.from_user
        name=user.first_name or "Opponent"
        if user.username:
            name=f"{name} (@{user.username})"

        avatar=get_avatar_url(user.id)
        g["black_name"]=name
        g["black_avatar"]=avatar
        g["status"]="playing"
        g["last"]=time.time()

        link=f"{WEB_LINK}/?game={game_id}&role=b&time={g['minutes']}"
        kb=InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Open Game",url=link))

        bot.send_message(message.chat.id,"تم دخولك للمباراة ✅\nاضغط Open Game",reply_markup=kb)
        return

    kb=InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Play",switch_inline_query=""))
    bot.send_message(message.chat.id,"Want to play chess with any contact from Telegram?\nClick Play and choose a chat.",reply_markup=kb)

@bot.inline_handler(func=lambda q: True)
def inline_query(query):
    user=query.from_user
    name=user.first_name or "Player"
    if user.username:
        name=f"{name} (@{user.username})"
    avatar=get_avatar_url(user.id)

    modes=[
        ("bullet","Bullet (1|0)","Timer: 1 min + 0 sec. Random color.","1"),
        ("blitz","Blitz (3|2)","Timer: 3 min + 2 sec. Random color.","3"),
        ("rapid","Rapid (10|5)","Timer: 10 min + 5 sec. Random color.","10")
    ]

    results=[]
    for mid,title,desc,minutes in modes:
        game_id=f"{user.id}_{int(time.time())}_{mid}"
        g=get_game(game_id,int(minutes))
        g["white_name"]=name
        g["white_avatar"]=avatar

        join_deep=f"https://t.me/{BOT_USERNAME}?start=join_{game_id}"

        kb=InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Join",url=join_deep))

        text=f"User {name} wants to play chess.\\n\\nGame Rules: {desc}\\n\\nClick Join to enter the game."

        results.append(
            InlineQueryResultArticle(
                id=game_id,
                title=title,
                description=desc,
                input_message_content=InputTextMessageContent(text),
                reply_markup=kb
            )
        )

    bot.answer_inline_query(query.id,results,cache_time=1,is_personal=True)

@bot.chosen_inline_handler(func=lambda chosen: True)
def chosen_inline(chosen):
    try:
        game_id=chosen.result_id
        g=get_game(game_id)

        safe_name=urllib.parse.quote(g["white_name"])
        safe_avatar=urllib.parse.quote(g["white_avatar"],safe=":/?=&.%")
        link=f"{WEB_LINK}/?game={game_id}&role=w&time={g['minutes']}&white_name={safe_name}&white_avatar={safe_avatar}"

        kb=InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Open Waiting Room",url=link))

        bot.send_message(chosen.from_user.id,"تم إنشاء مباراة ✅\nافتح غرفة الانتظار:",reply_markup=kb)
    except:
        pass

def run_bot():
    try:
        bot.remove_webhook()
    except:
        pass
    bot.infinity_polling(skip_pending=True)

threading.Thread(target=run_bot,daemon=True).start()

if __name__=="__main__":
    port=int(os.environ.get("PORT",8080))
    socketio.run(app,host="0.0.0.0",port=port)
