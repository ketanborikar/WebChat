import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required, verify_jwt_in_request
import config

app = Flask(__name__, template_folder="templates")
app.config["JWT_SECRET_KEY"] = "your_secret_key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False  # ✅ No expiration for debugging
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")

online_users = set()  # Store online users dynamically

@app.route("/")
def home():
    return "Chat service is running!"

@app.route("/chat")
def chat_page():
    try:
        print(f"Received Headers: {request.headers}")  # ✅ Debugging log: Print headers
        verify_jwt_in_request()  # ✅ Ensure the JWT token is verified before retrieving identity
        current_user = get_jwt_identity()
        print(f"Received JWT identity: {current_user}")  # ✅ Debugging log
        return render_template("index.html", username=current_user)
    except Exception as e:
        print(f"JWT verification failed: {str(e)}")  # ✅ Debugging log
        return jsonify({"message": "Unauthorized access"}), 401

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    config.cursor.execute("SELECT id FROM users WHERE username = %s;", (data["username"],))
    user = config.cursor.fetchone()
    if user:
        token = create_access_token(identity=data["username"])
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
    config.cursor.execute(
        "INSERT INTO messages (sender_id, receiver_id, group_chat, content) VALUES (%s, %s, %s, %s) RETURNING id;",
        (data["sender_id"], data["receiver_id"], data["group_chat"], data["message"])
    )
    msg_id = config.cursor.fetchone()[0]
    config.conn.commit()
    emit("message", {"id": msg_id, "sender": data["sender"], "message": data["message"]}, room=data["room"])

if __name__ == "__main__":
    socketio.run(app, debug=True)
