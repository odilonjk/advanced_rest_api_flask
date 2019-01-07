import traceback
from time import time

from flask import make_response, render_template
from flask_restful import Resource

from models.confirmation import ConfirmationModel
from models.user import UserModel
from schemas.confirmation import ConfirmationSchema
from libs.mailgun import MailGunException

CONFIRMATION_NOT_FOUND = 'Confirmation not found.'
CONFIRMATION_EXPIRED = 'Confirmation expired.'
ALREADY_CONFIRMED = 'User already confirmed.'
USER_NOT_FOUND = 'User not found.'
RESEND_SUCCESSFUL = 'Confirmation email sucessfully re-sent.'
RESEND_FAIL = 'Failed to resend confirmation email.'

confirmation_schema = ConfirmationSchema()


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {'message': CONFIRMATION_NOT_FOUND}, 400

        if confirmation.expired:
            return {'message': CONFIRMATION_EXPIRED}, 400

        if confirmation.confirmed:
            return {'message': ALREADY_CONFIRMED}, 400

        confirmation.confirmed = True
        confirmation.save_to_db()

        headers = {'Content-Type': 'text/html'}
        return make_response(
            render_template('confirmation_path.html', email=confirmation.user.email),
            200,
            headers
        )


class ConfirmationByUser(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': USER_NOT_FOUND}, 400

        return {
            'current_time': int(time()),
            'confirmation': [
                confirmation_schema.dump(confirmation)
                for confirmation in user.confirmation.order_by(ConfirmationModel.expire_at)
            ]
        }, 200

    @classmethod
    def post(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': USER_NOT_FOUND}, 400

        try:
            confirmation = user.most_recent_confirmation
            if confirmation:
                if confirmation.confirmed:
                    return {'message': ALREADY_CONFIRMED}, 400
                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save_to_db()
            user.send_confirmation_email()
            return {'message': RESEND_SUCCESSFUL}, 201
        except MailGunException as e:
            return {'nessage': str(e)}, 500
        except:
            traceback.print_exc()
            return {'message': RESEND_FAIL}, 500
