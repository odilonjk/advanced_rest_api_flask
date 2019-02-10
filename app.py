import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_uploads import configure_uploads, patch_request_class
from flask_migrate import Migrate

load_dotenv(".env", verbose=True)

from blacklist import BLACKLIST
from database import db
from libs.image_helper import IMAGE_SET
from libs.strings import gettext
from ma import ma
from oa import oauth
from marshmallow import ValidationError
from resources.confirmation import Confirmation, ConfirmationByUser
from resources.image import ImageUpload, Image, AvatarUpload, Avatar
from resources.item import Item, ItemList
from resources.github_login import GithubLogin
from resources.store import Store, StoreList
from resources.user import (
    User,
    UserRegister,
    UserLogin,
    UserLogout,
    UserModel,
    TokenRefresh,
)

app = Flask(__name__)
app.config.from_object("default_config")
app.config.from_envvar("APPLICATION_SETTINGS")
app.secret_key = "mysecret"
patch_request_class(app, 5 * 1024 * 1024)  # 5MB max size upload
configure_uploads(app, IMAGE_SET)
db.init_app(app)

api = Api(app)

jwt = JWTManager(app)
migrate = Migrate(app, db)


@app.before_first_request
def create_tables():
    db.create_all()


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
        'description': gettext("security_token_expired"),
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(err):
    return jsonify({
        'description': gettext("secutity_invalid_signature"),
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(err):
    return jsonify({
        'description': gettext("security_request_without_token"),
        'error': 'token_required'
    }), 401


@jwt.needs_fresh_token_loader
def needs_fresh_token_callback():
    return jsonify({
        'description': gettext("security_token_not_fresh"),
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        'description': gettext("security_token_revoked"),
        'error': 'token_revoked'
    }), 401


@app.errorhandler(ValidationError)
def handle_marshmallow_validation(err):
    return jsonify(err.messages), 400


api.add_resource(AvatarUpload, '/avatar')
api.add_resource(Avatar, '/avatar/<int:user_id>')
api.add_resource(Confirmation, '/user_confirmation/<string:confirmation_id>')
api.add_resource(ConfirmationByUser, '/confirmation/user/<int:user_id>')
api.add_resource(GithubLogin, '/login/github')
api.add_resource(Image, '/image/<string:filename>')
api.add_resource(ImageUpload, '/image')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(UserRegister, '/register')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')

if __name__ == '__main__':
    from database import db
    db.init_app(app)
    ma.init_app(app)
    oauth.init_app(app)
    app.run(port=5000)
