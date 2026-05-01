from flask import Flask, request, render_template_string, jsonify, Response
from flask_socketio import SocketIO, join_room, emit
import os, time, threading, urllib.parse, urllib.request
import chess
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8526200321:AAEJcRb8Mor8YJKsLGfPs1DXmJDW8O0iT6M"
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
<script src="https://telegram.org/js/telegram-web-app.js"></script>
<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<style>
*{box-sizing:border-box}
body{margin:0;background:#0f172a;font-family:Arial;color:#eaf2ff;overflow:hidden}
.screen{height:100vh;display:flex;align-items:center;justify-content:center;flex-direction:column}
.home{background:#111827;color:white;text-align:left;padding:35px;width:100%;height:100vh}
.home h1{font-size:42px;margin:45px 0 5px}.home p{font-size:22px;color:#cbd5e1;margin:0 0 25px}
.play{background:#2f6fc7;color:white;border:2px solid #7db4ff;border-radius:16px;font-size:30px;font-weight:900;padding:12px 38px}
.modes button,.share{background:#2f6fc7;color:white;border:0;border-radius:14px;font-size:22px;font-weight:800;padding:15px;margin:9px;width:85%}
.wait{color:#888;font-size:22px;background:#dcecf8}.loader{margin-top:18px;width:30px;height:30px;border:4px solid #c6cfd6;border-top-color:#666;border-radius:50%;animation:spin 1s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.top{height:72px;display:flex;align-items:center;padding:0 28px;border-bottom:1px solid #263246;background:#111827;color:#fff}
.x{font-size:44px;margin-right:34px}.title{font-size:32px;font-weight:900}.icons{margin-left:auto;font-size:34px;display:flex;align-items:center;gap:18px}
.musicBtn{width:50px;height:50px;border-radius:50%;border:2px solid #60a5fa;background:#2563eb;color:white;font-size:28px;font-weight:900}
.player{display:flex;align-items:center;padding:12px 16px;min-height:88px;background:#111827;color:#fff}
.avatar{width:72px;height:72px;border-radius:50%;object-fit:cover;background:#334155}
.info{margin-left:12px;font-size:22px;font-weight:900}.rate{font-size:18px;font-weight:400;margin-top:4px;color:#cbd5e1}
.timer{margin-left:auto;background:#dbeafe;color:#020617;border-radius:16px;padding:14px 22px;font-size:28px;font-weight:900}
.board{width:100vw;height:100vw;position:relative;touch-action:none}
.square{position:absolute;width:12.5%;height:12.5%}.light{background:#dbeafe}.dark{background:#7294bd}
.piece{position:absolute;width:12.5%;height:12.5%;display:flex;align-items:center;justify-content:center;user-select:none;touch-action:none;transition:transform .06s linear;z-index:5}
.piece img{width:88%;height:88%;pointer-events:none}.sel{box-shadow:inset 0 0 0 5px #facc15}
.move::after{content:"";width:25px;height:25px;background:rgba(80,80,80,.35);border-radius:50%;position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)}
.last{background:#eab308!important}.check{background:#ef4444!important}.msg{text-align:center;font-size:22px;margin:8px;color:#e5e7eb}
.musicPanel{position:absolute;right:10px;top:85px;width:340px;max-width:94vw;background:#111827;border:1px solid #475569;border-radius:14px;padding:14px;z-index:20;display:none;box-shadow:0 15px 45px #0008;color:white}
.musicHead{display:flex;align-items:center;font-size:22px;font-weight:900;margin-bottom:12px}.closeM{margin-left:auto;font-size:28px;cursor:pointer}
.searchRow{display:flex;gap:8px}.search{flex:1;background:#0f172a;border:1px solid #475569;border-radius:12px;padding:13px;color:white;font-size:17px;margin-bottom:12px}
.searchBtn{background:#2563eb;color:white;border:0;border-radius:12px;padding:0 14px;font-size:20px;height:48px}
.song{display:flex;align-items:center;gap:10px;background:#1e293b;margin:8px 0;padding:9px;border-radius:12px}
.cover{width:48px;height:48px;border-radius:9px;object-fit:cover;background:#334155}.songInfo{flex:1}.songInfo b{display:block;color:white;font-size:15px}.songInfo span{color:#94a3b8;font-size:13px}
.playSmall{background:none;border:0;color:#e5e7eb;font-size:25px}.now{border-top:1px solid #475569;margin-top:12px;padding-top:12px;display:flex;align-items:center;gap:10px}
.progress{width:100%;accent-color:#2563eb}
@media(max-width:650px){.musicPanel{left:10px;right:10px;width:auto}.top{height:64px}.title{font-size:30px}.musicBtn{width:46px;height:46px}}
</style>
</head>
<body>

<div id="home" class="home">
  <h1>Fadi Chess</h1>
  <p>Play chess with friends</p>
  <button class="play" onclick="showModes()">▶ PLAY</button>
  <div style="margin-top:35px;color:#f7c948;font-size:22px;font-weight:bold">♟ Challenge • Think • Win</div>
</div>

<div id="modes" class="screen modes" style="display:none;background:#dcecf8;color:#000">
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
  <div class="top">
    <div class="x">×</div><div class="title">Chess Now</div>
    <div class="icons"><span>⌄</span><span>⋮</span><button class="musicBtn" onclick="toggleMusic()">♫</button></div>
  </div>
  <div class="player"><img class="avatar" id="topAvatar"><div class="info" id="topName">Opponent<div class="rate">1200</div></div><div class="timer" id="topTimer">◷ 00:00</div></div>
  <div class="board" id="board"></div>
  <div class="player"><img class="avatar" id="bottomAvatar"><div class="info" id="bottomName">Me<div class="rate">1200</div></div><div class="timer" id="bottomTimer">◷ 00:00</div></div>
  <div class="msg" id="msg">Loading...</div>
</div>

<div class="musicPanel" id="musicPanel">
  <div class="musicHead">🎵 Music Player <span class="closeM" onclick="toggleMusic()">×</span></div>
  <div class="searchRow">
    <input class="search" id="musicSearch" placeholder="اكتب اسم الأغنية...">
    <button class="searchBtn" onclick="searchMusic()">🔍</button>
  </div>
  <div style="color:#cbd5e1;margin:8px 0">نتائج البحث</div>
  <div id="songList"></div>
  <div class="now">
    <img class="cover" id="nowCover">
    <div style="flex:1">
      <b id="nowTitle">اختر أغنية</b>
      <span id="nowArtist">تشتغل لك وحدك فقط</span>
      <input class="progress" id="progress" type="range" value="0" min="0" max="100">
    </div>
    <button class="playSmall" id="pauseBtn" onclick="toggleAudio()">▶</button>
  </div>
</div>

<script>
const socket=io();
let GAME_ID="{{ game_id }}";
let ROLE="{{ role }}";
let MINUTES={{ minutes }};

let boardData=null, turn="w", over=false, selected=null, legal=[], dragging=null;
let lastMove=[], checkSquare=null, lastSoundId=0;

const boardEl=document.getElementById("board");
const pieceBase="https://cdn.jsdelivr.net/gh/lichess-org/lila@master/public/piece/cburnett/";

const soundMove=new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-self.mp3");
const soundCapture=new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/capture.mp3");
const soundCheck=new Audio("https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/move-check.mp3");

function defaultAvatar(name){
  const n=encodeURIComponent((name||"P")[0]||"P");
  return `https://ui-avatars.com/api/?name=${n}&background=334155&color=ffffff&size=128`;
}
function getTGProfile(){
  try{
    const u = window.Telegram?.WebApp?.initDataUnsafe?.user;
    if(u){
      return {
        id:String(u.id||Date.now()),
        name:u.first_name || u.username || "Player",
        avatar:u.photo_url || defaultAvatar(u.first_name || u.username || "P")
      };
    }
  }catch(e){}
  return {id:String(Date.now()), name:"Player", avatar:defaultAvatar("Player")};
}
let MY_PROFILE=getTGProfile();

function playChessSound(t){
  let s=t==="check"?soundCheck:t==="capture"?soundCapture:soundMove;
  try{s.currentTime=0;s.play().catch(()=>{})}catch(e){}
}

let musicAudio=new Audio();
let currentSong=null;

function toggleMusic(){
  const p=document.getElementById("musicPanel");
  p.style.display=p.style.display==="block"?"none":"block";
}
musicSearch.addEventListener("keydown",(e)=>{if(e.key==="Enter")searchMusic()});

async function searchMusic(){
  const q=musicSearch.value.trim();
  if(!q)return;
  songList.innerHTML='<div style="color:#94a3b8;padding:10px">جاري البحث...</div>';
  try{
    const r=await fetch(`/music_search?q=${encodeURIComponent(q)}`);
    const data=await r.json();
    renderSongs(data.results||[]);
  }catch(e){
    songList.innerHTML='<div style="color:#f87171;padding:10px">فشل البحث</div>';
  }
}
function renderSongs(list){
  songList.innerHTML="";
  if(!list.length){
    songList.innerHTML='<div style="color:#94a3b8;padding:10px">ماكو نتائج</div>';
    return;
  }
  list.forEach((s)=>{
    const d=document.createElement("div");
    d.className="song";
    d.innerHTML=`<img class="cover" src="${s.cover||defaultAvatar('S')}"><div class="songInfo"><b>${s.title}</b><span>${s.artist||'SoundCloud'}</span></div><button class="playSmall">▶</button>`;
    d.querySelector("button").onclick=()=>playSong(s);
    songList.appendChild(d);
  });
}
async function playSong(s){
  nowCover.src=s.cover||defaultAvatar("S");
  nowTitle.innerText=s.title||"Song";
  nowArtist.innerText="جاري التشغيل...";
  pauseBtn.innerText="⏳";
  try{
    const r=await fetch(`/music_stream?url=${encodeURIComponent(s.url)}`);
    const data=await r.json();
    if(!data.audio)throw new Error("no audio");
    currentSong=s;
    musicAudio.src=data.audio;
    await musicAudio.play();
    nowArtist.innerText=s.artist||"SoundCloud";
    pauseBtn.innerText="⏸";
  }catch(e){
    nowArtist.innerText="تعذر تشغيل الأغنية";
    pauseBtn.innerText="▶";
  }
}
function toggleAudio(){
  if(!currentSong)return;
  if(musicAudio.paused){musicAudio.play();pauseBtn.innerText="⏸"}else{musicAudio.pause();pauseBtn.innerText="▶"}
}
musicAudio.ontimeupdate=()=>{if(musicAudio.duration)progress.value=(musicAudio.currentTime/musicAudio.duration)*100}
progress.oninput=()=>{if(musicAudio.duration)musicAudio.currentTime=(progress.value/100)*musicAudio.duration}

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
  socket.emit("create_game",{game:GAME_ID,time:m,role:"w",profile:MY_PROFILE});
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
  if(selected){socket.emit("move",{game:GAME_ID,from:selected,to:sq,role:ROLE});selected=null;legal=[];return}
  socket.emit("legal",{game:GAME_ID,square:sq,role:ROLE});
}
function startDrag(e,el,sq){
  if(selected&&selected!==sq){socket.emit("move",{game:GAME_ID,from:selected,to:sq,role:ROLE});selected=null;legal=[];return}
  if(over)return;
  if((ROLE==="w"&&turn!=="w")||(ROLE==="b"&&turn!=="b"))return;
  selected=sq;socket.emit("legal",{game:GAME_ID,square:sq,role:ROLE});
  dragging={el,sq};el.style.transition="none";el.setPointerCapture(e.pointerId);
  moveDrag(e);el.onpointermove=moveDrag;el.onpointerup=endDrag;
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
    socket.emit("join_game",{game:GAME_ID,role:ROLE,time:MINUTES,profile:MY_PROFILE});
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

  if(d.sound_id && d.sound_id !== lastSoundId){lastSoundId=d.sound_id;playChessSound(d.sound_type)}

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

def default_avatar(name="Player"):
    safe = urllib.parse.quote((name or "P")[:1])
    return f"https://ui-avatars.com/api/?name={safe}&background=334155&color=ffffff&size=128"

def clean_profile(p, fallback):
    if not isinstance(p, dict):
        p = {}
    name = p.get("name") or fallback
    avatar = p.get("avatar") or default_avatar(name)
    return {"name": str(name)[:40], "avatar": str(avatar)}

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
            "white_avatar":default_avatar("White"),
            "black_avatar":default_avatar("Opponent"),
            "last_move":[],
            "sound_id":0,
            "sound_type":"move"
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
        "bottom_time":int(g["white_time"]),
        "sound_id":g["sound_id"],
        "sound_type":g["sound_type"]
    }, room=game_id)

@app.route("/")
def home():
    game_id=request.args.get("game","new")
    role=request.args.get("role","w")
    minutes=int(request.args.get("time","10"))
    if game_id!="new": get_game(game_id,minutes)
    return render_template_string(HTML,game_id=game_id,role=role,minutes=minutes)

@app.route("/music_search")
def music_search():
    q = request.args.get("q","").strip()
    if not q:
        return jsonify({"results":[]})
    try:
        import yt_dlp
        ydl_opts = {"quiet": True, "skip_download": True, "extract_flat": True, "noplaylist": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"scsearch10:{q}", download=False)
        results=[]
        for e in info.get("entries",[])[:10]:
            title=e.get("title") or "SoundCloud"
            url=e.get("url") or e.get("webpage_url")
            if url and not str(url).startswith("http"):
                url = "https://soundcloud.com/" + str(url)
            results.append({
                "title": title,
                "artist": e.get("uploader") or "SoundCloud",
                "cover": e.get("thumbnail") or default_avatar(title),
                "url": url
            })
        return jsonify({"results":results})
    except Exception as e:
        return jsonify({"results":[],"error":str(e)})

@app.route("/music_stream")
def music_stream():
    url=request.args.get("url","")
    try:
        import yt_dlp
        ydl_opts={"quiet":True,"skip_download":True,"format":"bestaudio/best","noplaylist":True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info=ydl.extract_info(url,download=False)
        audio=info.get("url")
        return jsonify({"audio":audio})
    except Exception as e:
        return jsonify({"audio":None,"error":str(e)})

@socketio.on("create_game")
def create_game(data):
    g=get_game(data["game"],int(data.get("time",10)))
    prof=clean_profile(data.get("profile"),"White")
    g["white_name"]=prof["name"]
    g["white_avatar"]=prof["avatar"]
    join_room(data["game"])
    emit_state(data["game"])

@socketio.on("join_game")
def join_game(data):
    game=data.get("game")
    role=data.get("role","w")
    minutes=int(data.get("time",10))
    g=get_game(game,minutes)
    prof=clean_profile(data.get("profile"), "Black" if role=="b" else "White")
    join_room(game)
    if role=="b":
        g["black_name"]=prof["name"]
        g["black_avatar"]=prof["avatar"]
        g["status"]="playing"
        g["last"]=time.time()
    else:
        g["white_name"]=prof["name"]
        g["white_avatar"]=prof["avatar"]
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
            is_capture=b.is_capture(mv)
            b.push(mv)
            g["last_move"]=[data["from"],data["to"]]
            g["last"]=time.time()
            g["sound_id"]+=1
            g["sound_type"]="check" if b.is_check() else "capture" if is_capture else "move"
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
