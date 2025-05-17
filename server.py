from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app, cors_allowed_origins="*")

users = set()  # Track active users

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    print("A user connected")

@socketio.on("disconnect")
def handle_disconnect():
    global users
    socketio.send("A user has left the chat.")

@socketio.on("join")
def handle_join(username):
    users.add(username)
    socketio.send(f"**{username} joined the chat**")

@socketio.on("leave")
def handle_leave(username):
    users.discard(username)
    socketio.send(f"**{username} left the chat**")

@socketio.on("message")
def handle_message(msg):
    print(f"Received: {msg}")
    socketio.send(msg)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
