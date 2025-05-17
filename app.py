from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import eventlet
import eventlet.wsgi
from auth import auth_bp
from chat import chat_bp, socketio

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = '7e1c7112fe937fe24e8fe1dc84d56299'
app.config['JWT_SECRET_KEY'] = 'c9de8c1fd839edef2260ab6f27f9dd1c'

jwt = JWTManager(app)

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(chat_bp, url_prefix='/chat')

@app.route('/')
def home():
    return render_template("index.html")

socketio.init_app(app, async_mode='eventlet')

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)
