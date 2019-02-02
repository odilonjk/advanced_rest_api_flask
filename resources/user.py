import sqlite3
import traceback

from flask import request
from flask_restful import Resource, inputs
from werkzeug.security import safe_str_cmp
from marshmallow import ValidationError
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_refresh_token_required,
    get_raw_jwt,
    jwt_required,
)

from blacklist import BLACKLIST
from libs.mailgun import MailGunException
from libs.strings import gettext
from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.user import UserSchema


user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user = user_schema.load(request.get_json())

        if UserModel.find_by_username(user.username):
            return {'message': gettext("user_already_exists").format(user.username)}, 400

        if UserModel.find_by_email(user.email):
            return {'message': gettext("user_email_exists").format(user.username)}, 400

        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
            return {'message': gettext("user_created").format(user.username)}, 201
        except MailGunException as e:
            user.delete_from_db()
            return {'message': str(e)}, 500
        except:
            traceback.print_exc()
            user.delete_from_db()
            return {'message': gettext("user_error_creating")}, 500


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': gettext("user_not_found")}, 404
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': gettext("user_not_found")}, 404
        user.delete_from_db()
        return {'message': gettext("generic_deleted").format(user.username)}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        login_user = user_schema.load(request.get_json(), partial=('email',))

        user = UserModel.find_by_username(login_user.username)
        if not (user and safe_str_cmp(user.password, login_user.password)):
            return {'message': gettext("security_invalid_credentials")}, 403

        confirmation = user.most_recent_confirmation
        if not confirmation or not confirmation.confirmed:
                return {'message': gettext("user_not_confirmed").format(user.username)}, 400

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
        return {'message': gettext("user_logged_out")}


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
