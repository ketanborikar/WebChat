import psycopg2
import os
from flask import Flask, render_template
from flask_socketio import SocketIO

# Initialize Flask and SocketIO
app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")

# NeonDB Connection String
DATABASE_URL = "postgresql://neondb_owner:npg_VX5T9BpaSOlP@ep-twilight-wave-a1cpdb3q-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

# Connect to NeonDB
def connect_db():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# Setup Database and Chat History Table
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
    
    # Retrieve chat history from the last 30 days
    cursor.execute("SELECT username, message, timestamp FROM messages WHERE timestamp >= NOW() - INTERVAL '30 days'")
    chat_history = cursor.fetchall()
    conn.close()

    # Format timestamps
    formatted_history = [
        (username, message, timestamp.strftime("%Y-%m-%d %H:%M:%S")) for username, message, timestamp in chat_history
    ]

    print("DEBUG: Retrieved Chat History →", formatted_history)  # Debugging log
    socketio.emit("chat_history", formatted_history)
    socketio.send(f"**{username} joined the chat**")

@socketio.on("message")
def handle_message(data):
    username, msg = data.split(": ", 1)

    # Save message to NeonDB
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (username, message) VALUES (%s, %s)", (username, msg))
    conn.commit()
    conn.close()

    print(f"DEBUG: Message saved → {username}: {msg}")  # Debugging log
    socketio.send(data)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
