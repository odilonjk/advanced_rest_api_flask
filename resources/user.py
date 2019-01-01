import sqlite3
from flask_restful import Resource, reqparse, inputs
from werkzeug.security import safe_str_cmp
from models.user import UserModel
from blacklist import BLACKLIST
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


_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
                          type=str,
                          required=True,
                          help=BLANK_ERROR.format('username'))

_user_parser.add_argument('password',
                          type=str,
                          required=True,
                          help=BLANK_ERROR.format('password'))

_user_parser.add_argument('is_admin',
                          type=inputs.boolean,
                          required=False)


class UserRegister(Resource):
    @classmethod
    def post(cls):
        data = _user_parser.parse_args()
        username = data['username']

        if UserModel.find_by_username(username):
            return {'message': USER_ALREADY_EXISTS.format(username)}, 400

        user = UserModel(**data)
        user.save_to_db()

        return {'message': USER_CREATED.format(username)}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': USER_NOT_FOUND}, 404
        return user.json()

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
        data = _user_parser.parse_args()
        user = UserModel.find_by_username(data['username'])
        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        return {'message': INVALID_CREDENTIALS}


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
