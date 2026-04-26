from flask import Flask, request, render_template_string, Response
from flask_socketio import SocketIO, join_room, emit
import os, time, threading, urllib.parse, urllib.request
import chess
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent

TOKEN = "8526200321:AAFkQRkgzCaXvoS9uSUvmM0yGFx_S5ck0bA"
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
.piece{position:absolute;width:12.5%;height:12.5%;display:flex;align-items:center;justify-content:center;font-size:40px;font-weight:bold;line-height:1;user-select:none;touch-action:none;transition:transform .14s linear}
.white{color:white;text-shadow:0 0 2px #000,0 0 2px #000}.black{color:#000}
.sel{box-shadow:inset 0 0 0 5px #ffe066}
.move{box-shadow:inset 0 0 0 7px rgba(30,150,70,.45)}
.msg{text-align:center;font-size:22px;margin:10px}
</style>
</head>
<body>
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

<script>
const socket = io();
const GAME_ID="{{ game_id }}";
const ROLE="{{ role }}";
const whiteName="{{ white_name }}";
const blackName="{{ black_name }}";
const whiteAvatar="{{ white_avatar }}";
const blackAvatar="{{ black_avatar }}";

let boardData=null;
let turn="w";
let over=false;
let selected=null;
let legal=[];
let dragging=null;

const boardEl=document.getElementById("board");
const pieces={p:{w:"♙",b:"♟"},r:{w:"♖",b:"♜"},n:{w:"♘",b:"♞"},b:{w:"♗",b:"♝"},q:{w:"♕",b:"♛"},k:{w:"♔",b:"♚"}};

function setupNames(){
  if(ROLE==="w"){
    topAvatar.src=blackAvatar; topName.innerHTML=blackName+'<div class="rate">1200</div>';
    bottomAvatar.src=whiteAvatar; bottomName.innerHTML=whiteName+'<div class="rate">1200</div>';
  }else{
    topAvatar.src=whiteAvatar; topName.innerHTML=whiteName+'<div class="rate">1200</div>';
    bottomAvatar.src=blackAvatar; bottomName.innerHTML=blackName+'<div class="rate">1200</div>';
  }
}

function fmt(s){s=Math.max(0,Math.floor(s));let m=Math.floor(s/60),r=s%60;return String(m).padStart(2,"0")+":"+String(r).padStart(2,"0")}
function visualToSq(r,c){const f=["a","b","c","d","e","f","g","h"];return ROLE==="w"?f[c]+(8-r):f[7-c]+(r+1)}
function sqToVisual(sq){const f=["a","b","c","d","e","f","g","h"];let c=f.indexOf(sq[0]), r=8-parseInt(sq[1]); if(ROLE==="b"){r=7-r;c=7-c} return {r,c}}
function pos(r,c){return `translate(${c*100}%,${r*100}%)`}

function drawSquares(){
  boardEl.innerHTML="";
  for(let r=0;r<8;r++)for(let c=0;c<8;c++){
    let d=document.createElement("div");
    let sq=visualToSq(r,c);
    d.className="square "+(((r+c)%2==0)?"light":"dark");
    if(selected===sq)d.classList.add("sel");
    if(legal.includes(sq))d.classList.add("move");
    d.style.transform=pos(r,c);
    d.onclick=()=>tapSquare(sq);
    boardEl.appendChild(d);
  }
}

function getPiece(r,c){return ROLE==="w"?boardData[r][c]:boardData[7-r][7-c]}

function drawPieces(){
  for(let r=0;r<8;r++)for(let c=0;c<8;c++){
    let p=getPiece(r,c);
    if(!p)continue;
    let sq=visualToSq(r,c);
    let el=document.createElement("div");
    el.className="piece "+(p.color==="w"?"white":"black");
    el.innerText=pieces[p.type][p.color];
    el.style.transform=pos(r,c);
    el.dataset.square=sq;
    el.onpointerdown=(e)=>startDrag(e,el,sq);
    boardEl.appendChild(el);
  }
}

function render(){
  drawSquares();
  if(boardData)drawPieces();
}

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
  dragging.el.style.transition="transform .14s linear";
  dragging=null; selected=null; legal=[];
}

socket.on("connect",()=>socket.emit("join_game",{game:GAME_ID}));
socket.on("state",(d)=>{
  boardData=d.board; turn=d.turn; over=d.over;
  if(ROLE==="w"){topTimer.innerText="◷ "+fmt(d.black_time);bottomTimer.innerText="◷ "+fmt(d.white_time)}
  else{topTimer.innerText="◷ "+fmt(d.white_time);bottomTimer.innerText="◷ "+fmt(d.black_time)}
  msg.innerText=d.message;
  render();
});
socket.on("legal_moves",(d)=>{selected=d.square;legal=d.moves;render()});

setupNames();
setInterval(()=>socket.emit("get_state",{game:GAME_ID}),500);
</script>
</body>
</html>
"""

def get_game(game_id, minutes=10):
    if game_id not in games:
        games[game_id]={"board":chess.Board(),"white_time":minutes*60,"black_time":minutes*60,"last":time.time(),"minutes":minutes}
    return games[game_id]

def update_clock(g):
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

def emit_state(game_id):
    g=get_game(game_id); update_clock(g); b=g["board"]
    if g["white_time"]<=0: msg="انتهى وقت الأبيض"; over=True
    elif g["black_time"]<=0: msg="انتهى وقت الأسود"; over=True
    elif b.is_checkmate(): msg="كش مات"; over=True
    elif b.is_stalemate(): msg="تعادل"; over=True
    else: msg="دور الأبيض" if b.turn==chess.WHITE else "دور الأسود"; over=False
    socketio.emit("state",{
        "board":board_json(b),"turn":"w" if b.turn==chess.WHITE else "b",
        "white_time":int(g["white_time"]),"black_time":int(g["black_time"]),
        "message":msg,"over":over
    }, room=game_id)

@app.route("/")
def home():
    game_id=request.args.get("game","solo"); role=request.args.get("role","w")
    minutes=int(request.args.get("time","10"))
    white_name=request.args.get("white_name","fadi"); black_name=request.args.get("black_name","Opponent")
    white_avatar=request.args.get("white_avatar","https://i.imgur.com/8Km9tLL.jpeg")
    black_avatar=request.args.get("black_avatar","https://i.imgur.com/8Km9tLL.jpeg")
    get_game(game_id,minutes)
    return render_template_string(HTML,game_id=game_id,role=role,white_name=white_name,black_name=black_name,white_avatar=white_avatar,black_avatar=black_avatar)

@socketio.on("join_game")
def ws_join(data):
    game=data.get("game","solo"); join_room(game); emit_state(game)

@socketio.on("get_state")
def ws_state(data):
    emit_state(data.get("game","solo"))

@socketio.on("legal")
def ws_legal(data):
    game=data.get("game","solo"); sq_name=data.get("square",""); role=data.get("role","w")
    g=get_game(game); b=g["board"]
    try:sq=chess.parse_square(sq_name)
    except:return emit("legal_moves",{"square":sq_name,"moves":[]})
    p=b.piece_at(sq)
    if not p:return emit("legal_moves",{"square":sq_name,"moves":[]})
    if (role=="w" and (b.turn!=chess.WHITE or p.color!=chess.WHITE)) or (role=="b" and (b.turn!=chess.BLACK or p.color!=chess.BLACK)):
        return emit("legal_moves",{"square":sq_name,"moves":[]})
    moves=[chess.square_name(m.to_square) for m in b.legal_moves if m.from_square==sq]
    emit("legal_moves",{"square":sq_name,"moves":moves})

@socketio.on("move")
def ws_move(data):
    game=data.get("game","solo"); frm=data.get("from"); to=data.get("to"); role=data.get("role","w")
    g=get_game(game); update_clock(g); b=g["board"]
    if (role=="w" and b.turn!=chess.WHITE) or (role=="b" and b.turn!=chess.BLACK): return
    try:
        mv=chess.Move.from_uci(frm+to)
        if mv not in b.legal_moves: mv=chess.Move.from_uci(frm+to+"q")
        if mv in b.legal_moves:
            b.push(mv); g["last"]=time.time(); emit_state(game)
    except: pass

@app.route("/avatar")
def avatar_proxy():
    path=request.args.get("path","")
    if not path:return "",404
    try:
        data=urllib.request.urlopen(f"https://api.telegram.org/file/bot{TOKEN}/{path}",timeout=10).read()
        return Response(data,mimetype="image/jpeg")
    except:return "",404

def get_avatar_url(user_id):
    try:
        photos=bot.get_user_profile_photos(user_id,limit=1)
        if photos.total_count>0:
            file_id=photos.photos[0][-1].file_id
            file_info=bot.get_file(file_id)
            path=urllib.parse.quote(file_info.file_path)
            return f"{WEB_LINK}/avatar?path={path}"
    except: pass
    return "https://i.imgur.com/8Km9tLL.jpeg"

@bot.message_handler(commands=["start"])
def start(message):
    kb=InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Play",switch_inline_query=""))
    bot.send_message(message.chat.id,"Want to play chess with any contact from Telegram?\nClick Play and choose a chat.",reply_markup=kb)

@bot.inline_handler(func=lambda q: True)
def inline_query(query):
    user=query.from_user; name=user.first_name or "Player"; avatar=get_avatar_url(user.id)
    safe_name=urllib.parse.quote(name); safe_avatar=urllib.parse.quote(avatar,safe=":/?=&.%")
    modes=[("bullet","Bullet (1|0)","Timer: 1 min + 0 sec. Random color.","1"),("blitz","Blitz (3|2)","Timer: 3 min + 2 sec. Random color.","3"),("rapid","Rapid (10|5)","Timer: 10 min + 5 sec. Random color.","10")]
    results=[]
    for mid,title,desc,minutes in modes:
        game_id=f"{user.id}_{int(time.time())}_{mid}"
        start_link=f"{WEB_LINK}/?game={game_id}&role=w&time={minutes}&white_name={safe_name}&white_avatar={safe_avatar}&black_name=Opponent"
        join_link=f"{WEB_LINK}/?game={game_id}&role=b&time={minutes}&white_name={safe_name}&white_avatar={safe_avatar}&black_name=Opponent"
        kb=InlineKeyboardMarkup(); kb.add(InlineKeyboardButton("Start",url=start_link)); kb.add(InlineKeyboardButton("Join",url=join_link))
        text=f"User {name} wants to play chess.\n\nGame Rules: {desc}\n\nPress Start if you created it, or Join if you are the opponent."
        results.append(InlineQueryResultArticle(id=game_id,title=title,description=desc,input_message_content=InputTextMessageContent(text),reply_markup=kb))
    bot.answer_inline_query(query.id,results,cache_time=1,is_personal=True)

def run_bot():
    try: bot.remove_webhook()
    except: pass
    bot.infinity_polling(skip_pending=True)

threading.Thread(target=run_bot,daemon=True).start()

if __name__=="__main__":
    port=int(os.environ.get("PORT",8080))
    socketio.run(app,host="0.0.0.0",port=port)
