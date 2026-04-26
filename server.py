from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Chess</title>
  <style>
    body { margin:0; background:#dbeeff; font-family:Arial; text-align:center; }
    h2 { margin-top:15px; }
    #board { width:360px; height:360px; margin:20px auto; display:grid; grid-template-columns:repeat(8,1fr); border:2px solid #333; }
    .cell { width:45px; height:45px; font-size:28px; display:flex; align-items:center; justify-content:center; }
    .white { background:#f0d9b5; }
    .black { background:#b58863; }
  </style>
</head>
<body>
  <h2>لعبة الشطرنج ♟️</h2>
  <p>الوقت: {{ time }} دقائق</p>
  <div id="board"></div>

  <script>
    const pieces = [
      "♜","♞","♝","♛","♚","♝","♞","♜",
      "♟","♟","♟","♟","♟","♟","♟","♟",
      "","","","","","","","",
      "","","","","","","","",
      "","","","","","","","",
      "","","","","","","","",
      "♙","♙","♙","♙","♙","♙","♙","♙",
      "♖","♘","♗","♕","♔","♗","♘","♖"
    ];

    const board = document.getElementById("board");

    for (let i = 0; i < 64; i++) {
      const cell = document.createElement("div");
      const row = Math.floor(i / 8);
      const col = i % 8;
      cell.className = "cell " + ((row + col) % 2 === 0 ? "white" : "black");
      cell.textContent = pieces[i];
      board.appendChild(cell);
    }
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    time = request.args.get("time", "10")
    return render_template_string(HTML, time=time)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
