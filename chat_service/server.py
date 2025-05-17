import psycopg2
import os
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, template_folder="templates")
app.secret_key = "6ff4c93c0352662c3fbff580c5aaed77"
socketio = SocketIO(app, cors_allowed_origins="*")

DATABASE_URL = "postgresql://neondb_owner:npg_VX5T9BpaSOlP@ep-twilight-wave-a1cpdb3q-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

def connect_db():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def setup_db():
    conn = connect_db()
    cursor = conn.cursor()

    # Users table for authentication and online status
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            status TEXT DEFAULT 'offline'
        )
    """)

    # Messages table for group and private chat
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            sender TEXT,
            recipient TEXT DEFAULT 'group',
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_status BOOLEAN DEFAULT FALSE
        )
    """)

    # Favorites table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            user_id INT,
            favorite_id INT,
            PRIMARY KEY (user_id, favorite_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (favorite_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

setup_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data["username"]
    password = generate_password_hash(data["password"])

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password))
        conn.commit()
        return jsonify({"status": "success"})
    except:
        return jsonify({"status": "error", "message": "Username already taken"})
    finally:
        conn.close()

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data["username"]
    password = data["password"]

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[0], password):
        session["username"] = username
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Invalid credentials"})

@socketio.on("join")
def handle_join(username):
    session["username"] = username
    conn = connect_db()
    cursor = conn.cursor()

    # Update online status
    cursor.execute("UPDATE users SET status = 'online' WHERE username = %s", (username,))

    # Retrieve chat history
    cursor.execute("SELECT sender, message, timestamp FROM messages WHERE recipient = 'group' ORDER BY timestamp DESC LIMIT 50")
    chat_history = cursor.fetchall()
    
    conn.commit()
    conn.close()

    formatted_history = [(sender, message, timestamp.strftime("%Y-%m-%d %H:%M:%S")) for sender, message, timestamp in chat_history]
    socketio.emit("chat_history", formatted_history)
    socketio.send(f"**{username} joined the chat**")

@socketio.on("message")
def handle_message(data):
    username, msg = data.split(": ", 1)

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, message) VALUES (%s, %s)", (username, msg))
    conn.commit()
    conn.close()

    socketio.send(data)

@socketio.on("private_message")
def handle_private_message(data):
    sender = session.get("username")
    recipient = data["recipient"]
    message = data["message"]

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, recipient, message) VALUES (%s, %s, %s)", (sender, recipient, message))
    conn.commit()
    conn.close()

    socketio.emit(f"private_{recipient}", {"sender": sender, "message": message})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
