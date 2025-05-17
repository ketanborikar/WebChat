from flask import Blueprint
from flask_socketio import SocketIO
from models import Message
from config import SessionLocal

chat_bp = Blueprint('chat', __name__)
socketio = SocketIO(cors_allowed_origins="*")

@socketio.on('message')
def handle_message(data):
    session = SessionLocal()
    sender = data['sender']
    receiver = data.get('receiver')
    content = data['content']
    group = data.get('group', None)

    new_message = Message(sender_id=sender, receiver_id=receiver, group=group, content=content)
    session.add(new_message)
    session.commit()

    socketio.emit('message', data)
