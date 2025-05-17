from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token
import bcrypt
import config

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "your_secret_key"
jwt = JWTManager(app)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    hashed_pw = bcrypt.hashpw(data["password"].encode(), bcrypt.gensalt())
    config.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id;", (data["username"], hashed_pw))
    user_id = config.cursor.fetchone()[0]
    config.conn.commit()
    return jsonify({"message": "User registered", "user_id": user_id})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    config.cursor.execute("SELECT id, password FROM users WHERE username = %s;", (data["username"],))
    user = config.cursor.fetchone()
    if user and bcrypt.checkpw(data["password"].encode(), user[1].encode()):
        token = create_access_token(identity=user[0])
        return jsonify({"token": token})
    return jsonify({"message": "Invalid credentials"}), 401
