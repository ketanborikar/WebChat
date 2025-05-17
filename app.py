from flask import Flask
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import eventlet
import eventlet.wsgi
from auth import auth_bp
from chat import chat_bp, socketio

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret'

jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(chat_bp, url_prefix='/chat')

# Fix: Adding a route for the home page to avoid 404 errors
@app.route('/')
def home():
    return "Chat Server is Running"

# Explicitly using eventlet async mode
socketio.init_app(app, async_mode='eventlet')

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
