from flask import Blueprint, request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token
from models import User
from config import SessionLocal

auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth_bp.route('/signup', methods=['POST'])
def signup():
    session = SessionLocal()
    data = request.json
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(username=data['username'], password_hash=hashed_pw)
    session.add(user)
    session.commit()
    return jsonify({'message': 'User created'})

@auth_bp.route('/login', methods=['POST'])
def login():
    session = SessionLocal()
    data = request.json
    user = session.query(User).filter_by(username=data['username']).first()
    if user and bcrypt.check_password_hash(user.password_hash, data['password']):
        access_token = create_access_token(identity=user.username)
        return jsonify({'access_token': access_token})
    return jsonify({'message': 'Invalid credentials'}), 401
