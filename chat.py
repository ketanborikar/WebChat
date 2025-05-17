import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
from flask_jwt_extended import JWTManager, jwt_required, create_access_token
import config

app = Flask(__name__, template_folder="templates")
app.config["JWT_SECRET_KEY"] = "your_secret_key"
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

online_users = set()  # Track online users

@app.route("/")
def home():
    return "Chat service is running!"

@app.route("/chat")
@jwt_required()
def chat_page():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    config.cursor.execute("SELECT id FROM users WHERE username = %s;", (data["username"],))
    user = config.cursor.fetchone()
    if user:
        token = create_access_token(identity=user[0])
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    config.cursor.execute("INSERT INTO users (username) VALUES (%s) RETURNING id;", (data["username"],))
    user_id = config.cursor.fetchone()[0]
    config.conn.commit()
    return jsonify({"message": "User registered", "user_id": user_id})

@socketio.on("join")
def handle_join(data):
    online_users.add(data["username"])
    join_room("group_chat")
    emit("message", {"msg": f"{data['username']} joined the chat"}, room="group_chat")
    emit("online_users", {"users": list(online_users)}, broadcast=True)

@socketio.on("send_message")
def handle_send_message(data):
    emit("message", {"sender": data["sender"], "message": data["message"]}, room="group_chat")

if __name__ == "__main__":
    socketio.run(app, debug=True)
