import psycopg2
import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt

app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")
bcrypt = Bcrypt(app)

# Updated NeonDB connection string
DATABASE_URL = "postgresql://neondb_owner:npg_OInDoeA9RTp2@ep-hidden-poetry-a1tlicyt-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

def connect_db():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def setup_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            sender TEXT,
            receiver TEXT,
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()

setup_db()

# Global sets/dicts for tracking online users
online_users = set()
clients = {}  # mapping from socket id to username

@app.route("/")
def index():
    return render_template("index.html")

# --- USER AUTHENTICATION ---
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data["username"]
    password = data["password"]
    hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_pw))
        conn.commit()
    except psycopg2.IntegrityError:
        return jsonify({"message": "Username already exists!"}), 409
    finally:
        conn.close()
    return jsonify({"message": "User registered successfully!"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and bcrypt.check_password_hash(user[0], password):
        return jsonify({"message": "Login successful!"})
    return jsonify({"message": "Invalid credentials"}), 401

# --- SOCKET.IO EVENTS ---

@socketio.on("join")
def handle_join(username):
    from flask import request
    # Save this client's username with its socket id
    clients[request.sid] = username
    online_users.add(username)
    socketio.emit("update_users", list(online_users))  # Update list for all
    socketio.send(f"**{username} joined the chat**")

@socketio.on("disconnect")
def handle_disconnect():
    from flask import request
    sid = request.sid
    username = clients.get(sid)
    if username:
        if username in online_users:
            online_users.remove(username)
        del clients[sid]
        socketio.emit("update_users", list(online_users))  # Update online users list

@socketio.on("message")
def handle_message(data):
    sender, msg = data.split(": ", 1)
    receiver = None
    if msg.startswith("@"):
        parts = msg.split(" ", 1)
        if len(parts) == 2:
            receiver = parts[0][1:]
            msg = parts[1]
    # Save message to DB
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, receiver, message) VALUES (%s, %s, %s)", (sender, receiver, msg))
    conn.commit()
    conn.close()
    if receiver:
        socketio.emit(f"private_{receiver}", f"{sender}: {msg}")
    else:
        socketio.emit("message", f"{sender}: {msg}")

@socketio.on("private_message")
def handle_private_message(data):
    sender = data.get("sender")
    receiver = data.get("receiver")
    message = data.get("message")
    # Optionally include DB storage logic for private messages
    socketio.emit("private_" + receiver, f"{sender}: {message}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}")
    socketio.run(app, host="0.0.0.0", port=port)
