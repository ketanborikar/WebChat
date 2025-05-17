import psycopg2
import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt

# Initialize Flask, SocketIO & Bcrypt
app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")
bcrypt = Bcrypt(app)

# Updated NeonDB Connection String ✅
DATABASE_URL = "postgresql://neondb_owner:npg_OInDoeA9RTp2@ep-hidden-poetry-a1tlicyt-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

# Connect to NeonDB
def connect_db():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# Setup Database with Users & Messages Tables
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

# Track online users
online_users = set()

@app.route("/")
def index():
    return render_template("index.html")

# 🔹 **User Signup**
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username, password = data["username"], data["password"]
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

# 🔹 **User Login**
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username, password = data["username"], data["password"]

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user[0], password):
        return jsonify({"message": "Login successful!"})
    return jsonify({"message": "Invalid credentials"}), 401

# 🔹 **Group Chat Join**
@socketio.on("join")
def handle_join(username):
    online_users.add(username)
    socketio.emit("update_users", list(online_users))  # Send user list to all clients
    socketio.send(f"**{username} joined the chat**")

# 🔹 **Handle Disconnects**
@socketio.on("disconnect")
def handle_disconnect():
    global online_users
    for user in online_users.copy():
        online_users.remove(user)
    socketio.emit("update_users", list(online_users))  # Update user list on disconnect

# 🔹 **Handling Messages (Group & Private)**
@socketio.on("message")
def handle_message(data):
    sender, msg = data.split(": ", 1)
    receiver = None

    if msg.startswith("@"):
        parts = msg.split(" ", 1)
        if len(parts) == 2:
            receiver = parts[0][1:]
            msg = parts[1]

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, receiver, message) VALUES (%s, %s, %s)", (sender, receiver, msg))
    conn.commit()
    conn.close()

    if receiver:
        socketio.emit(f"private_{receiver}", f"{sender}: {msg}")
    else:
        socketio.emit("message", f"{sender}: {msg}")  # ✅ FIX: Broadcast to all users

# 🔹 **Fix: Bind to Render’s Assigned PORT & Debug Output**
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ✅ Get Render’s assigned port
    print(f"🔍 Debug: Starting server on port {port}")  # 🔍 Added Debugging Output
    socketio.run(app, host="0.0.0.0", port=port)
