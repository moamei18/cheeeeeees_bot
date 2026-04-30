from flask import Flask, request, render_template_string, Response
from flask_socketio import SocketIO, join_room, emit
import os, time, threading, urllib.parse, urllib.request
import chess
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8526200321:AAESExoSdMi5WOzT-DwvfcYOVYjOndv-dPE"
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
<title>Fadi Chess</title>
<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<style>
body{margin:0;background:#dcecf8;font-family:Arial;color:#000;overflow:hidden}
.screen{height:100vh;display:flex;align-items:center;justify-content:center;flex-direction:column}
.home{background:#111827;color:white;text-align:left;padding:35px;width:100%;height:100vh;box-sizing:border-box}
.home h1{font-size:42px;margin:45px 0 5px}
.home p{font-size:22px;color:#cbd5e1;margin:0 0 25px}
.play{background:#2f6fc7;color:white;border:2px solid #7db4ff;border-radius:16px;font-size:34px;font-weight:900;padding:12px 38px}
.modes button,.share{background:#2f6fc7;color:white;border:0;border-radius:14px;font-size:22px;font-weight:800;padding:15px;margin:9px;width:85%}
.wait{color:#888;font-size:22px}
.loader{margin-top:18px;width:30px;height:30px;border:4px solid #c6cfd6;border-top-color:#666;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.top{height:72px;display:flex;align-items:center;padding:0 28px;border-bottom:1px solid #c8d6e0}
.x{font-size:44px;margin-right:34px}.title{font-size:32px;font-weight:900}.icons{margin-left:auto;font-size:34px}
.player{display:flex;align-items:center;padding:12px 16px;min-height:88px}
.avatar{width:72px;height:72px;border-radius:50%;object-fit:cover;background:#ccc}
.info{margin-left:12px;font-size:22px;font-weight:900}.rate{font-size:18px;font-weight:400;margin-top:4px}
.timer{margin-left:auto;background:#cfe0ee;border-radius:16px;padding:14px 22px;font-size:28px;font-weight:900}
.board{width:100vw;height:100vw;position:relative;touch-action:none}
.square{position:absolute;width:12.5%;height:12.5%}
.light{background:#f0d9b5}.dark{background:#b88762}
.piece{position:absolute;width:12.5%;height:12.5%;display:flex;align-items:center;justify-content:center;user-select:none;touch-action:none;transition:transform .06s linear;z-index:5}
.piece img{width:88%;height:88%;pointer-events:none}
.sel{box-shadow:inset 0 0 0 5px #d8c52c}
.move::after{content:"";width:25px;height:25px;background:rgba(80,80,80,.35);border-radius:50%;position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)}
.last{background:#d7c52d!important}
.check{background:#e35b5b!important}
.msg{text-align:center;font-size:22px;margin:8px}
</style>
</head>
<body>

<div id="home" class="home">
  <h1>Fadi Chess</h1>
  <p>Play chess with friends</p>
  <button class="play" onclick="showModes()">▶ PLAY</button>
  <div style="margin-top:35px;color:#f7c948;font-size:22px;font-weight:bold">♟ Challenge • Think • Win</div>
</div>

<div id="modes" class="screen modes" style="display:none">
  <h1>اختر الوقت</h1>
  <button onclick="createGame(1)">Bullet 1:00</button>
  <button onclick="createGame(3)">Blitz 3:00</button>
  <button onclick="createGame(10)">Rapid 10:00</button>
</div>

<div id="wait" class="screen wait" style="display:none">
  <img class="avatar" id="waitAvatar">
  <div style="margin-top:15px">Waiting for opponent to join</div>
  <button class="share" onclick="shareGame()">🔗 إرسال الدعوة</button>
  <div class="loader"></div>
</div>

<div id="game" style="display:none">
  <div class="top"><div class="x">×</div><div class="title">Chess Now</div><div class="icons">⌄ ⋮</div></div>
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
const socket=io();
let GAME_ID="{{ game_id }}";
let ROLE="{{ role }}";
let MINUTES={{ minutes }};

let boardData=null, turn="w", over=false, selected=null, legal=[], dragging=null;
let lastMove=[], checkSquare=null;

const boardEl=document.getElementById("board");
const pieceBase="https://cdn.jsdelivr.net/gh/lichess-org/lila@master/public/piece/cburnett/";

function showOnly(id){
  ["home","modes","wait","game"].forEach(x=>document.getElementById(x).style.display="none");
  document.getElementById(id).style.display=id==="game"?"block":"flex";
  if(id==="home")document.getElementById(id).style.display="block";
}

function showModes(){showOnly("modes")}

function createGame(m){
  GAME_ID=Date.now().toString();
  ROLE="w";
  MINUTES=m;
  history.replaceState(null,"",`/?game=${GAME_ID}&role=w&time=${m}`);
  socket.emit("create_game",{game:GAME_ID,time:m,role:"w"});
  showOnly("wait");
}

function shareGame(){
  const joinLink=`${location.origin}/?game=${GAME_ID}&role=b&time=${MINUTES}`;
  const text="تعال العب شطرنج وياي ♟";
  window.open(`https://t.me/share/url?url=${encodeURIComponent(joinLink)}&text=${encodeURIComponent(text)}`,"_blank");
}

function fmt(s){s=Math.max(0,Math.floor(s));let m=Math.floor(s/60),r=s%60;return String(m).padStart(2,"0")+":"+String(r).padStart(2,"0")}
function visualToSq(r,c){const f=["a","b","c","d","e","f","g","h"];return ROLE==="w"?f[c]+(8-r):f[7-c]+(r+1)}
function pos(r,c){return `translate(${c*100}%,${r*100}%)`}
function getPiece(r,c){return ROLE==="w"?boardData[r][c]:boardData[7-r][7-c]}

function drawSquares(){
  boardEl.innerHTML="";
  for(let r=0;r<8;r++)for(let c=0;c<8;c++){
    let sq=visualToSq(r,c), d=document.createElement("div");
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
    let p=getPiece(r,c); if(!p)continue;
    let sq=visualToSq(r,c);
    let el=document.createElement("div");
    el.className="piece";
    el.style.transform=pos(r,c);
    el.onclick=(e)=>{e.stopPropagation();tapSquare(sq)};
    el.onpointerdown=(e)=>startDrag(e,el,sq);
    let img=document.createElement("img");
    img.src=pieceBase+(p.color==="w"?"w":"b")+p.type.toUpperCase()+".svg";
    el.appendChild(img);
    boardEl.appendChild(el);
  }
}

function render(){drawSquares();if(boardData)drawPieces()}

function tapSquare(sq){
  if(over)return;
  if((ROLE==="w"&&turn!=="w")||(ROLE==="b"&&turn!=="b"))return;
  if(selected){
    socket.emit("move",{game:GAME_ID,from:selected,to:sq,role:ROLE});
    selected=null;legal=[];return;
  }
  socket.emit("legal",{game:GAME_ID,square:sq,role:ROLE});
}

function startDrag(e,el,sq){
  if(selected&&selected!==sq){
    socket.emit("move",{game:GAME_ID,from:selected,to:sq,role:ROLE});
    selected=null;legal=[];return;
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
  const rect=boardEl.getBoundingClientRect(), size=rect.width/8;
  dragging.el.style.transform=`translate(${e.clientX-rect.left-size/2}px,${e.clientY-rect.top-size/2}px)`;
}

function endDrag(e){
  if(!dragging)return;
  const rect=boardEl.getBoundingClientRect(), size=rect.width/8;
  let c=Math.floor((e.clientX-rect.left)/size), r=Math.floor((e.clientY-rect.top)/size);
  c=Math.max(0,Math.min(7,c)); r=Math.max(0,Math.min(7,r));
  socket.emit("move",{game:GAME_ID,from:dragging.sq,to:visualToSq(r,c),role:ROLE});
  dragging.el.style.transition="transform .06s linear";
  dragging=null;selected=null;legal=[];
}

socket.on("connect",()=>{
  if(GAME_ID && GAME_ID!=="new"){
    socket.emit("join_game",{game:GAME_ID,role:ROLE,time:MINUTES});
  }
});

socket.on("state",(d)=>{
  boardData=d.board; turn=d.turn; over=d.over;
  lastMove=d.last_move||[]; checkSquare=d.check_square||null;

  topAvatar.src=d.top_avatar;
  bottomAvatar.src=d.bottom_avatar;
  waitAvatar.src=d.bottom_avatar;
  topName.innerHTML=d.top_name+'<div class="rate">1200</div>';
  bottomName.innerHTML=d.bottom_name+'<div class="rate">1200</div>';

  if(d.status==="waiting"){showOnly("wait");return}
  showOnly("game");

  topTimer.innerText="◷ "+fmt(d.top_time);
  bottomTimer.innerText="◷ "+fmt(d.bottom_time);
  msg.innerText=d.message;
  render();

  if(checkSquare)setTimeout(()=>{checkSquare=null;render()},450);
});

socket.on("legal_moves",(d)=>{selected=d.square;legal=d.moves;render()});

if(GAME_ID==="new"){showOnly("home")}
else{showOnly("wait")}
</script>
</body>
</html>
"""

def default_avatar():
    return "https://i.imgur.com/8Km9tLL.jpeg"

def get_game(game_id, minutes=10):
    if game_id not in games:
        games[game_id]={
            "board":chess.Board(),
            "white_time":minutes*60,
            "black_time":minutes*60,
            "last":time.time(),
            "minutes":minutes,
            "status":"waiting",
            "white_name":"White",
            "black_name":"Opponent",
            "white_avatar":default_avatar(),
            "black_avatar":default_avatar(),
            "last_move":[]
        }
    return games[game_id]

def update_clock(g):
    if g["status"]!="playing":
        g["last"]=time.time()
        return
    now=time.time(); diff=now-g["last"]
    if not g["board"].is_game_over():
        if g["board"].turn==chess.WHITE:g["white_time"]-=diff
        else:g["black_time"]-=diff
    g["last"]=now

def board_json(board):
    out=[]
    for r in range(8):
        row=[]
        for c in range(8):
            sq=chess.square(c,7-r); p=board.piece_at(sq)
            row.append({"type":p.symbol().lower(),"color":"w" if p.color==chess.WHITE else "b"} if p else None)
        out.append(row)
    return out

def check_square(board):
    if not board.is_check():return None
    k=board.king(board.turn)
    return chess.square_name(k) if k is not None else None

def emit_state(game_id):
    g=get_game(game_id); update_clock(g); b=g["board"]

    over=False
    if g["status"]=="waiting": msg="Waiting for opponent"
    elif g["white_time"]<=0: msg="انتهى وقت الأبيض"; over=True
    elif g["black_time"]<=0: msg="انتهى وقت الأسود"; over=True
    elif b.is_checkmate(): msg="كش مات"; over=True
    elif b.is_stalemate(): msg="تعادل"; over=True
    else: msg="دور الأبيض" if b.turn==chess.WHITE else "دور الأسود"

    socketio.emit("state",{
        "board":board_json(b),
        "turn":"w" if b.turn==chess.WHITE else "b",
        "over":over,
        "status":g["status"],
        "message":msg,
        "last_move":g["last_move"],
        "check_square":check_square(b),
        "top_name":g["black_name"],
        "bottom_name":g["white_name"],
        "top_avatar":g["black_avatar"],
        "bottom_avatar":g["white_avatar"],
        "top_time":int(g["black_time"]),
        "bottom_time":int(g["white_time"])
    }, room=game_id)

@app.route("/")
def home():
    game_id=request.args.get("game","new")
    role=request.args.get("role","w")
    minutes=int(request.args.get("time","10"))
    if game_id!="new": get_game(game_id,minutes)
    return render_template_string(HTML,game_id=game_id,role=role,minutes=minutes)

@socketio.on("create_game")
def create_game(data):
    g=get_game(data["game"],int(data.get("time",10)))
    join_room(data["game"])
    emit_state(data["game"])

@socketio.on("join_game")
def join_game(data):
    game=data.get("game")
    role=data.get("role","w")
    minutes=int(data.get("time",10))
    g=get_game(game,minutes)
    join_room(game)
    if role=="b":
        g["status"]="playing"
        g["last"]=time.time()
    emit_state(game)

@socketio.on("get_state")
def get_state(data):
    emit_state(data.get("game"))

@socketio.on("legal")
def legal(data):
    g=get_game(data["game"]); b=g["board"]
    sq_name=data.get("square",""); role=data.get("role","w")
    if g["status"]!="playing": return emit("legal_moves",{"square":sq_name,"moves":[]})
    try: sq=chess.parse_square(sq_name)
    except: return emit("legal_moves",{"square":sq_name,"moves":[]})
    p=b.piece_at(sq)
    if not p: return emit("legal_moves",{"square":sq_name,"moves":[]})
    if (role=="w" and (b.turn!=chess.WHITE or p.color!=chess.WHITE)) or (role=="b" and (b.turn!=chess.BLACK or p.color!=chess.BLACK)):
        return emit("legal_moves",{"square":sq_name,"moves":[]})
    moves=[chess.square_name(m.to_square) for m in b.legal_moves if m.from_square==sq]
    emit("legal_moves",{"square":sq_name,"moves":moves})

@socketio.on("move")
def move(data):
    g=get_game(data["game"]); update_clock(g); b=g["board"]
    role=data.get("role","w")
    if g["status"]!="playing": return
    if (role=="w" and b.turn!=chess.WHITE) or (role=="b" and b.turn!=chess.BLACK): return
    try:
        mv=chess.Move.from_uci(data["from"]+data["to"])
        if mv not in b.legal_moves: mv=chess.Move.from_uci(data["from"]+data["to"]+"q")
        if mv in b.legal_moves:
            b.push(mv)
            g["last_move"]=[data["from"],data["to"]]
            g["last"]=time.time()
            emit_state(data["game"])
    except: pass

@bot.message_handler(commands=["start"])
def start(msg):
    kb=InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🎮 العب الشطرنج",url=WEB_LINK))
    bot.send_message(msg.chat.id,"اضغط وابدأ لعبة شطرنج 🔥",reply_markup=kb)

def run_bot():
    try: bot.remove_webhook()
    except: pass
    bot.infinity_polling(skip_pending=True)

threading.Thread(target=run_bot,daemon=True).start()

if __name__=="__main__":
    port=int(os.environ.get("PORT",8080))
    socketio.run(app,host="0.0.0.0",port=port)
