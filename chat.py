from flask import Blueprint, jsonify
from flask_socketio import SocketIO
from models import Message, User
from config import SessionLocal

chat_bp = Blueprint('chat', __name__)
socketio = SocketIO(cors_allowed_origins="*")

@socketio.on('message')
def handle_message(data):
    session = SessionLocal()

    # Debugging log to confirm message receipt
    print(f"Received WebSocket message: {data}")

    # Fetch sender user ID from the database
    sender_user = session.query(User).filter_by(username=data['sender']).first()
    if not sender_user:
        print("Error: Sender user not found")
        socketio.emit('error', {"error": "Sender user not found"})
        return

    # Store message in database
    new_message = Message(
        sender_id=sender_user.id,
        receiver_id=data.get('receiver'),
        group=data.get('group'),
        content=data['content']
    )

    session.add(new_message)
    session.commit()
    
    print("Message saved successfully!")

    # ✅ Send confirmation response
    socketio.emit('message', data)
    return {"status": "success", "message": "Message stored"}
