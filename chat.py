from flask import Blueprint, jsonify
from flask_socketio import SocketIO
from models import Message, User
from config import SessionLocal

chat_bp = Blueprint('chat', __name__)
socketio = SocketIO(cors_allowed_origins="*")

@socketio.on('message')
def handle_message(data):
    session = SessionLocal()

    # Retrieve sender's user ID
    sender_user = session.query(User).filter_by(username=data['sender']).first()
    if not sender_user:
        return jsonify({"error": "Sender user not found"}), 400

    new_message = Message(
        sender_id=sender_user.id,  # ✅ Store numeric ID instead of username
        receiver_id=data.get('receiver'),
        group=data.get('group'),
        content=data['content']
    )

    session.add(new_message)
    session.commit()

    socketio.emit('message', data)
