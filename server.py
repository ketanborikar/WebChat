import sqlite3
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")

# Create database table for chat messages
def setup_db():
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

setup_db()

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("join")
def handle_join(username):
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, message, timestamp FROM messages WHERE timestamp >= datetime('now', '-30 days')")
    chat_history = cursor.fetchall()
    conn.close()

    # Send chat history to the user
    socketio.emit("chat_history", chat_history)

    socketio.send(f"**{username} joined the chat**")

@socketio.on("message")
def handle_message(data):
    username, msg = data.split(": ", 1)

    # Save message to the database
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, msg))
    conn.commit()
    conn.close()

    socketio.send(data)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
