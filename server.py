import psycopg2
import os
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt

app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")
bcrypt = Bcrypt(app)

DATABASE_URL = "postgresql://neondb_owner:npg_OInDoeA9RTp2@ep-hidden-poetry-a1tlicyt-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

def connect_db():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

@socketio.on("private_message")
def handle_private_message(data):
    sender = data.get("sender")
    receiver = data.get("receiver")
    message = data.get("message")

    print(f"🔍 Server Log: Received private message from {sender} to {receiver}: {message}")  # ✅ Debugging log

    # ✅ Store private messages in the database
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender, receiver, message) VALUES (%s, %s, %s)", (sender, receiver, message))
    conn.commit()
    conn.close()

    socketio.emit(f"private_{receiver}", f"{sender}: {message}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}")
    socketio.run(app, host="0.0.0.0", port=port)
