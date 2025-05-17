import eventlet
eventlet.monkey_patch()  # Fix: Apply monkey patching BEFORE other imports

from flask import Flask
from flask_socketio import SocketIO, emit, join_room
import config

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ✅ Fix: Homepage route to prevent 404 errors
@app.route("/")
def home():
    return "Chat service is running!"

@socketio.on("join")
def handle_join(data):
    join_room(data["room"])
    emit("message", {"msg": f"{data['username']} joined the chat"}, room=data["room"])

@socketio.on("send_message")
def handle_send_message(data):
    config.cursor.execute("INSERT INTO messages (sender_id, receiver_id, group_chat, content) VALUES (%s, %s, %s, %s) RETURNING id;",
                          (data["sender_id"], data["receiver_id"], data["group_chat"], data["message"]))
    msg_id = config.cursor.fetchone()[0]
    config.conn.commit()
    emit("message", {"id": msg_id, "sender": data["sender"], "message": data["message"]}, room=data["room"])

if __name__ == "__main__":
    socketio.run(app, debug=True)
