import psycopg2
import os
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")

DATABASE_URL = "postgresql://chat_db_bnpo_user:LEltmJ1OYX1mIRZKHKDCGJPDXsEAnx2x@dpg-d0k64ore5dus73bgbnl0-a/chat_db_bnpo"

# Connect to PostgreSQL
def connect_db():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# Create chat history table
def setup_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            username TEXT,
            message TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT username, message, timestamp FROM messages WHERE timestamp >= NOW() - INTERVAL '30 days'")
    chat_history = cursor.fetchall()
    conn.close()

    # Send chat history to the user
    socketio.emit("chat_history", chat_history)

    socketio.send(f"**{username} joined the chat**")

@socketio.on("message")
def handle_message(data):
    username, msg = data.split(": ", 1)

    # Save message to PostgreSQL
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (username, message) VALUES (%s, %s)", (username, msg))
    conn.commit()
    conn.close()

    socketio.send(data)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
