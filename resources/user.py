import sqlite3
from flask import request
from flask_restful import Resource, inputs
from werkzeug.security import safe_str_cmp
from models.user import UserModel
from blacklist import BLACKLIST
from schemas.user import UserSchema
from marshmallow import ValidationError
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    get_raw_jwt,
    jwt_required,
)

BLANK_ERROR = '{} cannot be blank.'
DELETED = '{} deleted.'
INVALID_CREDENTIALS = 'Invalid credentials'
LOGGED_OUT = 'Successfully logged out.'
USER_ALREADY_EXISTS = 'The user {} already exists.'
USER_CREATED = 'User {} created successfully.'
USER_NOT_FOUND = 'User not found'
USER_CONFIRMED = '{} was successfully actived.'
USER_ALREADY_CONFIRMED = '{} is already confirmed.'
NOT_CONFIRMED_USER = 'You have not confirmed {} registration'

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user = user_schema.load(request.get_json())

        if UserModel.find_by_username(user.username):
            return {'message': USER_ALREADY_EXISTS.format(user.username)}, 400

        user.save_to_db()

        return {'message': USER_CREATED.format(user.username)}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': USER_NOT_FOUND}, 404
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': USER_NOT_FOUND}, 404
        user.delete_from_db()
        return {'message': DELETED.format(user.username)}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        login_user = user_schema.load(request.get_json())

        user = UserModel.find_by_username(login_user.username)
        if not (user and safe_str_cmp(user.password, login_user.password)):
            return {'message': INVALID_CREDENTIALS}, 403

        if not user.activated:
                return {'message': NOT_CONFIRMED_USER.format(user.username)}, 400

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(user.id)
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }, 200


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()['jti']
        BLACKLIST.add(jti)
        return {'message': LOGGED_OUT}


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200


class UserActivation(Resource):
    @classmethod
    def post(cls):
        id = request.get_json()['id']
        user = UserModel.find_by_id(id)

        if not user:
            return {'message': USER_NOT_FOUND}, 404

        if user.activated:
            return {'message': USER_ALREADY_CONFIRMED.format(user.username)}, 400

        user.activated = True
        user.save_to_db()
        return {'message': USER_CONFIRMED.format(user.username)}, 200
