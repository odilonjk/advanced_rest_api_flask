from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from blacklist import BLACKLIST
from resources.user import (
    User,
    UserRegister,
    UserLogin,
    UserLogout,
    UserModel,
    TokenRefresh,
)
from ma import ma

app = Flask(__name__)

app.secret_key = 'my_secret'
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
app.config['PROPAGATE_EXCEPTIONS'] = True

# SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

api = Api(app)

jwt = JWTManager(app)


@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    user = UserModel.find_by_id(identity)
    return {'is_admin': user.is_admin}


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in BLACKLIST


@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'description': 'The token has expired.',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(err):
    return jsonify({
        'description': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(err):
    return jsonify({
        'description': 'Request does not contain an access token.',
        'error': 'token_required'
    }), 401


@jwt.needs_fresh_token_loader
def needs_fresh_token_callback():
    return jsonify({
        'description': 'The token is not fresh.',
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        'description': 'The token has been revoked.',
        'error': 'token_revoked'
    }), 401


api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(TokenRefresh, '/refresh')

if __name__ == '__main__':
    from database import db
    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True)
