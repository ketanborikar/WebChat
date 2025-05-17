from flask import Flask
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from auth import auth_bp
from chat import chat_bp, socketio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret'

jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(chat_bp, url_prefix='/chat')

if __name__ == '__main__':
    socketio.run(app, debug=True)
