from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, send
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import psycopg2

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
socketio = SocketIO(app, cors_allowed_origins="*")
jwt = JWTManager(app)

# Connect to PostgreSQL (NeonDB)
conn = psycopg2.connect("postgresql://neondb_owner:npg_OInDoeA9RTp2@ep-hidden-poetry-a1tlicyt-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require")
cursor = conn.cursor()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    # Assume username/password validation
    access_token = create_access_token(identity=data["username"])
    return jsonify(access_token=access_token)

@socketio.on('message')
def handle_message(data):
    send(data['message'], room=data['room'])

@socketio.on('join')
def on_join(data):
    join_room(data['room'])
    send(f"{data['username']} joined {data['room']}", room=data['room'])

@socketio.on('leave')
def on_leave(data):
    leave_room(data['room'])
    send(f"{data['username']} left {data['room']}", room=data['room'])

if __name__ == '__main__':
    socketio.run(app)
